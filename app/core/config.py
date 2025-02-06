import os
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Uygulama ayarları."""
    # Temel ayarlar
    APP_NAME: str = "Yüz Tanıma ile Yoklama Sistemi"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # Güvenlik
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY: str = "gizli_anahtar_buraya"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    
    # Veritabanı - SQLite için
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/attendance.db"
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    
    # Yüz tanıma
    MIN_FACE_CONFIDENCE: float = 0.6
    MAX_IMAGE_SIZE: int = 800
    FACE_DETECTION_MODEL: str = "hog"
    
    # Loglama
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Dosya Yükleme
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 