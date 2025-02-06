from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, students, teachers, attendance, reports

def create_app() -> FastAPI:
    """Uygulama oluştur."""
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
    )

    # CORS ayarları
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API router'ları ekle
    app.include_router(
        auth.router,
        prefix=f"{settings.API_PREFIX}/auth",
        tags=["authentication"]
    )
    app.include_router(
        students.router,
        prefix=f"{settings.API_PREFIX}/students",
        tags=["students"]
    )
    app.include_router(
        teachers.router,
        prefix=f"{settings.API_PREFIX}/teachers",
        tags=["teachers"]
    )
    app.include_router(
        attendance.router,
        prefix=f"{settings.API_PREFIX}/attendance",
        tags=["attendance"]
    )
    app.include_router(
        reports.router,
        prefix=f"{settings.API_PREFIX}/reports",
        tags=["reports"]
    )

    return app 