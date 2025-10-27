"""
Fix database schema for ABIS
Run this script to recreate interview_scores table with correct columns
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

def fix_database():
    """Recreate interview_scores table with correct schema"""
    
    print("[INFO] Fixing database schema...")
    print("[WARNING] This will drop and recreate interview_scores table!")
    print("          All existing score data will be LOST!")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("[CANCELLED] Operation cancelled.")
        return
    
    print()
    print("[PROGRESS] Recreating interview_scores table...")
    
    sql = """
    DROP TABLE IF EXISTS interview_scores;
    
    CREATE TABLE interview_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        interview_id INT NOT NULL UNIQUE,
        
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
        
        emotion_stability FLOAT DEFAULT NULL,
        speech_clarity FLOAT DEFAULT NULL,
        answer_coherence FLOAT DEFAULT NULL,
        
        overall_ai_score FLOAT DEFAULT NULL,
        overall_manual_score FLOAT DEFAULT NULL,
        final_score FLOAT DEFAULT NULL,
        
        ai_analysis_summary TEXT DEFAULT NULL,
        interviewer_notes TEXT DEFAULT NULL,
        
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        CONSTRAINT fk_interview_scores_interview 
            FOREIGN KEY (interview_id) 
            REFERENCES interviews(id) 
            ON DELETE CASCADE,
            
        INDEX idx_interview_id (interview_id),
        INDEX idx_final_score (final_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        with engine.connect() as connection:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            
            for stmt in statements:
                connection.execute(text(stmt))
                connection.commit()
        
        print("[SUCCESS] Database schema fixed successfully!")
        print()
        print("[CHANGES] Made:")
        print("  - Dropped old interview_scores table")
        print("  - Created new interview_scores table with:")
        print("    * All behavioral score columns (AI + Manual)")
        print("    * Performance metrics (emotion, speech, coherence)")
        print("    * Overall scores (AI, Manual, Final)")
        print("    * Analysis text fields")
        print("    * Proper indexes and foreign keys")
        print()
        print("[READY] You can now create interviews without errors!")
        
    except Exception as e:
        print(f"[ERROR] Error fixing database: {e}")
        print()
        print("[TIP] Try running the SQL manually in phpMyAdmin:")
        print(f"      File: {Path(__file__).parent / 'fix_database_schema.sql'}")
        sys.exit(1)

if __name__ == "__main__":
    fix_database()
