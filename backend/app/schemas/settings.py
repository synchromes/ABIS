"""
Pydantic schemas for application settings
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SettingBase(BaseModel):
    setting_key: str = Field(..., min_length=1, max_length=100)
    setting_value: str
    description: Optional[str] = None

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    setting_value: str
    description: Optional[str] = None

class SettingResponse(SettingBase):
    id: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ScoringWeightsUpdate(BaseModel):
    ai_weight: int = Field(..., ge=0, le=100, description="Persentase bobot AI (0-100)")
    manual_weight: int = Field(..., ge=0, le=100, description="Persentase bobot manual (0-100)")
    
    def validate_sum(self):
        """Ensure weights sum to 100"""
        if self.ai_weight + self.manual_weight != 100:
            raise ValueError("AI weight + Manual weight must equal 100%")
        return True

class ScoringWeightsResponse(BaseModel):
    ai_weight: int
    manual_weight: int
