from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, confloat
from .base import BaseSchema
from app.models.attendance import AttendanceType

class AttendanceBase(BaseModel):
    """Temel yoklama şeması."""
    course_id: int
    date: datetime
    type: str

class AttendanceCreate(AttendanceBase):
    """Yoklama oluşturma şeması."""
    created_by: int
    photo_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AttendanceUpdate(BaseModel):
    """Yoklama güncelleme şeması."""
    date: Optional[datetime] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AttendanceDetailBase(BaseModel):
    """Temel yoklama detay şeması."""
    student_id: int
    status: bool = False
    confidence: Optional[confloat(ge=0, le=1)] = None
    emotion_data: Optional[Dict[str, Any]] = None

class AttendanceDetailCreate(AttendanceDetailBase):
    """Yoklama detay oluşturma şeması."""
    attendance_id: int

class AttendanceDetailInDB(AttendanceDetailBase):
    """Veritabanı yoklama detay şeması."""
    id: int
    attendance_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AttendanceInDB(AttendanceBase):
    """Veritabanı yoklama şeması."""
    id: int
    created_by: int
    photo_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AttendanceResponse(AttendanceInDB):
    """Yoklama yanıt şeması."""
    details: List[AttendanceDetailInDB] = [] 