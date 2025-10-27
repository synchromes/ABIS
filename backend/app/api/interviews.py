from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..models.interview import Interview, InterviewScore, InterviewStatus, RecommendationStatus
from ..models.indicator import InterviewIndicator, InterviewAssessment
from ..schemas.interview import (
    InterviewCreate, InterviewUpdate, InterviewResponse, 
    InterviewDetailResponse, InterviewScoreInput, InterviewScoreResponse
)
from ..schemas.indicator import (
    IndicatorCreate, IndicatorResponse, IndicatorWithAssessment,
    InterviewAssessmentSummary, AssessmentResponse, ManualScoreInput
)
from ..services.batch_processor import get_batch_processor
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_interview = Interview(
        candidate_name=interview_data.candidate_name,
        candidate_email=interview_data.candidate_email,
        candidate_id_number=interview_data.candidate_id_number,
        position=interview_data.position,
        scheduled_at=interview_data.scheduled_at,
        interviewer_id=current_user.id,
        status=InterviewStatus.SCHEDULED
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    
    db_score = InterviewScore(interview_id=db_interview.id)
    db.add(db_score)
    db.commit()
    
    return db_interview

@router.get("/", response_model=List[InterviewResponse])
def list_interviews(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Interview)
    
    if current_user.role != "admin":
        query = query.filter(Interview.interviewer_id == current_user.id)
    
    if status:
        query = query.filter(Interview.status == status)
    
    interviews = query.order_by(Interview.created_at.desc()).offset(skip).limit(limit).all()
    return interviews

@router.get("/{interview_id}", response_model=InterviewDetailResponse)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    return interview

@router.put("/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this interview")
    
    for key, value in interview_data.model_dump(exclude_unset=True).items():
        setattr(interview, key, value)
    
    db.commit()
    db.refresh(interview)
    return interview

@router.post("/{interview_id}/start", response_model=InterviewResponse)
def start_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    interview.status = InterviewStatus.IN_PROGRESS
    interview.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(interview)
    return interview

class CompleteInterviewRequest(BaseModel):
    audio_file_path: Optional[str] = None

@router.post("/{interview_id}/complete", response_model=InterviewResponse)
def complete_interview(
    interview_id: int,
    request: Optional[CompleteInterviewRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    interview.status = InterviewStatus.COMPLETED
    interview.ended_at = datetime.utcnow()
    
    if interview.started_at:
        duration = (interview.ended_at - interview.started_at).total_seconds()
        interview.duration_seconds = int(duration)
    
    # Save audio file path if provided
    if request and request.audio_file_path:
        interview.audio_file_path = request.audio_file_path
        interview.processing_status = "recording"  # Ready for batch processing
    
    db.commit()
    db.refresh(interview)
    return interview

@router.put("/{interview_id}/scores", response_model=InterviewScoreResponse)
def update_interview_scores(
    interview_id: int,
    score_data: InterviewScoreInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    score = db.query(InterviewScore).filter(InterviewScore.interview_id == interview_id).first()
    
    if not score:
        score = InterviewScore(interview_id=interview_id)
        db.add(score)
    
    for key, value in score_data.model_dump(exclude_unset=True).items():
        setattr(score, key, value)
    
    manual_scores = [
        score.berorientasi_pelayanan_manual,
        score.akuntabel_manual,
        score.kompeten_manual,
        score.harmonis_manual,
        score.loyal_manual,
        score.adaptif_manual,
        score.kolaboratif_manual
    ]
    manual_scores = [s for s in manual_scores if s is not None]
    
    if manual_scores:
        score.overall_manual_score = sum(manual_scores) / len(manual_scores)
    
    if score.overall_ai_score and score.overall_manual_score:
        score.final_score = (score.overall_ai_score * 0.6 + score.overall_manual_score * 0.4)
    elif score.overall_ai_score:
        score.final_score = score.overall_ai_score
    
    db.commit()
    db.refresh(score)
    return score

@router.get("/{interview_id}/emotions")
def get_interview_emotions(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get emotion statistics for an interview (facial + speech)"""
    from ..models.interview import Interview, EmotionLog
    from collections import Counter
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Get all emotion logs
    emotion_logs = db.query(EmotionLog).filter(
        EmotionLog.interview_id == interview_id
    ).order_by(EmotionLog.timestamp).all()
    
    if not emotion_logs:
        return {
            "total_detections": 0,
            "facial_emotion_distribution": {},
            "speech_emotion_distribution": {},
            "dominant_facial_emotion": "neutral",
            "dominant_speech_emotion": "neutral",
            "average_facial_confidence": 0.0,
            "average_speech_confidence": 0.0,
            "emotion_timeline": [],
            "emotion_stability": 1.0
        }
    
    # Separate facial and speech emotions
    facial_emotions = [log.facial_emotion for log in emotion_logs if log.facial_emotion]
    facial_confidences = [log.facial_confidence for log in emotion_logs if log.facial_confidence]
    
    speech_emotions = [log.speech_emotion for log in emotion_logs if log.speech_emotion]
    speech_confidences = [log.speech_confidence for log in emotion_logs if log.speech_confidence]
    
    # Facial emotion statistics
    facial_distribution = {}
    dominant_facial = "neutral"
    avg_facial_conf = 0.0
    
    if facial_emotions:
        facial_counts = Counter(facial_emotions)
        total_facial = len(facial_emotions)
        facial_distribution = {
            emotion: round(count / total_facial * 100, 1)
            for emotion, count in facial_counts.most_common()
        }
        dominant_facial = facial_counts.most_common(1)[0][0]
        avg_facial_conf = round(sum(facial_confidences) / len(facial_confidences), 3)
    
    # Speech emotion statistics
    speech_distribution = {}
    dominant_speech = "neutral"
    avg_speech_conf = 0.0
    
    if speech_emotions:
        speech_counts = Counter(speech_emotions)
        total_speech = len(speech_emotions)
        speech_distribution = {
            emotion: round(count / total_speech * 100, 1)
            for emotion, count in speech_counts.most_common()
        }
        dominant_speech = speech_counts.most_common(1)[0][0]
        avg_speech_conf = round(sum(speech_confidences) / len(speech_confidences), 3)
    
    # Combined timeline (sample every 5 seconds for visualization)
    timeline = []
    if emotion_logs:
        start_time = emotion_logs[0].timestamp
        for log in emotion_logs[::5]:  # Sample every 5th entry
            timeline.append({
                "time": round(log.timestamp - start_time, 1),
                "facial_emotion": log.facial_emotion,
                "facial_confidence": round(log.facial_confidence, 2) if log.facial_confidence else 0,
                "speech_emotion": log.speech_emotion,
                "speech_confidence": round(log.speech_confidence, 2) if log.speech_confidence else 0
            })
    
    # Emotion stability (using facial emotions as primary)
    emotion_stability = 1.0
    if facial_emotions and len(facial_emotions) > 1:
        changes = sum(1 for i in range(1, len(facial_emotions)) if facial_emotions[i] != facial_emotions[i-1])
        emotion_stability = round(1.0 - (changes / len(facial_emotions)), 3)
    
    # Overall distribution (combine both if available, otherwise use what we have)
    if facial_emotions and speech_emotions:
        # Combine both for overall picture
        all_emotions = facial_emotions + speech_emotions
        emotion_counts = Counter(all_emotions)
        total = len(all_emotions)
        emotion_distribution = {
            emotion: round(count / total * 100, 1)
            for emotion, count in emotion_counts.most_common()
        }
        dominant_emotion = emotion_counts.most_common(1)[0][0]
    elif facial_emotions:
        emotion_distribution = facial_distribution
        dominant_emotion = dominant_facial
    else:
        emotion_distribution = speech_distribution
        dominant_emotion = dominant_speech
    
    return {
        "total_detections": len(emotion_logs),
        "emotion_distribution": emotion_distribution,  # Combined
        "facial_emotion_distribution": facial_distribution,
        "speech_emotion_distribution": speech_distribution,
        "dominant_emotion": dominant_emotion,  # Combined
        "dominant_facial_emotion": dominant_facial,
        "dominant_speech_emotion": dominant_speech,
        "average_confidence": round((avg_facial_conf + avg_speech_conf) / 2, 3) if (avg_facial_conf > 0 or avg_speech_conf > 0) else 0.0,
        "average_facial_confidence": avg_facial_conf,
        "average_speech_confidence": avg_speech_conf,
        "emotion_timeline": timeline,
        "emotion_stability": emotion_stability
    }

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(interview)
    db.commit()
    return

# ============================================================================
# BATCH PROCESSING ENDPOINTS
# ============================================================================

@router.post("/{interview_id}/process")
def process_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start batch processing for interview:
    1. Transcribe audio with Whisper
    2. Analyze with custom indicators
    3. Generate assessment scores
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if audio file exists
    if not interview.audio_file_path:
        raise HTTPException(status_code=400, detail="No audio file found for this interview")
    
    # Check if already processing
    if interview.processing_status == "processing":
        raise HTTPException(status_code=400, detail="Interview is already being processed")
    
    # Allow reprocessing if already completed (will update existing assessment)
    # if interview.processing_status == "completed":
    #     raise HTTPException(status_code=400, detail="Interview has already been processed")
    
    # Get indicators for this interview
    indicators = db.query(InterviewIndicator).filter(
        InterviewIndicator.interview_id == interview_id
    ).all()
    
    if not indicators:
        raise HTTPException(
            status_code=400, 
            detail="No indicators defined for this interview. Please add indicators first."
        )
    
    # Prepare indicators data
    indicators_data = [
        {
            'id': ind.id,
            'name': ind.name,
            'description': ind.description,
            'weight': float(ind.weight)
        }
        for ind in indicators
    ]
    
    # Start batch processing
    try:
        processor = get_batch_processor()
        result = processor.process_interview(
            interview_id=interview_id,
            audio_file_path=interview.audio_file_path,
            indicators=indicators_data,
            db=db
        )
        
        if result['success']:
            return {
                "message": "Interview processed successfully",
                "interview_id": interview_id,
                "transcript_length": result['transcript_length'],
                "assessments_count": result['assessments_count'],
                "overall_score": result['overall_score']
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Processing failed'))
            
    except Exception as e:
        logger.error(f"Error processing interview {interview_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{interview_id}/assessment", response_model=InterviewAssessmentSummary)
def get_interview_assessment(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get assessment results for processed interview
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if processed
    if interview.processing_status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Interview has not been processed yet. Current status: {interview.processing_status}"
        )
    
    # Get all indicators with their assessments
    indicators = db.query(InterviewIndicator).filter(
        InterviewIndicator.interview_id == interview_id
    ).all()
    
    indicators_with_assessments = []
    total_weighted_score = 0.0
    total_weight = 0.0
    assessed_count = 0
    
    for indicator in indicators:
        assessment = db.query(InterviewAssessment).filter(
            InterviewAssessment.interview_id == interview_id,
            InterviewAssessment.indicator_id == indicator.id
        ).first()
        
        indicator_data = IndicatorWithAssessment(
            id=indicator.id,
            interview_id=indicator.interview_id,
            name=indicator.name,
            description=indicator.description,
            weight=indicator.weight,
            created_at=indicator.created_at,
            assessment=AssessmentResponse(
                id=assessment.id,
                interview_id=assessment.interview_id,
                indicator_id=assessment.indicator_id,
                score=assessment.score,
                manual_score=assessment.manual_score,
                evidence=assessment.evidence,
                reasoning=assessment.reasoning,
                interviewer_notes=assessment.interviewer_notes,
                created_at=assessment.created_at
            ) if assessment else None
        )
        
        indicators_with_assessments.append(indicator_data)
        
        if assessment:
            # Use combined score if manual score exists, otherwise use AI score
            final_score = float(assessment.score)  # Default to AI score
            
            if assessment.manual_score is not None and assessment.manual_score > 0:
                # Get scoring weights from settings
                from ..models.settings import AppSetting
                ai_weight_setting = db.query(AppSetting).filter(
                    AppSetting.setting_key == "ai_score_weight"
                ).first()
                manual_weight_setting = db.query(AppSetting).filter(
                    AppSetting.setting_key == "manual_score_weight"
                ).first()
                
                ai_weight = float(ai_weight_setting.setting_value) / 100 if ai_weight_setting else 0.6
                manual_weight = float(manual_weight_setting.setting_value) / 100 if manual_weight_setting else 0.4
                
                # Calculate combined score
                final_score = (float(assessment.score) * ai_weight) + (float(assessment.manual_score) * manual_weight)
            
            total_weighted_score += final_score * float(indicator.weight)
            total_weight += float(indicator.weight)
            assessed_count += 1
    
    overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    return InterviewAssessmentSummary(
        indicators=indicators_with_assessments,
        overall_score=overall_score,
        total_indicators=len(indicators),
        assessed_indicators=assessed_count
    )

@router.put("/{interview_id}/manual-scores", response_model=InterviewAssessmentSummary)
def update_manual_scores(
    interview_id: int,
    score_data: ManualScoreInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update manual scores for interview assessments
    Allows interviewer to input manual scores alongside AI scores
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if processed
    if interview.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Interview must be processed first before adding manual scores"
        )
    
    # Update manual scores for each indicator
    updated_count = 0
    for indicator_id, manual_score in score_data.manual_scores.items():
        assessment = db.query(InterviewAssessment).filter(
            InterviewAssessment.interview_id == interview_id,
            InterviewAssessment.indicator_id == indicator_id
        ).first()
        
        if assessment:
            assessment.manual_score = manual_score
            if score_data.interviewer_notes:
                assessment.interviewer_notes = score_data.interviewer_notes
            updated_count += 1
    
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="No assessments found to update")
    
    db.commit()
    
    logger.info(f"Updated {updated_count} manual scores for interview {interview_id}")
    
    # Return updated assessment summary
    return get_interview_assessment(interview_id, db, current_user)

# ============================================================================
# INDICATORS MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{interview_id}/indicators", response_model=IndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_indicator(
    interview_id: int,
    indicator_data: IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a custom indicator for an interview
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Don't allow adding indicators after processing started
    if interview.processing_status in ["processing", "completed"]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot add indicators after processing has started"
        )
    
    db_indicator = InterviewIndicator(
        interview_id=interview_id,
        name=indicator_data.name,
        description=indicator_data.description,
        weight=indicator_data.weight
    )
    
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    
    return db_indicator

@router.get("/{interview_id}/indicators", response_model=List[IndicatorResponse])
def list_indicators(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all indicators for an interview
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    indicators = db.query(InterviewIndicator).filter(
        InterviewIndicator.interview_id == interview_id
    ).all()
    
    return indicators

@router.delete("/{interview_id}/indicators/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(
    interview_id: int,
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an indicator
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if current_user.role != "admin" and interview.interviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Don't allow deleting indicators after processing started
    if interview.processing_status in ["processing", "completed"]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete indicators after processing has started"
        )
    
    indicator = db.query(InterviewIndicator).filter(
        InterviewIndicator.id == indicator_id,
        InterviewIndicator.interview_id == interview_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    
    db.delete(indicator)
    db.commit()
    return None


# ============================================================================
# ADVANCED FEATURES FOR COMPETITION
# ============================================================================

@router.get("/dashboard/statistics")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard statistics
    For competition - shows AI capabilities at scale
    """
    try:
        from sqlalchemy import func
        from datetime import timedelta
        
        # Total interviews
        total_query = db.query(Interview)
        if current_user.role != "admin":
            total_query = total_query.filter(Interview.interviewer_id == current_user.id)
        total_interviews = total_query.count()
        
        # Completed interviews
        completed_interviews = total_query.filter(
            Interview.status == InterviewStatus.COMPLETED
        ).count()
        
        # Average score
        avg_score_query = db.query(func.avg(InterviewScore.final_score))\
            .join(Interview)\
            .filter(Interview.status == InterviewStatus.COMPLETED)
        if current_user.role != "admin":
            avg_score_query = avg_score_query.filter(Interview.interviewer_id == current_user.id)
        avg_score_result = avg_score_query.scalar()
        avg_score = round(float(avg_score_result), 2) if avg_score_result else 0
        
        # Top performers (top 5 by score)
        top_performers_query = db.query(
            Interview.candidate_name,
            Interview.position,
            InterviewScore.final_score
        ).join(InterviewScore).filter(
            Interview.status == InterviewStatus.COMPLETED
        )
        if current_user.role != "admin":
            top_performers_query = top_performers_query.filter(Interview.interviewer_id == current_user.id)
        top_performers = top_performers_query.order_by(InterviewScore.final_score.desc()).limit(5).all()
        
        # Score distribution (0-20, 20-40, 40-60, 60-80, 80-100)
        score_distribution = {
            "0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0
        }
        all_scores_query = db.query(InterviewScore.final_score)\
            .join(Interview)\
            .filter(Interview.status == InterviewStatus.COMPLETED)
        if current_user.role != "admin":
            all_scores_query = all_scores_query.filter(Interview.interviewer_id == current_user.id)
        all_scores = all_scores_query.all()
        
        for (score,) in all_scores:
            if score and score <= 20:
                score_distribution["0-20"] += 1
            elif score and score <= 40:
                score_distribution["20-40"] += 1
            elif score and score <= 60:
                score_distribution["40-60"] += 1
            elif score and score <= 80:
                score_distribution["60-80"] += 1
            elif score:
                score_distribution["80-100"] += 1
        
        # Top indicators performance
        top_indicators_query = db.query(
            InterviewIndicator.name,
            func.avg(InterviewAssessment.score).label('avg_score'),
            func.count(InterviewAssessment.id).label('count')
        ).join(InterviewAssessment)\
         .join(Interview, Interview.id == InterviewIndicator.interview_id)\
         .filter(Interview.status == InterviewStatus.COMPLETED)
        if current_user.role != "admin":
            top_indicators_query = top_indicators_query.filter(Interview.interviewer_id == current_user.id)
        top_indicators = top_indicators_query.group_by(InterviewIndicator.name)\
         .order_by(func.avg(InterviewAssessment.score).desc())\
         .limit(10).all()
        
        # Processing success rate
        processing_completed = total_query.filter(
            Interview.processing_status == "completed"
        ).count()
        processing_failed = total_query.filter(
            Interview.processing_status == "failed"
        ).count()
        
        success_rate = round((processing_completed / (processing_completed + processing_failed)) * 100, 1) if (processing_completed + processing_failed) > 0 else 100
        
        # Recent interviews (last 7 days trend)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_trend = []
        for i in range(7):
            day = seven_days_ago + timedelta(days=i)
            count = total_query.filter(
                func.date(Interview.created_at) == day.date()
            ).count()
            recent_trend.append({
                "date": day.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return {
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "avg_score": avg_score,
            "top_performers": [
                {
                    "name": name,
                    "position": position,
                    "score": float(score) if score else 0
                }
                for name, position, score in top_performers
            ],
            "score_distribution": score_distribution,
            "top_indicators": [
                {
                    "name": name,
                    "avg_score": round(float(avg_score), 2) if avg_score else 0,
                    "count": count
                }
                for name, avg_score, count in top_indicators
            ],
            "processing_success_rate": success_rate,
            "recent_trend": recent_trend
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
def compare_candidates(
    interview_ids: str,  # comma-separated IDs
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple candidates side-by-side
    For competition - unique feature for decision support
    """
    try:
        # Parse interview IDs
        ids = [int(id.strip()) for id in interview_ids.split(",")]
        
        # Get interviews
        interviews = db.query(Interview).filter(Interview.id.in_(ids)).all()
        
        if not interviews:
            raise HTTPException(status_code=404, detail="Interviews not found")
        
        comparison = []
        for interview in interviews:
            # Get score
            score = db.query(InterviewScore).filter_by(interview_id=interview.id).first()
            
            # Get assessments
            assessments = db.query(InterviewAssessment)\
                .join(InterviewIndicator)\
                .filter(InterviewIndicator.interview_id == interview.id)\
                .all()
            
            # Get top strengths (top 3 indicators)
            strengths = sorted(assessments, key=lambda a: a.score, reverse=True)[:3]
            
            # Get weaknesses (bottom 3 indicators)
            weaknesses = sorted(assessments, key=lambda a: a.score)[:3]
            
            comparison.append({
                "id": interview.id,
                "candidate_name": interview.candidate_name,
                "position": interview.position,
                "total_score": float(score.final_score) if score else 0,
                "ai_score": float(score.overall_ai_score) if score else 0,
                "manual_score": float(score.overall_manual_score) if score else 0,
                "emotion_score": float(score.emotion_stability) if score else 0,
                "strengths": [
                    {
                        "indicator": s.indicator.name,
                        "score": float(s.score),
                        "reasoning": s.reasoning[:100] + "..." if len(s.reasoning) > 100 else s.reasoning
                    }
                    for s in strengths
                ] if strengths else [],
                "weaknesses": [
                    {
                        "indicator": w.indicator.name,
                        "score": float(w.score),
                        "reasoning": w.reasoning[:100] + "..." if len(w.reasoning) > 100 else w.reasoning
                    }
                    for w in weaknesses
                ] if weaknesses else [],
                "duration": interview.duration_seconds,
                "date": interview.created_at.isoformat() if interview.created_at else None
            })
        
        return {
            "candidates": comparison,
            "comparison_date": datetime.utcnow().isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid interview IDs format")
    except Exception as e:
        logger.error(f"Error comparing candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_id}/transcript")
def get_interview_transcript(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get interview transcript with timestamps
    For competition - unique transcript viewer feature
    """
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check authorization
        if current_user.role != "admin" and interview.interviewer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get assessments
        assessments = db.query(InterviewAssessment)\
            .join(InterviewIndicator)\
            .filter(InterviewIndicator.interview_id == interview_id)\
            .all()
        
        # Collect all matched sentences
        all_sentences = []
        for assessment in assessments:
            if assessment.matched_sentences:
                sentences = assessment.matched_sentences.split("\n")
                for sentence in sentences:
                    if sentence.strip():
                        all_sentences.append({
                            "text": sentence.strip(),
                            "indicator": assessment.indicator.name,
                            "confidence": float(assessment.score) / 100
                        })
        
        return {
            "interview_id": interview_id,
            "candidate_name": interview.candidate_name,
            "position": interview.position,
            "duration": interview.duration_seconds,
            "transcript": all_sentences,
            "total_segments": len(all_sentences)
        }
        
    except Exception as e:
        logger.error(f"Error getting transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_id}/recommendations")
def get_ai_recommendations(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered hiring recommendations
    For competition - UNIQUE FEATURE for decision support
    """
    try:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check authorization
        if current_user.role != "admin" and interview.interviewer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get score
        score = db.query(InterviewScore).filter_by(interview_id=interview_id).first()
        if not score:
            return {
                "interview_id": interview_id,
                "candidate_name": interview.candidate_name,
                "position": interview.position,
                "decision": "PENDING",
                "confidence": 0,
                "reason": "Interview not yet processed",
                "total_score": 0,
                "strengths": [],
                "areas_for_improvement": [],
                "next_steps": ["Complete interview processing first"],
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Get assessments
        assessments = db.query(InterviewAssessment)\
            .join(InterviewIndicator)\
            .filter(InterviewIndicator.interview_id == interview_id)\
            .all()
        
        # AI Recommendation Logic
        total_score = float(score.final_score) if score.final_score else 0
        
        # Decision
        if total_score >= 80:
            decision = "HIGHLY RECOMMENDED"
            confidence = 0.95
            reason = "Exceptional performance across all indicators"
        elif total_score >= 70:
            decision = "RECOMMENDED"
            confidence = 0.85
            reason = "Strong performance with good potential"
        elif total_score >= 60:
            decision = "CONSIDER"
            confidence = 0.70
            reason = "Meets basic requirements, some areas need improvement"
        elif total_score >= 50:
            decision = "BORDERLINE"
            confidence = 0.60
            reason = "Several concerns, requires further evaluation"
        else:
            decision = "NOT RECOMMENDED"
            confidence = 0.50
            reason = "Significant gaps in required competencies"
        
        # Strengths
        strengths = sorted(assessments, key=lambda a: a.score, reverse=True)[:3] if assessments else []
        
        # Areas for improvement
        improvements = sorted(assessments, key=lambda a: a.score)[:3] if assessments else []
        
        # Next steps
        next_steps = []
        if decision in ["HIGHLY RECOMMENDED", "RECOMMENDED"]:
            next_steps = [
                "Proceed to final interview round",
                "Verify references and credentials",
                "Discuss compensation and start date"
            ]
        elif decision == "CONSIDER":
            next_steps = [
                "Conduct additional technical assessment",
                "Schedule follow-up interview on weak areas",
                "Compare with other candidates"
            ]
        else:
            next_steps = [
                "Send polite rejection with feedback",
                "Keep in talent pool for future opportunities",
                "Continue candidate search"
            ]
        
        return {
            "interview_id": interview_id,
            "candidate_name": interview.candidate_name,
            "position": interview.position,
            "decision": decision,
            "confidence": round(confidence, 2),
            "reason": reason,
            "total_score": total_score,
            "strengths": [
                {
                    "indicator": s.indicator.name,
                    "score": float(s.score),
                    "summary": s.reasoning[:150] + "..." if len(s.reasoning) > 150 else s.reasoning
                }
                for s in strengths
            ],
            "areas_for_improvement": [
                {
                    "indicator": i.indicator.name,
                    "score": float(i.score),
                    "suggestion": i.reasoning[:150] + "..." if len(i.reasoning) > 150 else i.reasoning
                }
                for i in improvements
            ],
            "next_steps": next_steps,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recalculate-scores")
async def recalculate_all_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Utility endpoint to recalculate overall_ai_score and final_score for all completed interviews.
    Useful for fixing interviews that were processed before scoring logic was added.
    """
    try:
        from sqlalchemy import func
        from ..models.indicator import InterviewIndicator, InterviewAssessment
        
        # Find all completed interviews
        interviews_query = db.query(Interview).filter(
            Interview.status == InterviewStatus.COMPLETED,
            Interview.processing_status == "completed"
        )
        
        # For non-admin users, only their interviews
        if current_user.role != "admin":
            interviews_query = interviews_query.filter(Interview.interviewer_id == current_user.id)
        
        interviews = interviews_query.all()
        
        updated_count = 0
        skipped_count = 0
        
        for interview in interviews:
            # Get all assessments for this interview
            assessments = db.query(InterviewAssessment).filter(
                InterviewAssessment.interview_id == interview.id
            ).all()
            
            if not assessments:
                skipped_count += 1
                continue
            
            # Get indicators with weights
            indicator_ids = [a.indicator_id for a in assessments]
            indicators = db.query(InterviewIndicator).filter(
                InterviewIndicator.id.in_(indicator_ids)
            ).all()
            
            weight_map = {ind.id: float(ind.weight) for ind in indicators}
            
            # Calculate weighted average score
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for assessment in assessments:
                score = float(assessment.score)
                weight = weight_map.get(assessment.indicator_id, 1.0)
                total_weighted_score += score * weight
                total_weight += weight
            
            overall_ai_score = round(total_weighted_score / total_weight, 2) if total_weight > 0 else 0.0
            
            # Get or create InterviewScore
            score_record = db.query(InterviewScore).filter(
                InterviewScore.interview_id == interview.id
            ).first()
            
            if not score_record:
                score_record = InterviewScore(interview_id=interview.id)
                db.add(score_record)
            
            # Update scores
            score_record.overall_ai_score = overall_ai_score
            
            # Set final_score
            if score_record.overall_manual_score:
                # Recalculate with manual score (60% AI, 40% Manual)
                score_record.final_score = round(
                    (overall_ai_score * 0.6) + (score_record.overall_manual_score * 0.4), 2
                )
            else:
                # No manual score, use AI score
                score_record.final_score = overall_ai_score
            
            updated_count += 1
        
        db.commit()
        
        logger.info(f"Score recalculation complete: {updated_count} updated, {skipped_count} skipped")
        
        return {
            "success": True,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "total_interviews": len(interviews),
            "message": f"Successfully recalculated scores for {updated_count} interviews"
        }
        
    except Exception as e:
        logger.error(f"Error recalculating scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
