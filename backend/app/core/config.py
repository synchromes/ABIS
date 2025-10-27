from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "ABIS Interview Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "abis_interview"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    ENCRYPTION_KEY: str
    
    CORS_ORIGINS: str = "http://localhost:3000"
    
    UPLOAD_DIR: str = "./storage/uploads"
    RECORDINGS_DIR: str = "./storage/recordings"
    REPORTS_DIR: str = "./storage/reports"
    MODELS_DIR: str = "./ml_models"
    
    WHISPER_MODEL: str = "base"  # Base model with GPU is faster than tiny on CPU
    WHISPER_DEVICE: str = "cuda"  # Use GPU for 10x speed boost with RTX 2050
    WHISPER_LANGUAGE: str = "id"
    
    MAX_WEBSOCKET_CONNECTIONS: int = 10
    VIDEO_FRAME_RATE: int = 5
    AUDIO_SAMPLE_RATE: int = 16000
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
