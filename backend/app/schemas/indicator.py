"""
Pydantic schemas for indicators and assessments
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Indicator Schemas
class IndicatorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    weight: Decimal = Field(default=1.0, ge=0, le=10)

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorUpdate(IndicatorBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    weight: Optional[Decimal] = Field(None, ge=0, le=10)

class IndicatorResponse(IndicatorBase):
    id: int
    interview_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Assessment Schemas
class AssessmentBase(BaseModel):
    score: Decimal = Field(..., ge=0, le=100)  # AI Score
    manual_score: Optional[Decimal] = Field(None, ge=0, le=100)  # Manual Score
    evidence: Optional[str] = None
    reasoning: Optional[str] = None
    interviewer_notes: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    indicator_id: int

class AssessmentResponse(AssessmentBase):
    id: int
    interview_id: int
    indicator_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Manual Scoring Input
class ManualScoreInput(BaseModel):
    manual_scores: dict[int, Decimal] = Field(..., description="Dict of indicator_id: manual_score")
    interviewer_notes: Optional[str] = None

# Combined responses
class IndicatorWithAssessment(IndicatorResponse):
    assessment: Optional[AssessmentResponse] = None

class InterviewAssessmentSummary(BaseModel):
    indicators: List[IndicatorWithAssessment]
    overall_score: Decimal
    total_indicators: int
    assessed_indicators: int
