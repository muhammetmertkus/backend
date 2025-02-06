from typing import Optional, List
from pydantic import BaseModel, constr
from .user import UserInDB
from .course import CourseInDB

class TeacherBase(BaseModel):
    """Temel öğretmen şeması."""
    department: constr(min_length=2, max_length=100)
    title: constr(min_length=2, max_length=50)

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

    class Config:
        orm_mode = True

class TeacherResponse(TeacherInDB):
    """Öğretmen yanıt şeması."""
    user: UserInDB
    courses: List[CourseInDB] = [] 