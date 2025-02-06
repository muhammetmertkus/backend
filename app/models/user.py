from enum import Enum
from sqlalchemy import Boolean, Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import Base

class UserRole(str, Enum):
    """Kullanıcı rolleri."""
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"

class User(Base):
    """Kullanıcı modeli."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)

    # İlişkiler
    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>" 