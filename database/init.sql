-- Create database
CREATE DATABASE IF NOT EXISTS abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE abis_interview;

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
    position VARCHAR(100) NOT NULL,
    status ENUM('scheduled', 'in_progress', 'completed', 'cancelled') DEFAULT 'scheduled' NOT NULL,
    recommendation ENUM('layak', 'dipertimbangkan', 'tidak_layak'),
    interviewer_id INT NOT NULL,
    scheduled_at DATETIME,
    started_at DATETIME,
    ended_at DATETIME,
    duration_seconds INT,
    video_file_path VARCHAR(255),
    audio_file_path VARCHAR(255),
    transcript_file_path VARCHAR(255),
    report_file_path VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (interviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_interviewer (interviewer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Interview scores table
CREATE TABLE IF NOT EXISTS interview_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT UNIQUE NOT NULL,
    berorientasi_pelayanan_ai FLOAT,
    berorientasi_pelayanan_manual FLOAT,
    akuntabel_ai FLOAT,
    akuntabel_manual FLOAT,
    kompeten_ai FLOAT,
    kompeten_manual FLOAT,
    harmonis_ai FLOAT,
    harmonis_manual FLOAT,
    loyal_ai FLOAT,
    loyal_manual FLOAT,
    adaptif_ai FLOAT,
    adaptif_manual FLOAT,
    kolaboratif_ai FLOAT,
    kolaboratif_manual FLOAT,
    emotion_stability FLOAT,
    speech_clarity FLOAT,
    answer_coherence FLOAT,
    overall_ai_score FLOAT,
    overall_manual_score FLOAT,
    final_score FLOAT,
    ai_analysis_summary TEXT,
    interviewer_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transcript entries table
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

-- Emotion logs table
CREATE TABLE IF NOT EXISTS emotion_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    timestamp FLOAT NOT NULL,
    facial_emotion VARCHAR(50),
    facial_confidence FLOAT,
    speech_emotion VARCHAR(50),
    speech_confidence FLOAT,
    emotion_scores JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_interview (interview_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, full_name, hashed_password, role, is_active) 
VALUES (
    'admin',
    'admin@abis.local',
    'Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5PLP.peWYOeXC',
    'admin',
    TRUE
) ON DUPLICATE KEY UPDATE username=username;

-- Insert sample interviewer (password: interviewer123)
INSERT INTO users (username, email, full_name, hashed_password, role, is_active) 
VALUES (
    'interviewer1',
    'interviewer1@abis.local',
    'Pewawancara Satu',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn98vJ5KP8RXQ6zPJnZZQF3lYpxC',
    'interviewer',
    TRUE
) ON DUPLICATE KEY UPDATE username=username;
