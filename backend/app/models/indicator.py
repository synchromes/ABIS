"""
Models for interview indicators and assessments
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class InterviewIndicator(Base):
    __tablename__ = "interview_indicators"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    weight = Column(DECIMAL(5, 2), default=1.0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    interview = relationship("Interview", back_populates="indicators")
    assessments = relationship("InterviewAssessment", back_populates="indicator", cascade="all, delete-orphan")

class InterviewAssessment(Base):
    __tablename__ = "interview_assessments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("interview_indicators.id", ondelete="CASCADE"), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=False)  # AI Score
    manual_score = Column(DECIMAL(5, 2), nullable=True)  # Manual Score from Interviewer
    evidence = Column(Text)
    reasoning = Column(Text)
    interviewer_notes = Column(Text)  # Notes from manual scoring
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    interview = relationship("Interview", back_populates="assessments")
    indicator = relationship("InterviewIndicator", back_populates="assessments")
