from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.course import Course
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse
)
from app.api.dependencies import get_current_teacher_user
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
def get_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """Ders listesini getir."""
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.post("/", response_model=CourseResponse)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_teacher_user)
) -> Any:
    """Yeni ders oluştur."""
    # Ders kodu kontrolü
    if db.query(Course).filter(Course.code == course_in.code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu ders kodu zaten kullanılıyor"
        )
    
    course = Course(**course_in.dict())
    
    try:
        db.add(course)
        db.commit()
        db.refresh(course)
        logger.info(f"Yeni ders oluşturuldu: {course.code}")
        return course
    except Exception as e:
        logger.error(f"Ders oluşturma hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ders oluşturulamadı"
        )

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Ders detaylarını getir."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ders bulunamadı"
        )
    return course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_teacher_user)
) -> Any:
    """Ders bilgilerini güncelle."""
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
            detail="Bu dersi güncelleme yetkiniz yok"
        )
    
    for field, value in course_in.dict(exclude_unset=True).items():
        setattr(course, field, value)
    
    try:
        db.commit()
        db.refresh(course)
        logger.info(f"Ders güncellendi: {course.code}")
        return course
    except Exception as e:
        logger.error(f"Ders güncelleme hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ders güncellenemedi"
        )

@router.get("/{course_id}/attendance", response_model=List[AttendanceResponse])
def get_course_attendance(
    course_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_teacher_user)
) -> Any:
    """Ders yoklamalarını getir."""
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
            detail="Bu dersin yoklamalarını görüntüleme yetkiniz yok"
        )
    
    return course.attendance_records[skip:skip + limit] 