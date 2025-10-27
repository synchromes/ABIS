"""
Audio Recording Service for Interview Sessions
Records continuous audio stream to WAV file
"""
import wave
import numpy as np
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self, interview_id: int, sample_rate: int = 16000, channels: int = 1):
        self.interview_id = interview_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_file = None
        self.wav_file = None
        self.audio_buffer = []
        self.is_recording = False
        
        # Create recordings directory if not exists
        self.recordings_dir = Path("./storage/recordings")
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_path = self.recordings_dir / f"interview_{interview_id}_{timestamp}.wav"
        
        logger.info(f"[AudioRecorder] Initialized for interview {interview_id}")
        logger.info(f"[AudioRecorder] Will save to: {self.file_path}")
    
    def start_recording(self):
        """Start recording - open WAV file for writing"""
        try:
            self.wav_file = wave.open(str(self.file_path), 'wb')
            self.wav_file.setnchannels(self.channels)
            self.wav_file.setsampwidth(2)  # 16-bit audio
            self.wav_file.setframerate(self.sample_rate)
            self.is_recording = True
            
            logger.info(f"[AudioRecorder] Recording started: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"[AudioRecorder] Failed to start recording: {e}")
            return False
    
    def write_chunk(self, audio_data: np.ndarray):
        """Write audio chunk to file"""
        if not self.is_recording or self.wav_file is None:
            return False
        
        try:
            # Convert float32 [-1, 1] to int16 [-32768, 32767]
            if audio_data.dtype == np.float32:
                audio_int16 = (audio_data * 32767).astype(np.int16)
            else:
                audio_int16 = audio_data.astype(np.int16)
            
            # Write to file
            self.wav_file.writeframes(audio_int16.tobytes())
            return True
        except Exception as e:
            logger.error(f"[AudioRecorder] Error writing chunk: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording and close file"""
        if self.wav_file:
            try:
                self.wav_file.close()
                self.is_recording = False
                
                # Verify file was created
                if self.file_path.exists():
                    file_size = self.file_path.stat().st_size
                    duration = self.get_audio_duration()
                    logger.info(f"[AudioRecorder] Recording stopped")
                    logger.info(f"[AudioRecorder] File: {self.file_path}")
                    logger.info(f"[AudioRecorder] Size: {file_size} bytes")
                    logger.info(f"[AudioRecorder] Duration: {duration:.2f} seconds")
                    return str(self.file_path)
                else:
                    logger.error(f"[AudioRecorder] File not created: {self.file_path}")
                    return None
            except Exception as e:
                logger.error(f"[AudioRecorder] Error stopping recording: {e}")
                return None
        return None
    
    def get_audio_duration(self):
        """Get duration of recorded audio"""
        try:
            with wave.open(str(self.file_path), 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.error(f"[AudioRecorder] Error getting duration: {e}")
            return 0.0
    
    def get_file_path(self):
        """Get the audio file path"""
        return str(self.file_path) if self.file_path.exists() else None
    
    def cleanup(self):
        """Cleanup resources"""
        if self.is_recording:
            self.stop_recording()
        self.audio_buffer = []
