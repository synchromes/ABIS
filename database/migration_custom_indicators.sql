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

ALTER TABLE interviews
ADD COLUMN indicators_config JSON DEFAULT NULL;

---
