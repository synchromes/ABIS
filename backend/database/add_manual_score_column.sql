-- Add manual_score column to interview_assessments table
-- This allows interviewers to input manual scores alongside AI scores

ALTER TABLE interview_assessments 
ADD COLUMN manual_score DECIMAL(5,2) DEFAULT NULL AFTER score;

ALTER TABLE interview_assessments
ADD COLUMN interviewer_notes TEXT DEFAULT NULL AFTER reasoning;

-- Update existing rows to have NULL manual_score (not required initially)
UPDATE interview_assessments SET manual_score = NULL WHERE manual_score IS NULL;
