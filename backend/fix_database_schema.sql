-- Fix Database Schema for ABIS
-- Run this in MySQL/phpMyAdmin to add missing columns

USE abis_interview;

-- Check if columns exist, if not add them
-- For interview_scores table

-- Drop the table and recreate with correct schema
DROP TABLE IF EXISTS interview_scores;

CREATE TABLE interview_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL UNIQUE,
    
    -- Behavioral scores (AI + Manual)
    berorientasi_pelayanan_ai FLOAT DEFAULT NULL,
    berorientasi_pelayanan_manual FLOAT DEFAULT NULL,
    
    akuntabel_ai FLOAT DEFAULT NULL,
    akuntabel_manual FLOAT DEFAULT NULL,
    
    kompeten_ai FLOAT DEFAULT NULL,
    kompeten_manual FLOAT DEFAULT NULL,
    
    harmonis_ai FLOAT DEFAULT NULL,
    harmonis_manual FLOAT DEFAULT NULL,
    
    loyal_ai FLOAT DEFAULT NULL,
    loyal_manual FLOAT DEFAULT NULL,
    
    adaptif_ai FLOAT DEFAULT NULL,
    adaptif_manual FLOAT DEFAULT NULL,
    
    kolaboratif_ai FLOAT DEFAULT NULL,
    kolaboratif_manual FLOAT DEFAULT NULL,
    
    -- Performance metrics
    emotion_stability FLOAT DEFAULT NULL,
    speech_clarity FLOAT DEFAULT NULL,
    answer_coherence FLOAT DEFAULT NULL,
    
    -- Overall scores
    overall_ai_score FLOAT DEFAULT NULL,
    overall_manual_score FLOAT DEFAULT NULL,
    final_score FLOAT DEFAULT NULL,
    
    -- Analysis text
    ai_analysis_summary TEXT DEFAULT NULL,
    interviewer_notes TEXT DEFAULT NULL,
    
    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key
    CONSTRAINT fk_interview_scores_interview 
        FOREIGN KEY (interview_id) 
        REFERENCES interviews(id) 
        ON DELETE CASCADE,
        
    INDEX idx_interview_id (interview_id),
    INDEX idx_final_score (final_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Success message
SELECT 'Database schema fixed successfully!' as message;
