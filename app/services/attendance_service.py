from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.attendance import Attendance, AttendanceDetail, AttendanceType
from app.models.course import Course
from app.models.student import Student
from app.schemas.attendance import AttendanceCreate, AttendanceDetailCreate
from app.services.face_service import FaceService
from app.services.emotion_service import EmotionService
from app.utils.logger import logger

class AttendanceService:
    """Yoklama servisi."""

    def __init__(self, db: Session):
        self.db = db
        self.face_service = FaceService()
        self.emotion_service = EmotionService()

    def create_attendance(self, attendance_in: AttendanceCreate) -> Optional[Attendance]:
        """Yoklama kaydı oluştur."""
        try:
            attendance = Attendance(
                course_id=attendance_in.course_id,
                date=attendance_in.date,
                type=attendance_in.type,
                photo_url=attendance_in.photo_url,
                metadata=attendance_in.metadata,
                created_by=attendance_in.created_by
            )
            
            self.db.add(attendance)
            self.db.commit()
            self.db.refresh(attendance)
            
            return attendance
        except Exception as e:
            logger.error(f"Yoklama oluşturma hatası: {str(e)}")
            self.db.rollback()
            return None

    def create_attendance_detail(
        self, 
        data: AttendanceDetailCreate
    ) -> Optional[AttendanceDetail]:
        """Yoklama detayı oluştur."""
        try:
            detail = AttendanceDetail(
                attendance_id=data.attendance_id,
                student_id=data.student_id,
                status=data.status,
                emotion_data=data.emotion_data,
                confidence=data.confidence
            )
            
            self.db.add(detail)
            self.db.commit()
            self.db.refresh(detail)
            
            return detail
        except Exception as e:
            self.db.rollback()
            logger.error(f"Yoklama detayı oluşturma hatası: {str(e)}")
            return None

    async def process_attendance_image(
        self,
        course_id: int,
        image_data: bytes,
        known_students: List[Dict]
    ) -> Dict:
        """Görüntüden yoklama al."""
        try:
            # Yüzleri tespit et
            face_locations, face_encodings = self.face_service.detect_faces(image_data)
            
            if not face_encodings:
                return {"error": "Görüntüde yüz bulunamadı"}
            
            # Yoklama kaydı oluştur
            attendance = self.create_attendance(
                AttendanceCreate(
                    course_id=course_id,
                    date=datetime.utcnow(),
                    type="FACE",
                    photo_url=None,  # Fotoğraf kaydedilecek
                    created_by=1  # Sistem kullanıcısı
                )
            )
            
            if not attendance:
                return {"error": "Yoklama kaydı oluşturulamadı"}
            
            # Her yüz için öğrenci eşleştirmesi yap
            results = []
            for encoding in face_encodings:
                match = self.face_service.find_matching_student(encoding, known_students)
                if match:
                    # Duygu analizi yap
                    emotion_result = self.emotion_service.analyze_emotion(image_data)
                    
                    # Yoklama detayı oluştur
                    detail = AttendanceDetail(
                        attendance_id=attendance.id,
                        student_id=match['student_id'],
                        status=True,
                        confidence=match['confidence'],
                        emotion_data=emotion_result
                    )
                    
                    self.db.add(detail)
                    results.append({
                        'student_id': match['student_id'],
                        'confidence': match['confidence'],
                        'emotion': emotion_result
                    })
            
            self.db.commit()
            
            return {
                'attendance_id': attendance.id,
                'total_faces': len(face_encodings),
                'matched_students': len(results),
                'results': results
            }
        except Exception as e:
            logger.error(f"Görüntü işleme hatası: {str(e)}")
            self.db.rollback()
            return {"error": str(e)} 