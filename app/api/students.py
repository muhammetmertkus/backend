from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse
)
from app.services.face_service import FaceService
from app.utils.validators import validate_image
from app.utils.logger import logger
from app.api.dependencies import get_current_admin_user, get_current_user

router = APIRouter()
face_service = FaceService()

@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """Tüm öğrencileri listele."""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.post("/", response_model=StudentResponse)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """Yeni öğrenci oluştur."""
    # Kullanıcı kontrolü
    user = db.query(User).filter(User.id == student_in.user_id).first()
    if not user or user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz kullanıcı"
        )
    
    # Öğrenci numarası kontrolü
    existing_student = db.query(Student).filter(
        Student.student_number == student_in.student_number
    ).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu öğrenci numarası zaten kayıtlı"
        )
    
    student = Student(**student_in.dict())
    
    try:
        db.add(student)
        db.commit()
        db.refresh(student)
        logger.info(f"Yeni öğrenci oluşturuldu: {student.student_number}")
        return student
    except Exception as e:
        logger.error(f"Öğrenci oluşturma hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Öğrenci oluşturulamadı"
        )

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Öğrenci detaylarını getir."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğrenci bulunamadı"
        )
    return student

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """Öğrenci bilgilerini güncelle."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğrenci bulunamadı"
        )
    
    for field, value in student_in.dict(exclude_unset=True).items():
        setattr(student, field, value)
    
    try:
        db.commit()
        db.refresh(student)
        logger.info(f"Öğrenci güncellendi: {student.student_number}")
        return student
    except Exception as e:
        logger.error(f"Öğrenci güncelleme hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Öğrenci güncellenemedi"
        )

@router.post("/{student_id}/face", response_model=StudentResponse)
async def upload_face_photo(
    student_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    """Öğrenci yüz fotoğrafı yükle."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğrenci bulunamadı"
        )
    
    try:
        # Görüntüyü doğrula
        image_data = await file.read()
        if not validate_image(image_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz görüntü formatı"
            )
        
        # Yüz özelliklerini çıkar
        face_encoding = face_service.encode_face(image_data)
        if not face_encoding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Görüntüde yüz tespit edilemedi"
            )
        
        # Öğrenci bilgilerini güncelle
        student.face_encodings = face_encoding.tolist()
        student.face_photo_url = f"/uploads/faces/{student_id}.jpg"
        
        db.commit()
        db.refresh(student)
        logger.info(f"Öğrenci yüz fotoğrafı güncellendi: {student.student_number}")
        return student
    except Exception as e:
        logger.error(f"Yüz fotoğrafı yükleme hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yüz fotoğrafı yüklenemedi"
        ) 