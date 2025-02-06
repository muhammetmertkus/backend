import pytest
import numpy as np
from PIL import Image
import io
from app.services.face_service import FaceService

@pytest.fixture
def face_service():
    """Face service fixture."""
    return FaceService()

@pytest.fixture
def test_image():
    """Test görüntüsü oluştur."""
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_detect_faces(face_service, test_image):
    """Yüz tespiti testi."""
    locations, encodings = face_service.detect_faces(test_image)
    assert isinstance(locations, list)
    assert isinstance(encodings, list)

def test_compare_faces(face_service):
    """Yüz karşılaştırma testi."""
    encoding1 = np.random.rand(128)
    encoding2 = np.random.rand(128)
    
    is_match, confidence = face_service.compare_faces(encoding1, encoding2)
    assert isinstance(is_match, bool)
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1

def test_encode_face(face_service, test_image):
    """Yüz kodlama testi."""
    encoding = face_service.encode_face(test_image)
    if encoding is not None:
        assert isinstance(encoding, np.ndarray)
        assert encoding.shape == (128,)

def test_find_matching_student(face_service):
    """Öğrenci eşleştirme testi."""
    encoding = np.random.rand(128)
    known_students = [
        {
            'id': 1,
            'face_encodings': np.random.rand(128).tolist()
        },
        {
            'id': 2,
            'face_encodings': np.random.rand(128).tolist()
        }
    ]
    
    match = face_service.find_matching_student(encoding, known_students)
    if match:
        assert 'student_id' in match
        assert 'confidence' in match
        assert isinstance(match['confidence'], float) 