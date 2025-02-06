import pytest
from datetime import datetime, timedelta
from fastapi import status
from app.models.attendance import Attendance, AttendanceDetail
from app.models.emotion import EmotionHistory
from app.models.course import Course
from app.models.student import Student
from app.models.teacher import Teacher

@pytest.fixture
def test_data(db_session, test_student, test_teacher):
    """Test verilerini oluştur."""
    # Ders oluştur
    course = Course(
        code="CS101",
        name="Introduction to Programming",
        teacher_id=test_teacher.id,
        semester="2024-Spring"
    )
    db_session.add(course)
    db_session.commit()
    
    # Yoklama oluştur
    attendance = Attendance(
        course_id=course.id,
        date=datetime.utcnow(),
        type="FACE",
        created_by=test_teacher.user_id
    )
    db_session.add(attendance)
    db_session.commit()
    
    # Yoklama detayı oluştur
    detail = AttendanceDetail(
        attendance_id=attendance.id,
        student_id=test_student.id,
        status=True,
        emotion_data={"dominant_emotion": "happy", "confidence": 0.9},
        confidence=0.95
    )
    db_session.add(detail)
    
    # Duygu geçmişi oluştur
    emotion = EmotionHistory(
        student_id=test_student.id,
        course_id=course.id,
        emotion="happy",
        confidence=0.9,
        date=datetime.utcnow()
    )
    db_session.add(emotion)
    db_session.commit()
    
    return {
        'course': course,
        'attendance': attendance,
        'detail': detail,
        'emotion': emotion
    }

def test_get_daily_attendance_report(client, test_data):
    """Günlük yoklama raporu testi."""
    response = client.get(
        "/api/v1/reports/attendance/daily",
        params={
            'course_id': test_data['course'].id,
            'date': datetime.utcnow().date().isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'total_students' in response.json()
    assert 'details' in response.json()

def test_get_course_emotion_report(client, test_data):
    """Ders duygu analizi raporu testi."""
    response = client.get(
        f"/api/v1/reports/emotions/course/{test_data['course'].id}",
        params={
            'start_date': (datetime.utcnow() - timedelta(days=7)).isoformat(),
            'end_date': datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'emotion_stats' in response.json()
    assert 'total_records' in response.json()

def test_get_student_attendance_report(client, test_data, test_student):
    """Öğrenci yoklama raporu testi."""
    response = client.get(
        f"/api/v1/reports/attendance/student/{test_student.id}",
        params={
            'course_id': test_data['course'].id,
            'start_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
            'end_date': datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'total_attendance' in response.json()
    assert 'attendance_rate' in response.json()
    assert 'emotion_stats' in response.json()
    assert 'details' in response.json() 