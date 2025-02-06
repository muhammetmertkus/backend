from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app: FastAPI) -> None:
    """CORS yapılandırması."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Production'da spesifik domainler belirtilmeli
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

def setup_middleware(app: FastAPI) -> None:
    """Tüm middleware'leri yapılandır."""
    setup_cors(app)
    
    # Rate limiting middleware
    # TODO: Rate limiting eklenecek
    
    # Security headers middleware
    # TODO: Güvenlik başlıkları eklenecek 