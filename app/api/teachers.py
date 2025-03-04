from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.teacher import Teacher
from app.schemas.teacher import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse
)
from app.schemas.course import CourseResponse
from app.api.dependencies import get_current_admin_user
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[TeacherResponse])
def get_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """Öğretmen listesini getir."""
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers

@router.post("/", response_model=TeacherResponse)
def create_teacher(
    teacher_in: TeacherCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """Yeni öğretmen oluştur."""
    # Kullanıcı kontrolü
    user = db.query(User).filter(User.id == teacher_in.user_id).first()
    if not user or user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz kullanıcı"
        )
    
    # Öğretmen zaten var mı kontrolü
    if db.query(Teacher).filter(Teacher.user_id == teacher_in.user_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı zaten öğretmen olarak kayıtlı"
        )
    
    teacher = Teacher(**teacher_in.dict())
    
    try:
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        logger.info(f"Yeni öğretmen oluşturuldu: {teacher.user.email}")
        return teacher
    except Exception as e:
        logger.error(f"Öğretmen oluşturma hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Öğretmen oluşturulamadı"
        )

@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Öğretmen detaylarını getir."""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğretmen bulunamadı"
        )
    return teacher

@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher_in: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """Öğretmen bilgilerini güncelle."""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğretmen bulunamadı"
        )
    
    for field, value in teacher_in.dict(exclude_unset=True).items():
        setattr(teacher, field, value)
    
    try:
        db.commit()
        db.refresh(teacher)
        logger.info(f"Öğretmen güncellendi: {teacher.user.email}")
        return teacher
    except Exception as e:
        logger.error(f"Öğretmen güncelleme hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Öğretmen güncellenemedi"
        )

@router.get("/{teacher_id}/courses", response_model=List[CourseResponse])
def get_teacher_courses(
    teacher_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Öğretmenin derslerini getir."""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğretmen bulunamadı"
        )
    return teacher.courses 