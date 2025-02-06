from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.attendance import Attendance, AttendanceDetail
from app.models.course import Course
from app.models.emotion import EmotionHistory
from app.models.student import Student
from app.api.dependencies import get_current_teacher_user
from app.services.emotion_service import EmotionService
from app.utils.logger import logger

router = APIRouter()

@router.get("/attendance/daily")
def get_daily_attendance_report(
    course_id: int = None,
    date: datetime = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_teacher_user)
) -> Dict:
    """Günlük yoklama raporu."""
    try:
        # Tarih belirtilmemişse bugünü kullan
        if not date:
            date = datetime.utcnow().date()
        
        # Sorguyu oluştur
        query = db.query(Attendance).filter(
            func.date(Attendance.date) == date
        )
        
        # Ders filtrelemesi
        if course_id:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ders bulunamadı"
                )
            
            # Yetki kontrolü
            if course.teacher_id != current_user.teacher.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bu dersin raporlarını görüntüleme yetkiniz yok"
                )
            
            query = query.filter(Attendance.course_id == course_id)
        
        # Yoklamaları getir
        attendance_records = query.all()
        
        # İstatistikleri hesapla
        total_students = db.query(Student).count()
        present_students = db.query(AttendanceDetail).filter(
            AttendanceDetail.attendance_id.in_([a.id for a in attendance_records]),
            AttendanceDetail.status == True
        ).count()
        
        return {
            'date': date,
            'total_students': total_students,
            'present_students': present_students,
            'attendance_rate': present_students / total_students if total_students > 0 else 0,
            'details': [
                {
                    'course': a.course.name,
                    'time': a.date.time(),
                    'type': a.type,
                    'present_count': len([d for d in a.details if d.status])
                } for a in attendance_records
            ]
        }
    except Exception as e:
        logger.error(f"Günlük rapor hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rapor oluşturulurken bir hata oluştu"
        )

@router.get("/emotions/course/{course_id}")
def get_course_emotion_report(
    course_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_teacher_user)
) -> Dict:
    """Ders duygu analizi raporu."""
    try:
        # Ders kontrolü
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ders bulunamadı"
            )
        
        # Yetki kontrolü
        if course.teacher_id != current_user.teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu dersin raporlarını görüntüleme yetkiniz yok"
            )
        
        # Tarih aralığı belirtilmemişse son 30 günü kullan
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Duygu kayıtlarını getir
        emotions = db.query(EmotionHistory).filter(
            EmotionHistory.course_id == course_id,
            EmotionHistory.date.between(start_date, end_date)
        ).all()
        
        # Duygu istatistiklerini hesapla
        emotion_service = EmotionService()
        emotion_stats = emotion_service.calculate_emotion_stats([
            {'dominant_emotion': e.emotion, 'confidence': e.confidence}
            for e in emotions
        ])
        
        return {
            'course_name': course.name,
            'start_date': start_date,
            'end_date': end_date,
            'total_records': len(emotions),
            'emotion_stats': emotion_stats
        }
    except Exception as e:
        logger.error(f"Duygu raporu hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rapor oluşturulurken bir hata oluştu"
        )

@router.get("/attendance/student/{student_id}")
def get_student_attendance_report(
    student_id: int,
    course_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_teacher_user)
) -> Dict:
    """Öğrenci yoklama raporu."""
    try:
        # Öğrenci kontrolü
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Öğrenci bulunamadı"
            )
        
        # Tarih aralığı belirtilmemişse son 30 günü kullan
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Yoklama kayıtlarını getir
        query = db.query(AttendanceDetail).join(Attendance).filter(
            AttendanceDetail.student_id == student_id,
            Attendance.date.between(start_date, end_date)
        )
        
        # Ders filtrelemesi
        if course_id:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ders bulunamadı"
                )
            
            # Yetki kontrolü
            if course.teacher_id != current_user.teacher.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bu dersin raporlarını görüntüleme yetkiniz yok"
                )
            
            query = query.filter(Attendance.course_id == course_id)
        
        attendance_records = query.all()
        
        # Duygu kayıtlarını getir
        emotions = [
            {'dominant_emotion': a.emotion_data['dominant_emotion']}
            for a in attendance_records
            if a.emotion_data and 'dominant_emotion' in a.emotion_data
        ]
        
        # Duygu istatistiklerini hesapla
        emotion_service = EmotionService()
        emotion_stats = emotion_service.calculate_emotion_stats(emotions)
        
        return {
            'student_name': f"{student.user.name} {student.user.surname}",
            'student_number': student.student_number,
            'start_date': start_date,
            'end_date': end_date,
            'total_attendance': len(attendance_records),
            'attendance_rate': len([a for a in attendance_records if a.status]) / len(attendance_records) if attendance_records else 0,
            'emotion_stats': emotion_stats,
            'details': [
                {
                    'date': a.attendance.date,
                    'course': a.attendance.course.name,
                    'status': a.status,
                    'confidence': a.confidence,
                    'emotion_data': a.emotion_data
                } for a in attendance_records
            ]
        }
    except Exception as e:
        logger.error(f"Öğrenci raporu hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rapor oluşturulurken bir hata oluştu"
        ) 