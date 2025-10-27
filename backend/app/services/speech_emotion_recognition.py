"""
Speech Emotion Recognition Service
Analyzes voice characteristics: intonation, pitch, energy, speaking rate
"""

import numpy as np
import logging
from typing import Dict, Optional
import io
import base64

logger = logging.getLogger(__name__)

# Try import audio processing libraries
try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
    logger.info("Speech emotion recognition libraries loaded successfully")
except ImportError as e:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning(f"Audio processing libraries not available: {e}")

class SpeechEmotionRecognizer:
    """
    Analyzes speech characteristics to detect emotional state from voice
    
    Features analyzed:
    - Pitch (fundamental frequency) - indicates excitement/stress
    - Energy/Intensity - indicates confidence/assertiveness  
    - Speaking Rate - indicates calmness/nervousness
    - Pitch Variation - indicates emotional stability
    - Voice Quality - indicates vocal tension
    """
    
    def __init__(self):
        self.sample_rate = 16000  # Standard for speech
        self.pitch_history = []  # For stability analysis
        self.energy_history = []
        self.max_history = 20  # Keep last 20 samples
        
    def analyze_audio_chunk(self, audio_data: bytes) -> Optional[Dict]:
        """
        Analyze audio chunk for speech emotion characteristics
        
        Args:
            audio_data: Raw audio bytes (PCM 16-bit)
            
        Returns:
            Dict with emotion characteristics or None if analysis fails
        """
        if not AUDIO_LIBS_AVAILABLE:
            return self._mock_analysis()
            
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            audio_array = audio_array / 32768.0  # Normalize to [-1, 1]
            
            # Skip if too short or silent
            if len(audio_array) < 1600:  # At least 0.1 seconds
                return None
                
            # Extract features
            features = self._extract_features(audio_array)
            
            if features is None:
                return None
            
            # Classify emotion state
            emotion_state = self._classify_emotion(features)
            
            # Update history for stability analysis
            self._update_history(features)
            
            return emotion_state
            
        except Exception as e:
            logger.error(f"Error analyzing audio chunk: {e}")
            return None
    
    def _extract_features(self, audio: np.ndarray) -> Optional[Dict]:
        """Extract acoustic features from audio"""
        try:
            # 1. Pitch (F0) - fundamental frequency
            pitches, magnitudes = librosa.piptrack(
                y=audio,
                sr=self.sample_rate,
                fmin=80,   # Male voice lower bound
                fmax=400   # Female voice upper bound
            )
            
            # Get dominant pitch
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:  # Valid pitch
                    pitch_values.append(pitch)
            
            if len(pitch_values) == 0:
                return None
                
            mean_pitch = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
            
            # 2. Energy/Intensity
            rms_energy = librosa.feature.rms(y=audio)[0]
            mean_energy = np.mean(rms_energy)
            energy_std = np.std(rms_energy)
            
            # 3. Zero Crossing Rate (indicates voice quality/tension)
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            mean_zcr = np.mean(zcr)
            
            # 4. Spectral features (voice quality)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
            mean_spectral = np.mean(spectral_centroid)
            
            # 5. Speaking rate (tempo)
            onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]
            
            return {
                'mean_pitch': float(mean_pitch),
                'pitch_std': float(pitch_std),
                'mean_energy': float(mean_energy),
                'energy_std': float(energy_std),
                'mean_zcr': float(mean_zcr),
                'mean_spectral': float(mean_spectral),
                'tempo': float(tempo)
            }
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def _classify_emotion(self, features: Dict) -> Dict:
        """
        Classify emotional state based on acoustic features
        
        Emotion indicators:
        - Calm: Low pitch variation, moderate energy, steady tempo
        - Confident: Moderate-high energy, steady pitch, clear voice
        - Nervous: High pitch, high pitch variation, variable energy
        - Excited: High pitch, high energy, fast tempo
        - Tired/Sad: Low energy, low pitch, slow tempo
        """
        
        pitch = features['mean_pitch']
        pitch_var = features['pitch_std']
        energy = features['mean_energy']
        energy_var = features['energy_std']
        tempo = features['tempo']
        
        # Normalize values (rough thresholds based on speech research)
        pitch_norm = (pitch - 150) / 100  # Normalize around 150Hz
        pitch_var_norm = pitch_var / 30
        energy_norm = energy / 0.05
        tempo_norm = (tempo - 120) / 30  # Normalize around 120 BPM
        
        # Calculate emotion dimensions
        
        # 1. Arousal (high = excited/nervous, low = calm/tired)
        arousal = (
            0.4 * pitch_norm +
            0.3 * energy_norm +
            0.3 * tempo_norm
        )
        arousal = np.clip(arousal, -1, 1)
        
        # 2. Valence (positive = happy/confident, negative = sad/stressed)
        # Stable pitch + moderate energy = positive
        # High variation + extreme values = negative
        stability = 1.0 - min(pitch_var_norm, 1.0)
        valence = (
            0.5 * stability +
            0.3 * min(energy_norm, 1.0) -
            0.2 * abs(pitch_norm)
        )
        valence = np.clip(valence, -1, 1)
        
        # 3. Confidence (high = assertive, low = hesitant)
        confidence = (
            0.5 * min(energy_norm, 1.0) +
            0.3 * stability +
            0.2 * (1.0 - abs(tempo_norm))
        )
        confidence = np.clip(confidence, 0, 1)
        
        # 4. Calmness (inverse of arousal + stability)
        calmness = (
            0.6 * (1.0 - abs(arousal)) +
            0.4 * stability
        )
        calmness = np.clip(calmness, 0, 1)
        
        # Determine primary emotion label
        if arousal > 0.3 and valence > 0.2:
            emotion = "confident"
        elif arousal > 0.5 and valence < 0:
            emotion = "nervous"
        elif arousal > 0.5 and valence > 0:
            emotion = "excited"
        elif arousal < -0.3:
            if valence > 0:
                emotion = "calm"
            else:
                emotion = "tired"
        elif abs(arousal) < 0.3 and abs(valence) < 0.3:
            emotion = "neutral"
        else:
            emotion = "neutral"
        
        return {
            'speech_emotion': emotion,
            'arousal': float(arousal),  # -1 (calm) to 1 (excited)
            'valence': float(valence),  # -1 (negative) to 1 (positive)
            'confidence': float(confidence),  # 0 to 1
            'calmness': float(calmness),  # 0 to 1
            'voice_features': {
                'pitch_hz': float(pitch),
                'pitch_variation': float(pitch_var),
                'energy_level': float(energy),
                'speaking_rate': float(tempo)
            }
        }
    
    def _update_history(self, features: Dict):
        """Update feature history for trend analysis"""
        self.pitch_history.append(features['mean_pitch'])
        self.energy_history.append(features['mean_energy'])
        
        # Keep only recent history
        if len(self.pitch_history) > self.max_history:
            self.pitch_history.pop(0)
        if len(self.energy_history) > self.max_history:
            self.energy_history.pop(0)
    
    def get_stability_score(self) -> float:
        """
        Calculate overall emotional stability from voice history
        
        Returns:
            Float 0-1 where 1 = very stable, 0 = highly variable
        """
        if len(self.pitch_history) < 5:
            return 0.5  # Neutral if not enough data
        
        # Calculate coefficient of variation (lower = more stable)
        pitch_cv = np.std(self.pitch_history) / (np.mean(self.pitch_history) + 1e-6)
        energy_cv = np.std(self.energy_history) / (np.mean(self.energy_history) + 1e-6)
        
        # Convert to stability score (inverse of variation)
        pitch_stability = 1.0 / (1.0 + pitch_cv * 5)  # Scale factor
        energy_stability = 1.0 / (1.0 + energy_cv * 3)
        
        # Combined stability
        overall_stability = 0.6 * pitch_stability + 0.4 * energy_stability
        
        return float(np.clip(overall_stability, 0, 1))
    
    def _mock_analysis(self) -> Dict:
        """Mock analysis when libraries not available"""
        logger.warning("Using mock speech emotion analysis (libraries not installed)")
        return {
            'speech_emotion': 'neutral',
            'arousal': 0.0,
            'valence': 0.0,
            'confidence': 0.5,
            'calmness': 0.5,
            'voice_features': {
                'pitch_hz': 150.0,
                'pitch_variation': 20.0,
                'energy_level': 0.05,
                'speaking_rate': 120.0
            }
        }

# Singleton instance
_recognizer_instance = None

def get_speech_emotion_recognizer() -> SpeechEmotionRecognizer:
    """Get singleton instance of speech emotion recognizer"""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = SpeechEmotionRecognizer()
    return _recognizer_instance
