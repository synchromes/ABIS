"""
API endpoints for application settings (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..models.settings import AppSetting
from ..schemas.settings import (
    SettingResponse, SettingUpdate, ScoringWeightsUpdate, ScoringWeightsResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/scoring-weights", response_model=ScoringWeightsResponse)
def get_scoring_weights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current scoring weights configuration
    Available to all authenticated users
    """
    ai_weight = db.query(AppSetting).filter(
        AppSetting.setting_key == "ai_score_weight"
    ).first()
    
    manual_weight = db.query(AppSetting).filter(
        AppSetting.setting_key == "manual_score_weight"
    ).first()
    
    if not ai_weight or not manual_weight:
        # Return defaults if not found
        return ScoringWeightsResponse(ai_weight=60, manual_weight=40)
    
    return ScoringWeightsResponse(
        ai_weight=int(ai_weight.setting_value),
        manual_weight=int(manual_weight.setting_value)
    )


@router.put("/scoring-weights", response_model=ScoringWeightsResponse)
def update_scoring_weights(
    weights: ScoringWeightsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update scoring weights configuration (Admin only)
    Weights must sum to 100%
    """
    # Validate weights sum to 100
    try:
        weights.validate_sum()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Update AI weight
    ai_setting = db.query(AppSetting).filter(
        AppSetting.setting_key == "ai_score_weight"
    ).first()
    
    if ai_setting:
        ai_setting.setting_value = str(weights.ai_weight)
        ai_setting.updated_by = current_user.id
    else:
        # Create if not exists
        ai_setting = AppSetting(
            setting_key="ai_score_weight",
            setting_value=str(weights.ai_weight),
            description="Persentase bobot penilaian AI (0-100)",
            updated_by=current_user.id
        )
        db.add(ai_setting)
    
    # Update Manual weight
    manual_setting = db.query(AppSetting).filter(
        AppSetting.setting_key == "manual_score_weight"
    ).first()
    
    if manual_setting:
        manual_setting.setting_value = str(weights.manual_weight)
        manual_setting.updated_by = current_user.id
    else:
        # Create if not exists
        manual_setting = AppSetting(
            setting_key="manual_score_weight",
            setting_value=str(weights.manual_weight),
            description="Persentase bobot penilaian manual (0-100)",
            updated_by=current_user.id
        )
        db.add(manual_setting)
    
    db.commit()
    db.refresh(ai_setting)
    db.refresh(manual_setting)
    
    logger.info(f"Admin {current_user.email} updated scoring weights: AI={weights.ai_weight}%, Manual={weights.manual_weight}%")
    
    return ScoringWeightsResponse(
        ai_weight=weights.ai_weight,
        manual_weight=weights.manual_weight
    )


@router.get("/all", response_model=List[SettingResponse])
def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all application settings (Admin only)
    """
    settings = db.query(AppSetting).all()
    return settings


@router.put("/{setting_key}", response_model=SettingResponse)
def update_setting(
    setting_key: str,
    setting_data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a specific setting (Admin only)
    """
    setting = db.query(AppSetting).filter(
        AppSetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.setting_value = setting_data.setting_value
    if setting_data.description:
        setting.description = setting_data.description
    setting.updated_by = current_user.id
    
    db.commit()
    db.refresh(setting)
    
    logger.info(f"Admin {current_user.email} updated setting: {setting_key} = {setting_data.setting_value}")
    
    return setting
