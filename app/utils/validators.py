import re
from typing import Optional
from PIL import Image
import io
from app.core.config import settings
from app.utils.logger import logger

def validate_email(email: str) -> bool:
    """Email formatını doğrula."""
    try:
        # Email formatı kontrolü
        if '@' not in email or '.' not in email:
            return False
        
        # Uzunluk kontrolü
        if len(email) > 255:
            return False
        
        # Domain kontrolü
        domain = email.split('@')[1]
        if '.' not in domain:
            return False
        
        return True
    except Exception as e:
        logger.error(f"Email doğrulama hatası: {str(e)}")
        return False

def validate_student_number(student_number: str) -> bool:
    """Öğrenci numarası formatı doğrulama."""
    pattern = r'^\d{8}$'  # 8 haneli sayı
    return bool(re.match(pattern, student_number))

def validate_image(image_data: bytes) -> bool:
    """Görüntü formatını ve boyutunu doğrula."""
    try:
        # Görüntüyü yükle
        image = Image.open(io.BytesIO(image_data))
        
        # Format kontrolü
        if image.format not in ['JPEG', 'PNG']:
            logger.warning("Desteklenmeyen görüntü formatı")
            return False
        
        # Boyut kontrolü
        if image.size[0] > settings.MAX_IMAGE_SIZE or image.size[1] > settings.MAX_IMAGE_SIZE:
            logger.warning("Görüntü boyutu çok büyük")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Görüntü doğrulama hatası: {str(e)}")
        return False

def validate_schedule(schedule: dict) -> bool:
    """Ders programı formatını doğrula."""
    try:
        valid_days = [
            'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday'
        ]
        
        # Gün kontrolü
        for day in schedule.keys():
            if day.lower() not in valid_days:
                logger.warning(f"Geçersiz gün: {day}")
                return False
        
        # Saat formatı kontrolü
        for times in schedule.values():
            if not isinstance(times, list):
                logger.warning("Saat listesi geçersiz format")
                return False
            
            for time in times:
                if not isinstance(time, str):
                    logger.warning("Saat değeri string olmalı")
                    return False
                
                try:
                    start, end = time.split('-')
                    datetime.strptime(start.strip(), '%H:%M')
                    datetime.strptime(end.strip(), '%H:%M')
                except ValueError:
                    logger.warning("Geçersiz saat formatı")
                    return False
        
        return True
    except Exception as e:
        logger.error(f"Program doğrulama hatası: {str(e)}")
        return False

def validate_password(password: str) -> Optional[str]:
    """Şifre gücünü kontrol et."""
    try:
        if len(password) < 8:
            return "Şifre en az 8 karakter olmalı"
        
        if not any(c.isupper() for c in password):
            return "Şifre en az bir büyük harf içermeli"
        
        if not any(c.islower() for c in password):
            return "Şifre en az bir küçük harf içermeli"
        
        if not any(c.isdigit() for c in password):
            return "Şifre en az bir rakam içermeli"
        
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            return "Şifre en az bir özel karakter içermeli"
        
        return None
    except Exception as e:
        logger.error(f"Şifre doğrulama hatası: {str(e)}")
        return "Şifre doğrulanamadı" 