from typing import Optional, List, Annotated
from pydantic import BaseModel, StringConstraints
from .user import UserInDB

class TeacherBase(BaseModel):
    """Temel öğretmen şeması."""
    department: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    title: Annotated[str, StringConstraints(min_length=2, max_length=50)]

class TeacherCreate(TeacherBase):
    """Öğretmen oluşturma şeması."""
    user_id: int

class TeacherUpdate(BaseModel):
    """Öğretmen güncelleme şeması."""
    department: Optional[str] = None
    title: Optional[str] = None

class TeacherInDB(TeacherBase):
    """Veritabanı öğretmen şeması."""
    id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }

class TeacherResponse(TeacherInDB):
    """Öğretmen yanıt şeması."""
    user: UserInDB
    courses: List["CourseInDB"] = []  # Forward reference kullanıyoruz

from .course import CourseInDB  # Döngüsel import'u önlemek için en sona taşıdık 