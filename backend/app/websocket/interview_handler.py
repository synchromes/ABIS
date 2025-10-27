from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
import base64
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from ..services.speech_to_text import SpeechToTextService
    from ..services.facial_emotion import FacialEmotionService
    from ..services.speech_emotion import SpeechEmotionService
    from ..services.nlp_analyzer import NLPAnalyzer
    from ..services.speech_emotion_recognition import get_speech_emotion_recognizer
    AI_AVAILABLE = True
    logger.info("Using REAL AI services - All dependencies loaded")
except ImportError as e:
    logger.error(f"Failed to import AI services: {e}")
    from ..services.mock_services import (
        MockSpeechToTextService as SpeechToTextService,
        MockFacialEmotionService as FacialEmotionService,
        MockSpeechEmotionService as SpeechEmotionService,
        MockNLPAnalyzer as NLPAnalyzer
    )
    # Mock speech emotion recognizer
    class MockSpeechEmotionRecognizer:
        def analyze_audio_chunk(self, audio_data):
            return None
        def get_stability_score(self):
            return 0.5
    def get_speech_emotion_recognizer():
        return MockSpeechEmotionRecognizer()
    AI_AVAILABLE = False
    logger.warning("Using MOCK AI services - AI dependencies not installed")

from ..services.behavioral_scoring import BehavioralScoringEngine
from ..services.audio_recorder import AudioRecorder
from ..core.config import settings

