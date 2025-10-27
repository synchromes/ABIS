import librosa
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class SpeechEmotionService:
    def __init__(self):
        self.sample_rate = 16000
        self.emotion_map = {
            0: "neutral",
            1: "calm",
            2: "happy",
            3: "sad",
            4: "angry",
            5: "fearful",
            6: "disgust",
            7: "surprised"
        }
    
    def extract_features(self, audio_path: str) -> np.ndarray:
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate, duration=3.0)
            
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            mfccs_mean = np.mean(mfccs, axis=1)
            
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            
            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_mean = np.mean(mel, axis=1)
            
            zcr = librosa.feature.zero_crossing_rate(y)
            zcr_mean = np.mean(zcr)
            
            rms = librosa.feature.rms(y=y)
            rms_mean = np.mean(rms)
            
            features = np.concatenate([
                mfccs_mean,
                chroma_mean,
                [zcr_mean, rms_mean]
            ])
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return np.zeros(54)
    
    def predict_emotion(self, audio_path: str) -> Dict:
        features = self.extract_features(audio_path)
        
        energy = np.mean(features[-10:])
        pitch_var = np.std(features[:40])
        
        if energy < 0.01:
            emotion = "calm"
            confidence = 0.7
        elif energy > 0.5 and pitch_var > 0.3:
            emotion = "angry"
            confidence = 0.65
        elif pitch_var > 0.4:
            emotion = "happy"
            confidence = 0.6
        elif energy < 0.02 and pitch_var < 0.2:
            emotion = "sad"
            confidence = 0.55
        else:
            emotion = "neutral"
            confidence = 0.8
        
        return {
            "emotion": emotion,
            "confidence": confidence,
            "energy_level": float(energy),
            "pitch_variation": float(pitch_var)
        }
    
    def analyze_speech_clarity(self, audio_path: str) -> float:
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            rms = librosa.feature.rms(y=y)[0]
            snr = np.mean(rms) / (np.std(rms) + 1e-6)
            
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            zcr_stability = 1.0 - np.std(zcr)
            
            clarity = (min(snr / 10.0, 1.0) + zcr_stability) / 2.0
            return max(0.0, min(1.0, clarity))
        except Exception as e:
            logger.error(f"Error analyzing clarity: {e}")
            return 0.5
