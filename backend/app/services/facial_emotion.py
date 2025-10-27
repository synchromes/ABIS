import cv2
import numpy as np
from deepface import DeepFace
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FacialEmotionService:
    def __init__(self):
        self.detector = None
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def initialize(self):
        if self.detector is None:
            logger.info("Loading DeepFace emotion detector")
            self.detector = True
            logger.info("DeepFace emotion detector loaded successfully")
    
    def detect_emotion(self, frame: np.ndarray) -> Dict:
        self.initialize()
        
        if frame is None or frame.size == 0:
            return self._empty_result()
        
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
            
            if isinstance(result, list):
                result = result[0]
            
            emotion_scores = result['emotion']
            dominant_emotion = result['dominant_emotion']
            confidence = emotion_scores[dominant_emotion] / 100.0
            
            normalized_scores = {k: v / 100.0 for k, v in emotion_scores.items()}
            
            return {
                "dominant_emotion": dominant_emotion,
                "confidence": confidence,
                "all_emotions": normalized_scores,
                "face_detected": True
            }
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return self._empty_result()
    
    def detect_emotion_from_path(self, image_path: str) -> Dict:
        frame = cv2.imread(image_path)
        if frame is None:
            return self._empty_result()
        return self.detect_emotion(frame)
    
    def calculate_emotion_stability(self, emotion_history: list) -> float:
        if not emotion_history or len(emotion_history) < 2:
            return 1.0
        
        changes = 0
        for i in range(1, len(emotion_history)):
            if emotion_history[i] != emotion_history[i-1]:
                changes += 1
        
        stability = 1.0 - (changes / len(emotion_history))
        return max(0.0, min(1.0, stability))
    
    def _empty_result(self) -> Dict:
        return {
            "dominant_emotion": "neutral",
            "confidence": 0.0,
            "all_emotions": {label: 0.0 for label in self.emotion_labels},
            "face_detected": False
        }
    
    def cleanup(self):
        if self.detector is not None:
            self.detector = None
            logger.info("DeepFace detector cleaned up")
