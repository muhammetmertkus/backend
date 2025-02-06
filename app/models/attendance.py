from enum import Enum
from sqlalchemy import Boolean, Column, Float, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class AttendanceType(str, Enum):
    """Yoklama türleri."""
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    FACE = "FACE"

class Attendance(Base):
    """Yoklama modeli."""
    course_id = Column(ForeignKey("course.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    type = Column(String(20), nullable=False)
    photo_url = Column(String(255), nullable=True)
    metadata = Column(Text, nullable=True)  # JSON olarak saklanacak
    created_by = Column(ForeignKey("user.id"), nullable=False)

    # İlişkiler
    course = relationship("Course", back_populates="attendance_records")
    details = relationship("AttendanceDetail", back_populates="attendance")
    creator = relationship("User")

    def __repr__(self) -> str:
        return f"<Attendance {self.course.code} {self.date}>"

class AttendanceDetail(Base):
    """Yoklama detay modeli."""
    attendance_id = Column(ForeignKey("attendance.id"), nullable=False)
    student_id = Column(ForeignKey("student.id"), nullable=False)
    status = Column(Boolean, default=False)
    emotion_data = Column(Text, nullable=True)  # JSON olarak saklanacak
    confidence = Column(Float, nullable=True)

    # İlişkiler
    attendance = relationship("Attendance", back_populates="details")
    student = relationship("Student", back_populates="attendance_details")

    def __repr__(self) -> str:
        return f"<AttendanceDetail {self.student.student_number}>" 