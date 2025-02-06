from typing import Optional
from pydantic import BaseModel, confloat
from datetime import datetime

class EmotionBase(BaseModel):
    """Temel duygu şeması."""
    student_id: int
    course_id: int
    emotion: str
    confidence: confloat(ge=0, le=1)
    date: datetime

class EmotionCreate(EmotionBase):
    """Duygu kaydı oluşturma şeması."""
    pass

class EmotionInDB(EmotionBase):
    """Veritabanı duygu şeması."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 