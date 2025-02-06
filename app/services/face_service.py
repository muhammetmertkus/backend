import face_recognition
import numpy as np
from typing import List, Optional, Tuple, Dict
from PIL import Image
import io
from app.core.config import settings
from app.utils.logger import logger

class FaceService:
    """Yüz tanıma servisi."""

    def detect_faces(self, image_data: bytes) -> Tuple[List[List[int]], List[List[float]]]:
        """Görüntüdeki yüzleri tespit et."""
        try:
            # Görüntüyü yükle
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            
            # Yüz konumlarını bul
            face_locations = face_recognition.face_locations(
                image,
                model=settings.FACE_DETECTION_MODEL
            )
            
            # Yüz kodlamalarını hesapla
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return face_locations, face_encodings
        except Exception as e:
            logger.error(f"Yüz tespiti hatası: {str(e)}")
            return [], []

    def compare_faces(
        self,
        known_encoding: List[float],
        unknown_encoding: List[float],
        tolerance: float = 0.6
    ) -> Tuple[bool, float]:
        """İki yüz kodlamasını karşılaştır."""
        try:
            # Numpy dizilerine dönüştür
            known = np.array(known_encoding)
            unknown = np.array(unknown_encoding)
            
            # Öklid mesafesini hesapla
            distance = np.linalg.norm(known - unknown)
            
            # Mesafeyi 0-1 arasına normalize et
            similarity = 1 / (1 + distance)
            
            # Eşleşme kontrolü
            is_match = distance <= tolerance
            
            return is_match, similarity
        except Exception as e:
            logger.error(f"Yüz karşılaştırma hatası: {str(e)}")
            return False, 0.0

    def encode_face(self, image_data: bytes) -> Optional[List[float]]:
        """Görüntüdeki yüzü kodla."""
        try:
            # Görüntüyü yükle ve yüzü kodla
            locations, encodings = self.detect_faces(image_data)
            
            if not encodings:
                return None
            
            return encodings[0].tolist()
        except Exception as e:
            logger.error(f"Yüz kodlama hatası: {str(e)}")
            return None

    def find_matching_student(
        self,
        face_encoding: List[float],
        known_students: List[Dict]
    ) -> Optional[Dict]:
        """Eşleşen öğrenciyi bul."""
        try:
            best_match = None
            best_confidence = 0.0
            
            for student in known_students:
                is_match, confidence = self.compare_faces(
                    student['face_encodings'],
                    face_encoding,
                    tolerance=settings.MIN_FACE_CONFIDENCE
                )
                
                if is_match and confidence > best_confidence:
                    best_match = {
                        'student_id': student['id'],
                        'confidence': confidence
                    }
                    best_confidence = confidence
            
            return best_match
        except Exception as e:
            logger.error(f"Öğrenci eşleştirme hatası: {str(e)}")
            return None 