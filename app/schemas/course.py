from typing import Optional, List, Dict
from pydantic import BaseModel, constr
from datetime import datetime

class CourseBase(BaseModel):
    """Temel ders şeması."""
    code: constr(min_length=3, max_length=20)
    name: constr(min_length=3, max_length=100)
    semester: constr(min_length=3, max_length=20)
    schedule: Optional[Dict[str, List[str]]] = None

class CourseCreate(CourseBase):
    """Ders oluşturma şeması."""
    teacher_id: int

class CourseUpdate(BaseModel):
    """Ders güncelleme şeması."""
    name: Optional[str] = None
    semester: Optional[str] = None
    schedule: Optional[Dict[str, List[str]]] = None

class CourseInDB(CourseBase):
    """Veritabanı ders şeması."""
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 