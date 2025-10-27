"""
Mock AI services untuk testing tanpa AI dependencies
"""
import random
import time
from typing import Dict, List

class MockSpeechToTextService:
    def __init__(self, **kwargs):
        pass
    
    def initialize(self):
        pass
    
    def transcribe_audio(self, audio_path: str) -> List[Dict]:
        return [
            {
                "start": 0.0,
                "end": 5.0,
                "text": "Ini adalah transkrip mock untuk testing",
                "confidence": 0.95
            }
        ]
    
    def transcribe_audio_stream(self, audio_data, sample_rate: int = 16000):
        return "Ini adalah transkrip real-time mock", 0.95
    
    def cleanup(self):
        pass

class MockFacialEmotionService:
    def __init__(self):
        self.emotions = ['happy', 'neutral', 'sad', 'angry', 'surprise']
    
    def initialize(self):
        pass
    
    def detect_emotion(self, frame) -> Dict:
        emotion = random.choice(self.emotions)
        return {
            "dominant_emotion": emotion,
            "confidence": random.uniform(0.7, 0.95),
            "all_emotions": {e: random.uniform(0.1, 0.3) for e in self.emotions},
            "face_detected": True
        }
    
    def calculate_emotion_stability(self, emotion_history: list) -> float:
        if not emotion_history:
            return 0.8
        return random.uniform(0.7, 0.95)
    
    def cleanup(self):
        pass

class MockSpeechEmotionService:
    def predict_emotion(self, audio_path: str) -> Dict:
        emotions = ['calm', 'happy', 'neutral', 'sad', 'angry']
        return {
            "emotion": random.choice(emotions),
            "confidence": random.uniform(0.7, 0.9),
            "energy_level": random.uniform(0.3, 0.7),
            "pitch_variation": random.uniform(0.2, 0.5)
        }
    
    def analyze_speech_clarity(self, audio_path: str) -> float:
        return random.uniform(0.7, 0.95)

class MockNLPAnalyzer:
    def __init__(self):
        pass
    
    def initialize(self):
        pass
    
    def analyze_berakhlak_values(self, text: str) -> Dict[str, float]:
        return {
            "berorientasi_pelayanan": random.uniform(0.5, 0.9),
            "akuntabel": random.uniform(0.5, 0.9),
            "kompeten": random.uniform(0.5, 0.9),
            "harmonis": random.uniform(0.5, 0.9),
            "loyal": random.uniform(0.5, 0.9),
            "adaptif": random.uniform(0.5, 0.9),
            "kolaboratif": random.uniform(0.5, 0.9)
        }
    
    def calculate_coherence(self, text_segments: List[str]) -> float:
        return random.uniform(0.7, 0.95)
    
    def analyze_sentiment(self, text: str) -> float:
        return random.uniform(0.4, 0.8)
    
    def cleanup(self):
        pass

# Replace real services dengan mock
try:
    from .speech_to_text import SpeechToTextService
    from .facial_emotion import FacialEmotionService
    from .speech_emotion import SpeechEmotionService
    from .nlp_analyzer import NLPAnalyzer
except ImportError:
    SpeechToTextService = MockSpeechToTextService
    FacialEmotionService = MockFacialEmotionService
    SpeechEmotionService = MockSpeechEmotionService
    NLPAnalyzer = MockNLPAnalyzer
