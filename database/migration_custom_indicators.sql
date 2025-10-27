-- Migration: Add Custom Indicators and Audio Recording
-- Created: 2025-10-16
-- Description: Refactor from real-time transcription to batch processing with custom indicators

-- Step 1: Create interview_indicators table
CREATE TABLE IF NOT EXISTS interview_indicators (
    id INT PRIMARY KEY AUTO_INCREMENT,
    interview_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    weight DECIMAL(5,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_interview_id (interview_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 2: Create interview_assessments table
CREATE TABLE IF NOT EXISTS interview_assessments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    interview_id INT NOT NULL,
    indicator_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    evidence TEXT,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    FOREIGN KEY (indicator_id) REFERENCES interview_indicators(id) ON DELETE CASCADE,
    INDEX idx_interview_id (interview_id),
    INDEX idx_indicator_id (indicator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 3: Update interviews table (separate statements to handle existing columns gracefully)
ALTER TABLE interviews 
ADD COLUMN audio_file_path VARCHAR(512) DEFAULT NULL;

ALTER TABLE interviews 
ADD COLUMN transcript LONGTEXT DEFAULT NULL;

ALTER TABLE interviews 
ADD COLUMN processing_status ENUM('recording', 'processing', 'completed', 'failed') DEFAULT 'recording';

ALTER TABLE interviews 
ADD COLUMN processed_at TIMESTAMP NULL DEFAULT NULL;

ALTER TABLE interviews 
ADD INDEX idx_processing_status (processing_status);

-- Step 4: Add indicators_config to interviews table (JSON field for custom indicators)
ALTER TABLE interviews
ADD COLUMN indicators_config JSON DEFAULT NULL;

-- Verification queries (run these to verify migration)
-- SELECT COUNT(*) as indicators_count FROM interview_indicators;
-- SELECT COUNT(*) as assessments_count FROM interview_assessments;
-- SHOW COLUMNS FROM interviews LIKE '%audio%';
-- SHOW COLUMNS FROM interviews LIKE '%transcript%';
-- SHOW COLUMNS FROM interviews LIKE '%processing%';
