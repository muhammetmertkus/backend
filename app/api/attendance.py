from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.attendance import Attendance, AttendanceType
from app.schemas.attendance import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    AttendanceDetailCreate
)
from app.services.attendance_service import AttendanceService
from app.services.email_service import EmailService
from app.utils.logger import logger

router = APIRouter()

@router.post("/face", response_model=dict)
async def create_face_attendance(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Any:
    """Yüz tanıma ile yoklama al."""
    try:
        # Servisleri başlat
        attendance_service = AttendanceService(db)
        email_service = EmailService()
        
        # Görüntüyü oku
        image_data = await file.read()
        
        # Öğrencileri getir
        students = db.query(Student).filter(
            Student.face_encodings.isnot(None)
        ).all()
        known_students = [
            {
                'id': s.id,
                'face_encodings': s.face_encodings,
                'email': s.user.email
            } for s in students
        ]
        
        # Yoklama işlemini gerçekleştir
        result = await attendance_service.process_attendance_image(
            course_id,
            image_data,
            known_students
        )
        
        # Email bildirimleri gönder
        if 'results' in result:
            notifications = []
            course = db.query(Course).filter(Course.id == course_id).first()
            
            for student_result in result['results']:
                notifications.append({
                    'email': next(
                        s['email'] for s in known_students 
                        if s['id'] == student_result['student_id']
                    ),
                    'course_name': course.name,
                    'status': True
                })
            
            email_service.send_bulk_attendance_notification(notifications)
        
        return result
    except Exception as e:
        logger.error(f"Yoklama alma hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yoklama alınırken bir hata oluştu"
        )

@router.post("/manual", response_model=AttendanceResponse)
def create_manual_attendance(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Manuel yoklama kaydı oluştur."""
    attendance_service = AttendanceService(db)
    attendance = attendance_service.create_attendance(attendance_in)
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yoklama kaydı oluşturulamadı"
        )
    
    return attendance

@router.get("/course/{course_id}", response_model=List[AttendanceResponse])
def get_course_attendance(
    course_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """Ders yoklamalarını getir."""
    attendance_records = db.query(Attendance).filter(
        Attendance.course_id == course_id
    ).offset(skip).limit(limit).all()
    
    return attendance_records

@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Yoklama detaylarını getir."""
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yoklama kaydı bulunamadı"
        )
    
    return attendance

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """Yoklama kaydını güncelle."""
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yoklama kaydı bulunamadı"
        )
    
    for field, value in attendance_in.dict(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.commit()
    db.refresh(attendance)
    return attendance 