# Add this endpoint after get_interview_assessment in interviews.py

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
