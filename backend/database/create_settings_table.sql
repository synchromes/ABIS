-- Create settings table for application-wide configurations
-- Allows admin to configure AI vs Manual scoring weights

CREATE TABLE IF NOT EXISTS app_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert default scoring weights
INSERT INTO app_settings (setting_key, setting_value, description) VALUES
('ai_score_weight', '60', 'Persentase bobot penilaian AI (0-100)'),
('manual_score_weight', '40', 'Persentase bobot penilaian manual (0-100)')
ON DUPLICATE KEY UPDATE setting_value = setting_value;

-- Create index for faster lookups
CREATE INDEX idx_setting_key ON app_settings(setting_key);
