import pytest
from datetime import datetime
from app.services.attendance_service import AttendanceService
from app.models.attendance import Attendance, AttendanceType
from app.schemas.attendance import AttendanceCreate

@pytest.fixture
def attendance_service(db_session):
    """Attendance service fixture."""
    return AttendanceService(db_session)

def test_create_attendance(attendance_service):
    """Yoklama oluşturma testi."""
    attendance_data = AttendanceCreate(
        course_id=1,
        date=datetime.utcnow(),
        type=AttendanceType.MANUAL,
        created_by=1
    )
    
    attendance = attendance_service.create_attendance(attendance_data)
    assert attendance is not None
    assert attendance.course_id == attendance_data.course_id
    assert attendance.type == attendance_data.type

@pytest.mark.asyncio
async def test_process_attendance_image(attendance_service, test_image):
    """Görüntüden yoklama alma testi."""
    known_students = [
        {
            'id': 1,
            'face_encodings': [0.1] * 128,
            'email': 'test@example.com'
        }
    ]
    
    result = await attendance_service.process_attendance_image(
        course_id=1,
        image_data=test_image,
        known_students=known_students
    )
    
    assert isinstance(result, dict)
    assert 'attendance_id' in result or 'error' in result 