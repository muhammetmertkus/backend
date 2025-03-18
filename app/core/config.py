import os
from pathlib import Path

class Config:
    """Uygulama ayarları."""
    # Temel ayarlar
    APP_NAME = "Yüz Tanıma ile Yoklama Sistemi"
    ENVIRONMENT = "development"
    DEBUG = True
    API_PREFIX = "/api"
    
    # Güvenlik
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "gizli_anahtar_buraya")
    JWT_ACCESS_TOKEN_EXPIRES = 30 * 60  # 30 dakika (saniye cinsinden)
    JWT_ALGORITHM = "HS256"
    
    # Veritabanı - SQLite veya PostgreSQL
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/attendance.db")
    
    # Heroku PostgreSQL için SSL sertifikası doğrulama ayarı
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
    
    # Yüz tanıma
    MIN_FACE_CONFIDENCE = float(os.getenv("MIN_FACE_CONFIDENCE", 0.6))
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 800))
    FACE_DETECTION_MODEL = os.getenv("FACE_DETECTION_MODEL", "hog")
    
    # Loglama
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    
    # Dosya Yükleme
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Port ayarı (Heroku için)
    PORT = int(os.getenv("PORT", 8000))

class DevelopmentConfig(Config):
    """Geliştirme ortamı ayarları."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Üretim ortamı ayarları."""
    DEBUG = False
    ENVIRONMENT = "production"
    # Üretim ortamında daha güvenli ayarlar kullanılmalı
    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60  # 15 dakika
    
class TestingConfig(Config):
    """Test ortamı ayarları."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
# Ortama göre doğru yapılandırmayı seç
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

# Varsayılan yapılandırma
config = config_by_name[os.getenv("FLASK_ENV", "development")] 