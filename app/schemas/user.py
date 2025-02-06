from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from app.models.user import UserRole
from .base import BaseSchema

class UserBase(BaseModel):
    """Temel kullanıcı şeması."""
    email: EmailStr
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    role: str

class UserCreate(UserBase):
    """Kullanıcı oluşturma şeması."""
    password: constr(min_length=8, max_length=50)

class UserUpdate(BaseModel):
    """Kullanıcı güncelleme şeması."""
    email: Optional[EmailStr] = None
    name: Optional[constr(min_length=2, max_length=50)] = None
    surname: Optional[constr(min_length=2, max_length=50)] = None
    password: Optional[constr(min_length=8, max_length=50)] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """Veritabanı kullanıcı şeması."""
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class UserResponse(UserInDB):
    """API yanıtı için kullanıcı şeması."""
    pass

class UserLogin(BaseModel):
    """Kullanıcı girişi şeması."""
    email: EmailStr
    password: str 