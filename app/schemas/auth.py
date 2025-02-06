from typing import Optional
from pydantic import BaseModel, EmailStr, constr

class Token(BaseModel):
    """Token şeması."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token veri şeması."""
    email: Optional[str] = None
    role: Optional[str] = None

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

class UserResponse(UserBase):
    """Kullanıcı yanıt şeması."""
    id: int
    is_active: bool

    class Config:
        orm_mode = True 