# Import numpy & cv2 only if available
try:
    import numpy as np
    import cv2
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    logger.warning("OpenCV not available - video frame processing disabled")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.interview_states: Dict[int, Dict] = {}
    
    async def connect(self, websocket: WebSocket, interview_id: int):
        await websocket.accept()
        self.active_connections[interview_id] = websocket
        self.interview_states[interview_id] = {
            "emotions": [],
            "emotion_history": [],
            "facial_service": FacialEmotionService(),
            "speech_emotion_recognizer": get_speech_emotion_recognizer(),
            "audio_recorder": AudioRecorder(interview_id),
            "frame_count": 0,
            "audio_chunk_count": 0
        }
        
        # Start audio recording
        if self.interview_states[interview_id]["audio_recorder"].start_recording():
            logger.info(f"[Interview {interview_id}] Audio recording started")
        else:
            logger.error(f"[Interview {interview_id}] Failed to start audio recording")
        logger.info(f"WebSocket connected for interview {interview_id}")
    
    def disconnect(self, interview_id: int, db=None):
        if interview_id in self.active_connections:
            del self.active_connections[interview_id]
        
        if interview_id in self.interview_states:
            state = self.interview_states[interview_id]
            
            # Stop audio recording and save file
            audio_path = None
            if "audio_recorder" in state:
                audio_path = state["audio_recorder"].stop_recording()
                if audio_path:
                    logger.info(f"[Interview {interview_id}] Audio saved to: {audio_path}")
                    
                    # Save audio path to database immediately
                    if db:
                        try:
                            from ..models.interview import Interview, EmotionLog
                            interview = db.query(Interview).filter(Interview.id == interview_id).first()
                            if interview:
                                interview.audio_file_path = audio_path
                                interview.processing_status = "recording"  # Ready for processing
                                db.commit()
                                logger.info(f"[Interview {interview_id}] Audio path saved to database")
                        except Exception as e:
                            logger.error(f"[Interview {interview_id}] Failed to save audio path to DB: {e}")
            
            # Save all collected emotions to database
            if db and "emotions" in state and len(state["emotions"]) > 0:
                try:
                    from ..models.interview import EmotionLog
                    logger.info(f"[Interview {interview_id}] Attempting to save {len(state['emotions'])} emotion records...")
                    
                    # Save emotions with good confidence
                    saved_count = 0
                    for emotion_data in state["emotions"]:
                        facial_conf = float(emotion_data.get("facial_confidence", 0))
                        
                        # Only save if facial confidence > 0.5 (good quality)
                        if facial_conf > 0.5:
                            try:
                                # Convert emotion_scores numpy types to native Python types for JSON serialization
                                emotion_scores = emotion_data.get("emotion_scores")
                                if emotion_scores and isinstance(emotion_scores, dict):
                                    # Convert all numpy.float32 to Python float
                                    emotion_scores = {
                                        k: float(v) if hasattr(v, 'item') else v 
                                        for k, v in emotion_scores.items()
                                    }
                                
                                emotion_log = EmotionLog(
                                    interview_id=interview_id,
                                    timestamp=float(emotion_data.get("timestamp")),
                                    facial_emotion=str(emotion_data.get("facial_emotion")),
                                    facial_confidence=facial_conf,
                                    speech_emotion=emotion_data.get("speech_emotion"),
                                    speech_confidence=float(emotion_data.get("speech_confidence")) if emotion_data.get("speech_confidence") else None,
                                    emotion_scores=emotion_scores
                                )
                                db.add(emotion_log)
                                saved_count += 1
                            except Exception as inner_e:
                                logger.error(f"[Interview {interview_id}] Error adding emotion log: {inner_e}")
                                continue
                    
                    if saved_count > 0:
                        db.commit()
                        logger.info(f"[Interview {interview_id}] ✅ SUCCESS! {saved_count} high-confidence emotion logs saved to database")
                    else:
                        logger.warning(f"[Interview {interview_id}] No emotions met confidence threshold (>0.5)")
                        
                except Exception as e:
                    logger.error(f"[Interview {interview_id}] ❌ FAILED to save emotion logs: {e}")
                    logger.exception(e)  # Full traceback
                    db.rollback()
            else:
                if db:
                    logger.warning(f"[Interview {interview_id}] No emotions to save (collected: {len(state.get('emotions', []))})")
                else:
                    logger.error(f"[Interview {interview_id}] Cannot save emotions - no database session")
            
            # Cleanup services
            if "facial_service" in state:
                state["facial_service"].cleanup()
            
            del self.interview_states[interview_id]
        
        logger.info(f"WebSocket disconnected for interview {interview_id}")
    
    async def send_message(self, interview_id: int, message: dict):
        if interview_id in self.active_connections:
            try:
                # Convert numpy types to native Python types for JSON serialization
                def convert_to_native(obj):
                    if hasattr(obj, 'item'):  # numpy scalar
                        return obj.item()
                    elif isinstance(obj, dict):
                        return {k: convert_to_native(v) for k, v in obj.items()}
                    elif isinstance(obj, (list, tuple)):
                        return [convert_to_native(item) for item in obj]
                    elif hasattr(obj, 'tolist'):  # numpy array
                        return obj.tolist()
                    return obj
                
                clean_message = convert_to_native(message)
                await self.active_connections[interview_id].send_json(clean_message)
            except Exception as e:
                logger.error(f"Error sending message: {e}", exc_info=True)
    
    async def process_video_frame(self, interview_id: int, frame_data: str):
        if interview_id not in self.interview_states:
            logger.warning(f"[Video] Interview {interview_id} not in states")
            return
        
        if not CV_AVAILABLE:
            logger.debug("[Video] OpenCV not available - skipping")
            return
        
        state = self.interview_states[interview_id]
        state["frame_count"] += 1
        
        if state["frame_count"] % settings.VIDEO_FRAME_RATE != 0:
            return
        
        logger.info(f"[Video] Processing frame {state['frame_count']} for interview {interview_id}")
        
        try:
            frame_bytes = base64.b64decode(frame_data.split(',')[1] if ',' in frame_data else frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("[Video] Failed to decode frame")
                return
            
            emotion_result = state["facial_service"].detect_emotion(frame)
            
            logger.info(f"[Video] Emotion detected: {emotion_result.get('dominant_emotion')} (confidence: {emotion_result.get('confidence'):.2f}, face: {emotion_result.get('face_detected')})")
            
            if emotion_result["face_detected"]:
                emotion_data = {
                    "timestamp": datetime.utcnow().timestamp(),
                    "facial_emotion": emotion_result["dominant_emotion"],
                    "facial_confidence": float(emotion_result["confidence"]),
                    "emotion_scores": emotion_result["all_emotions"]
                }
                
                # Store in memory
                state["emotions"].append(emotion_data)
                
                state["emotion_history"].append(emotion_result["dominant_emotion"])
                if len(state["emotion_history"]) > 100:
                    state["emotion_history"].pop(0)
                
                emotion_stability = state["facial_service"].calculate_emotion_stability(
                    state["emotion_history"]
                )
                
                # Log every 10th detection for monitoring
                if len(state["emotions"]) % 10 == 0:
                    logger.info(f"[Interview {interview_id}] Total emotions collected: {len(state['emotions'])}")
                
                logger.info(f"[Video] Sending emotion update: {emotion_result['dominant_emotion']}")
                
                # Convert numpy types to native Python types
                emotion_data = {
                    "emotion": str(emotion_result["dominant_emotion"]),
                    "confidence": float(emotion_result["confidence"]),
                    "stability": float(emotion_stability),
                    "all_emotions": {k: float(v) for k, v in emotion_result["all_emotions"].items()}
                }
                
                await self.send_message(interview_id, {
                    "type": "emotion_update",
                    "data": emotion_data
                })
            else:
                logger.warning("[Video] No face detected in frame")
        except Exception as e:
            logger.error(f"[Video] Error processing video frame: {e}", exc_info=True)
    
    async def process_audio_chunk(self, interview_id: int, audio_data: str):
        """
        Process audio chunk:
        1. Record to file for batch processing
        2. Analyze speech emotion characteristics (intonation, pitch, energy)
        """
        if interview_id not in self.interview_states:
            return
        
        state = self.interview_states[interview_id]
        
        # Get audio recorder
        audio_recorder = state.get("audio_recorder")
        if not audio_recorder:
            return
        
        try:
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
            
            if len(audio_bytes) == 0:
                return
            
            # Convert to numpy array
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Write directly to audio file
            audio_recorder.write_chunk(audio_array)
            
            # Track audio chunk count
            state["audio_chunk_count"] += 1
            
            # Analyze speech emotion every 5 chunks (~1 second)
            if state["audio_chunk_count"] % 5 == 0:
                await self._analyze_speech_emotion(interview_id, audio_bytes)
                
        except Exception as e:
            logger.error(f"[Audio] Error writing audio chunk: {e}")
    
    async def _analyze_speech_emotion(self, interview_id: int, audio_bytes: bytes):
        """
        Analyze speech emotion characteristics from audio
        Detects: intonation, pitch, energy, speaking rate, calmness
        """
        if interview_id not in self.interview_states:
            return
        
        state = self.interview_states[interview_id]
        speech_recognizer = state.get("speech_emotion_recognizer")
        
        if not speech_recognizer:
            return
        
        try:
            # Analyze speech characteristics
            speech_result = speech_recognizer.analyze_audio_chunk(audio_bytes)
            
            if speech_result is None:
                return  # Skip if analysis failed (e.g., too short, silent)
            
            logger.info(f"[Speech] Emotion: {speech_result['speech_emotion']}, "
                       f"Confidence: {speech_result['confidence']:.2f}, "
                       f"Calmness: {speech_result['calmness']:.2f}, "
                       f"Pitch: {speech_result['voice_features']['pitch_hz']:.1f}Hz")
            
            # Store speech emotion with timestamp
            emotion_data = {
                "timestamp": datetime.utcnow().timestamp(),
                "speech_emotion": speech_result["speech_emotion"],
                "speech_confidence": float(speech_result["confidence"]),
                "speech_arousal": float(speech_result["arousal"]),
                "speech_valence": float(speech_result["valence"]),
                "speech_calmness": float(speech_result["calmness"]),
                "pitch_hz": float(speech_result["voice_features"]["pitch_hz"]),
                "energy_level": float(speech_result["voice_features"]["energy_level"]),
                "speaking_rate": float(speech_result["voice_features"]["speaking_rate"])
            }
            
            # Merge with existing facial emotion if within 2 seconds
            if "emotions" in state and len(state["emotions"]) > 0:
                last_emotion = state["emotions"][-1]
                time_diff = emotion_data["timestamp"] - last_emotion.get("timestamp", 0)
                
                if time_diff < 2.0:
                    # Same time window, merge with facial emotion
                    last_emotion.update(emotion_data)
                    logger.info(f"[Speech] Merged with facial emotion")
                else:
                    # Different time, new entry
                    state["emotions"].append(emotion_data)
            else:
                # First emotion, initialize list
                if "emotions" not in state:
                    state["emotions"] = []
                state["emotions"].append(emotion_data)
                    
        except Exception as e:
            logger.error(f"[Speech] Error analyzing speech emotion: {e}")
    
    async def get_current_analysis(self, interview_id: int) -> Dict:
        """
        Get current analysis during interview.
        Note: Real-time transcription removed - now using batch processing.
        This returns basic emotion data only during interview.
        """
        if interview_id not in self.interview_states:
            return {}
        
        state = self.interview_states[interview_id]
        
        # Calculate emotion stability from collected emotions
        emotion_stability = 0.8
        if len(state.get("emotion_history", [])) > 0:
            emotion_stability = state["facial_service"].calculate_emotion_stability(
                state["emotion_history"]
            )
        
        # Return simple analysis with just emotion data
        # Full analysis happens in batch processing after interview
        return {
            "emotion_stability": emotion_stability,
            "total_emotions": len(state.get("emotions", [])),
            "status": "recording"
        }

manager = ConnectionManager()
