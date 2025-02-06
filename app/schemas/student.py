from typing import Optional
from pydantic import BaseModel, constr
from .user import UserInDB

class StudentBase(BaseModel):
    """Temel öğrenci şeması."""
    student_number: constr(min_length=5, max_length=20)
    department: constr(min_length=2, max_length=100)

class StudentCreate(StudentBase):
    """Öğrenci oluşturma şeması."""
    user_id: int

class StudentUpdate(BaseModel):
    """Öğrenci güncelleme şeması."""
    department: Optional[str] = None
    face_photo_url: Optional[str] = None

class StudentInDB(StudentBase):
    """Veritabanı öğrenci şeması."""
    id: int
    user_id: int
    face_photo_url: Optional[str] = None

    class Config:
        orm_mode = True

class StudentResponse(StudentInDB):
    """Öğrenci yanıt şeması."""
    user: UserInDB 