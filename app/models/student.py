from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Student(Base):
    """Öğrenci modeli."""
    user_id = Column(ForeignKey("user.id"), nullable=False, unique=True)
    student_number = Column(String(20), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False)
    face_encodings = Column(Text, nullable=True)
    face_photo_url = Column(String(255), nullable=True)

    # İlişkiler
    user = relationship("User", backref="student", uselist=False)
    attendance_details = relationship("AttendanceDetail", back_populates="student")
    emotion_history = relationship("EmotionHistory", back_populates="student")

    def __repr__(self) -> str:
        return f"<Student {self.student_number}>" 