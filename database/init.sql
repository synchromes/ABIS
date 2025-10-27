
-- ============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE abis_interview;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'interviewer', 'viewer') DEFAULT 'interviewer' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_name VARCHAR(100) NOT NULL,
    candidate_email VARCHAR(100),
    candidate_id_number VARCHAR(50),
    candidate_phone VARCHAR(50),
    position VARCHAR(100) NOT NULL,
    notes TEXT,
    status ENUM('scheduled', 'in_progress', 'completed', 'cancelled') DEFAULT 'scheduled' NOT NULL,
    recommendation ENUM('layak', 'dipertimbangkan', 'tidak_layak'),
    interviewer_id INT NOT NULL,
    scheduled_at DATETIME,
    started_at DATETIME,
    ended_at DATETIME,
    duration_seconds INT,
    
    -- File paths
    video_file_path VARCHAR(255),
    audio_file_path VARCHAR(512),
    transcript_file_path VARCHAR(255),
    report_file_path VARCHAR(255),
    
    -- Processing
    transcript LONGTEXT,
    processing_status ENUM('recording', 'processing', 'completed', 'failed') DEFAULT 'recording',
    processed_at DATETIME,
    
    -- Custom indicators config (JSON)
    indicators_config JSON,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign keys and indexes
    FOREIGN KEY (interviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_interviewer (interviewer_id),
    INDEX idx_processing_status (processing_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Interview scores table
CREATE TABLE IF NOT EXISTS interview_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT UNIQUE NOT NULL,
    
    -- Behavioral scores (AI detected)
    berorientasi_pelayanan_ai FLOAT,
    akuntabel_ai FLOAT,
    kompeten_ai FLOAT,
    harmonis_ai FLOAT,
    loyal_ai FLOAT,
    adaptif_ai FLOAT,
    kolaboratif_ai FLOAT,
    
    -- Behavioral scores (Manual override)
    berorientasi_pelayanan_manual FLOAT,
    akuntabel_manual FLOAT,
    kompeten_manual FLOAT,
    harmonis_manual FLOAT,
    loyal_manual FLOAT,
    adaptif_manual FLOAT,
    kolaboratif_manual FLOAT,
    
    -- Performance metrics
    emotion_stability FLOAT,
    speech_clarity FLOAT,
    answer_coherence FLOAT,
    
    -- Overall scores
    overall_ai_score FLOAT,
    overall_manual_score FLOAT,
    final_score FLOAT,
    
    -- Analysis
    ai_analysis_summary TEXT,
    interviewer_notes TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign keys and indexes
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_interview_id (interview_id),
    INDEX idx_final_score (final_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- CUSTOM INDICATORS SYSTEM
-- ============================================================================

-- Interview indicators table (custom indicators per interview)
CREATE TABLE IF NOT EXISTS interview_indicators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    keywords TEXT,
    weight DECIMAL(5,2) DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_interview_id (interview_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Interview assessments table (AI scores for each indicator)
CREATE TABLE IF NOT EXISTS interview_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    indicator_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    manual_score DECIMAL(5,2),
    evidence TEXT,
    reasoning TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    FOREIGN KEY (indicator_id) REFERENCES interview_indicators(id) ON DELETE CASCADE,
    INDEX idx_interview_id (interview_id),
    INDEX idx_indicator_id (indicator_id),
    UNIQUE KEY unique_interview_indicator (interview_id, indicator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TRANSCRIPT & EMOTION TRACKING
-- ============================================================================

-- Transcript entries table (detailed transcript with timing)
CREATE TABLE IF NOT EXISTS transcript_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    speaker VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    timestamp FLOAT NOT NULL,
    confidence FLOAT,
    emotion_detected VARCHAR(50),
    sentiment_score FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_interview (interview_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Emotion logs table (real-time emotion detection during interview)
CREATE TABLE IF NOT EXISTS emotion_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    timestamp FLOAT NOT NULL,
    
    -- Facial emotion (from DeepFace)
    facial_emotion VARCHAR(50),
    facial_confidence FLOAT,
    
    -- Speech emotion (from audio analysis)
    speech_emotion VARCHAR(50),
    speech_confidence FLOAT,
    
    -- Detailed emotion scores (JSON)
    emotion_scores JSON,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_interview (interview_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SETTINGS TABLE
-- ============================================================================

-- Settings table (system configuration)
CREATE TABLE IF NOT EXISTS app_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_setting_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default settings
INSERT INTO app_settings (setting_key, setting_value, description) VALUES
('ai_score_weight', '60', 'Persentase bobot penilaian AI (0-100)'),
('manual_score_weight', '40', 'Persentase bobot penilaian manual (0-100)'),
('emotion_threshold', '0.7', 'Minimum confidence threshold for emotion detection'),
('semantic_threshold', '0.5', 'Minimum similarity threshold for semantic matching')
ON DUPLICATE KEY UPDATE setting_key=setting_key;

-- ============================================================================
-- DEFAULT USERS
-- ============================================================================

-- Insert default admin user
-- Username: admin
-- Password: admin123
INSERT INTO users (username, email, full_name, hashed_password, role, is_active) 
VALUES (
    'admin',
    'admin@abis.local',
    'Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PLP.peWYOeXC',
    'admin',
    TRUE
) ON DUPLICATE KEY UPDATE username=username;

-- Insert sample interviewer
-- Username: interviewer1
-- Password: interviewer123
INSERT INTO users (username, email, full_name, hashed_password, role, is_active) 
VALUES (
    'interviewer1',
    'interviewer1@abis.local',
    'Pewawancara Satu',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn98vJ5KP8RXQ6zPJnZZQF3lYpxC',
    'interviewer',
    TRUE
) ON DUPLICATE KEY UPDATE username=username;

-- ============================================================================
-- VERIFICATION QUERIES (Optional - for testing)
-- ============================================================================

-- Uncomment to verify installation:
-- SELECT 'Database initialized successfully!' as message;
-- SELECT COUNT(*) as users_count FROM users;
-- SELECT COUNT(*) as interviews_count FROM interviews;
-- SELECT COUNT(*) as scores_count FROM interview_scores;
-- SELECT COUNT(*) as indicators_count FROM interview_indicators;
-- SELECT COUNT(*) as assessments_count FROM interview_assessments;
-- SELECT COUNT(*) as settings_count FROM app_settings;
-- SHOW TABLES;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
