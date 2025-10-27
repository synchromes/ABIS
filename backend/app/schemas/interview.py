from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

class InterviewBase(BaseModel):
    candidate_name: str
    candidate_email: Optional[EmailStr] = None
    candidate_id_number: Optional[str] = None
    position: str
    scheduled_at: Optional[datetime] = None

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    candidate_name: Optional[str] = None
    candidate_email: Optional[EmailStr] = None
    position: Optional[str] = None
    status: Optional[str] = None  # Changed from Enum to str
    recommendation: Optional[str] = None  # Changed from Enum to str
    scheduled_at: Optional[datetime] = None

class InterviewScoreInput(BaseModel):
    berorientasi_pelayanan_manual: Optional[float] = None
    akuntabel_manual: Optional[float] = None
    kompeten_manual: Optional[float] = None
    harmonis_manual: Optional[float] = None
    loyal_manual: Optional[float] = None
    adaptif_manual: Optional[float] = None
    kolaboratif_manual: Optional[float] = None
    interviewer_notes: Optional[str] = None

class InterviewScoreResponse(BaseModel):
    id: int
    interview_id: int
    berorientasi_pelayanan_ai: Optional[float]
    berorientasi_pelayanan_manual: Optional[float]
    akuntabel_ai: Optional[float]
    akuntabel_manual: Optional[float]
    kompeten_ai: Optional[float]
    kompeten_manual: Optional[float]
    harmonis_ai: Optional[float]
    harmonis_manual: Optional[float]
    loyal_ai: Optional[float]
    loyal_manual: Optional[float]
    adaptif_ai: Optional[float]
    adaptif_manual: Optional[float]
    kolaboratif_ai: Optional[float]
    kolaboratif_manual: Optional[float]
    emotion_stability: Optional[float]
    speech_clarity: Optional[float]
    answer_coherence: Optional[float]
    overall_ai_score: Optional[float]
    overall_manual_score: Optional[float]
    final_score: Optional[float]
    
    class Config:
        from_attributes = True

class TranscriptEntryResponse(BaseModel):
    id: int
    speaker: str
    text: str
    timestamp: float
    emotion_detected: Optional[str]
    sentiment_score: Optional[float]
    
    class Config:
        from_attributes = True

class EmotionLogResponse(BaseModel):
    timestamp: float
    facial_emotion: Optional[str]
    facial_confidence: Optional[float]
    speech_emotion: Optional[str]
    speech_confidence: Optional[float]
    emotion_scores: Optional[Dict]
    
    class Config:
        from_attributes = True

class InterviewResponse(InterviewBase):
    id: int
    status: str  # Changed from Enum to str
    recommendation: Optional[str]  # Changed from Enum to str
    interviewer_id: int
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    
    # New fields for batch processing
    audio_file_path: Optional[str] = None
    processing_status: Optional[str] = None
    processed_at: Optional[datetime] = None
    transcript: Optional[str] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class InterviewDetailResponse(InterviewResponse):
    video_file_path: Optional[str] = None
    transcript_file_path: Optional[str] = None
    report_file_path: Optional[str] = None
    indicators_config: Optional[dict] = None
    
    scores: Optional[InterviewScoreResponse] = None
    transcript_entries: List[TranscriptEntryResponse] = []
    emotion_logs: List[EmotionLogResponse] = []
    
    class Config:
        from_attributes = True

class RealTimeIndicator(BaseModel):
    timestamp: float
    emotion_score: float
    clarity_score: float
    coherence_score: float
    current_emotion: str
    berakhlak_scores: Dict[str, float]

class WebSocketMessage(BaseModel):
    type: str
    data: Dict
