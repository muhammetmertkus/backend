from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Teacher(Base):
    """Öğretmen modeli."""
    user_id = Column(ForeignKey("user.id"), nullable=False, unique=True)
    department = Column(String(100), nullable=False)
    title = Column(String(50), nullable=False)

    # İlişkiler
    user = relationship("User", backref="teacher", uselist=False)
    courses = relationship("Course", back_populates="teacher")

    def __repr__(self) -> str:
        return f"<Teacher {self.user.name} {self.user.surname}>" 