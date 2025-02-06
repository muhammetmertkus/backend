from sqlalchemy import Column, Float, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class EmotionHistory(Base):
    """Duygu geçmişi modeli."""
    student_id = Column(ForeignKey("student.id"), nullable=False)
    course_id = Column(ForeignKey("course.id"), nullable=False)
    emotion = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

    # İlişkiler
    student = relationship("Student", back_populates="emotion_history")
    course = relationship("Course", back_populates="emotion_records")

    def __repr__(self) -> str:
        return f"<EmotionHistory {self.student.student_number} {self.emotion}>" 