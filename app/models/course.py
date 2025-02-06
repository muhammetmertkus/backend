from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Course(Base):
    """Ders modeli."""
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(ForeignKey("teacher.id"), nullable=False)
    semester = Column(String(20), nullable=False)
    schedule = Column(Text, nullable=True)  # JSON olarak saklanacak

    # İlişkiler
    teacher = relationship("Teacher", back_populates="courses")
    attendance_records = relationship("Attendance", back_populates="course")
    emotion_records = relationship("EmotionHistory", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course {self.code}>" 