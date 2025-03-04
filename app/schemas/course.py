from typing import Optional, List, Dict, Annotated
from pydantic import BaseModel, StringConstraints
from datetime import datetime
from .teacher import TeacherResponse

class CourseBase(BaseModel):
    """Temel ders şeması."""
    code: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    name: Annotated[str, StringConstraints(min_length=3, max_length=100)]
    semester: Annotated[str, StringConstraints(min_length=3, max_length=20)]
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

    model_config = {
        "from_attributes": True
    }

class CourseResponse(CourseInDB):
    """Ders yanıt şeması."""
    teacher: TeacherResponse 