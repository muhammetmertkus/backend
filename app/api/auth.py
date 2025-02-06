from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password
)
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserCreate, UserResponse, UserUpdate
from app.api.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Kullanıcı girişi."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı email veya şifre"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Kullanıcı girişi: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Yeni kullanıcı kaydı."""
    # Email kontrolü
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # Şifre hash'leme
    hashed_password = get_password_hash(user_in.password)
    
    # Kullanıcı oluşturma
    user = User(
        email=user_in.email,
        password=hashed_password,
        name=user_in.name,
        surname=user_in.surname,
        role=user_in.role,
        is_active=True
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Yeni kullanıcı kaydı: {user.email}")
        return user
    except Exception as e:
        logger.error(f"Kullanıcı kaydı hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı kaydı oluşturulamadı"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mevcut kullanıcı bilgilerini getir."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mevcut kullanıcı bilgilerini güncelle."""
    if user_in.password:
        current_user.password = get_password_hash(user_in.password)
    
    for field, value in user_in.dict(exclude={'password'}, exclude_unset=True).items():
        setattr(current_user, field, value)
    
    try:
        db.commit()
        db.refresh(current_user)
        logger.info(f"Kullanıcı güncellendi: {current_user.email}")
        return current_user
    except Exception as e:
        logger.error(f"Kullanıcı güncelleme hatası: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı güncellenemedi"
        ) 