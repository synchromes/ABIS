from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class InterviewStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RecommendationStatus(str, enum.Enum):
    LAYAK = "layak"
    DIPERTIMBANGKAN = "dipertimbangkan"
    TIDAK_LAYAK = "tidak_layak"

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(100), nullable=False)
    candidate_email = Column(String(100), nullable=True)
    candidate_id_number = Column(String(50), nullable=True)
    position = Column(String(100), nullable=False)
    
    status = Column(String(20), default="scheduled", nullable=False)  # Changed from Enum to String
    recommendation = Column(String(20), nullable=True)  # Changed from Enum to String
    
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    video_file_path = Column(String(255), nullable=True)
    audio_file_path = Column(String(512), nullable=True)  # Updated to match migration
    transcript_file_path = Column(String(255), nullable=True)
    report_file_path = Column(String(255), nullable=True)
    
    # New columns for custom indicators system
    transcript = Column(Text, nullable=True)  # Full transcript text
    processing_status = Column(String(20), default="recording", nullable=False)  # recording|processing|completed|failed
    processed_at = Column(DateTime, nullable=True)
    indicators_config = Column(JSON, nullable=True)  # JSON config for custom indicators
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # interviewer = relationship("User", back_populates="interviews")  # Commented to avoid circular import
    scores = relationship("InterviewScore", back_populates="interview", uselist=False)
    transcript_entries = relationship("TranscriptEntry", back_populates="interview", cascade="all, delete-orphan")
    emotion_logs = relationship("EmotionLog", back_populates="interview", cascade="all, delete-orphan")
    
    # New relationships for custom indicators
    indicators = relationship("InterviewIndicator", back_populates="interview", cascade="all, delete-orphan")
    assessments = relationship("InterviewAssessment", back_populates="interview", cascade="all, delete-orphan")

class InterviewScore(Base):
    __tablename__ = "interview_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True, nullable=False)
    
    berorientasi_pelayanan_ai = Column(Float, nullable=True)
    berorientasi_pelayanan_manual = Column(Float, nullable=True)
    
    akuntabel_ai = Column(Float, nullable=True)
    akuntabel_manual = Column(Float, nullable=True)
    
    kompeten_ai = Column(Float, nullable=True)
    kompeten_manual = Column(Float, nullable=True)
    
    harmonis_ai = Column(Float, nullable=True)
    harmonis_manual = Column(Float, nullable=True)
    
    loyal_ai = Column(Float, nullable=True)
    loyal_manual = Column(Float, nullable=True)
    
    adaptif_ai = Column(Float, nullable=True)
    adaptif_manual = Column(Float, nullable=True)
    
    kolaboratif_ai = Column(Float, nullable=True)
    kolaboratif_manual = Column(Float, nullable=True)
    
    emotion_stability = Column(Float, nullable=True)
    speech_clarity = Column(Float, nullable=True)
    answer_coherence = Column(Float, nullable=True)
    
    overall_ai_score = Column(Float, nullable=True)
    overall_manual_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    
    ai_analysis_summary = Column(Text, nullable=True)
    interviewer_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    interview = relationship("Interview", back_populates="scores")

class TranscriptEntry(Base):
    __tablename__ = "transcript_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    
    speaker = Column(String(20), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    
    emotion_detected = Column(String(50), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    interview = relationship("Interview", back_populates="transcript_entries")

class EmotionLog(Base):
    __tablename__ = "emotion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    
    timestamp = Column(Float, nullable=False)
    
    facial_emotion = Column(String(50), nullable=True)
    facial_confidence = Column(Float, nullable=True)
    
    speech_emotion = Column(String(50), nullable=True)
    speech_confidence = Column(Float, nullable=True)
    
    emotion_scores = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    interview = relationship("Interview", back_populates="emotion_logs")
