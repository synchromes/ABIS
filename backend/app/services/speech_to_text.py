import os
import tempfile
import numpy as np
from faster_whisper import WhisperModel
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self, model_size: str = "base", device: str = "cuda", language: str = "id"):
        self.model_size = model_size
        # Auto-detect CUDA availability
        import torch
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            device = "cpu"
        self.device = device
        self.language = language
        self.model = None
        
    def initialize(self):
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8" if self.device == "cpu" else "float16"
            )
            logger.info("Whisper model loaded successfully")
    
    def transcribe_audio(self, audio_path: str) -> List[Dict]:
        self.initialize()
        
        segments, info = self.model.transcribe(
            audio_path,
            language=self.language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        results = []
        for segment in segments:
            results.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "confidence": segment.avg_logprob
            })
        
        return results
    
    def transcribe_audio_stream(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Tuple[str, float]:
        self.initialize()
        
        if len(audio_data) < sample_rate * 0.5:
            return "", 0.0
        
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            try:
                sf.write(temp_path, audio_data, sample_rate)
            except Exception as e:
                logger.error(f"[STT] Error writing audio file: {e}")
                return "", 0.0
        
        try:
            # Fast transcription with minimal options
            segments, info = self.model.transcribe(
                temp_path,
                language=self.language,
                beam_size=1,  # Reduced from 5 for speed
                vad_filter=True,  # Enable VAD for better accuracy
                condition_on_previous_text=False,  # Faster processing
                temperature=0.0  # Deterministic output
            )
            
            text = ""
            avg_confidence = 0.0
            count = 0
            
            for segment in segments:
                segment_text = segment.text.strip()
                if segment_text:  # Only add non-empty segments
                    text += segment_text + " "
                    avg_confidence += segment.avg_logprob
                    count += 1
            
            if count > 0:
                avg_confidence /= count
                avg_confidence = max(0.0, min(1.0, (avg_confidence + 5) / 5))
            
            result_text = text.strip()
            return result_text, float(avg_confidence)
        except Exception as e:
            logger.error(f"[STT] Error: {e}")
            return "", 0.0
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def cleanup(self):
        if self.model is not None:
            del self.model
            self.model = None
            logger.info("Whisper model cleaned up")
