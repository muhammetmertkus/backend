from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import setup_middleware
from app.api import (
    auth,
    students,
    teachers,
    courses,
    attendance,
    reports
)
from app.utils.logger import logger

def create_app() -> FastAPI:
    """FastAPI uygulamasını oluştur."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Yüz Tanıma ile Yoklama Sistemi API",
        version="1.0.0",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json"
    )
    
    # Middleware'leri yapılandır
    setup_middleware(app)
    
    # API router'larını ekle
    app.include_router(
        auth.router,
        prefix=f"{settings.API_PREFIX}/auth",
        tags=["Authentication"]
    )
    app.include_router(
        students.router,
        prefix=f"{settings.API_PREFIX}/students",
        tags=["Students"]
    )
    app.include_router(
        teachers.router,
        prefix=f"{settings.API_PREFIX}/teachers",
        tags=["Teachers"]
    )
    app.include_router(
        courses.router,
        prefix=f"{settings.API_PREFIX}/courses",
        tags=["Courses"]
    )
    app.include_router(
        attendance.router,
        prefix=f"{settings.API_PREFIX}/attendance",
        tags=["Attendance"]
    )
    app.include_router(
        reports.router,
        prefix=f"{settings.API_PREFIX}/reports",
        tags=["Reports"]
    )
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Uygulama başlatıldı")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Uygulama kapatıldı")
    
    return app 