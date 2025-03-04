from typing import Optional, Annotated
from pydantic import BaseModel, StringConstraints
from .user import UserInDB

class StudentBase(BaseModel):
    """Temel öğrenci şeması."""
    student_number: Annotated[str, StringConstraints(min_length=5, max_length=20)]
    department: Annotated[str, StringConstraints(min_length=2, max_length=100)]

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

    model_config = {
        "from_attributes": True
    }

class StudentResponse(StudentInDB):
    """Öğrenci yanıt şeması."""
    user: UserInDB 