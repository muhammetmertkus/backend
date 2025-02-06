import pytest
from fastapi import status
from app.models.course import Course
from app.models.teacher import Teacher

@pytest.fixture
def test_course(db_session, test_teacher):
    """Test dersi oluştur."""
    course = Course(
        code="CS101",
        name="Introduction to Programming",
        teacher_id=test_teacher.id,
        semester="2024-Spring",
        schedule={
            "monday": ["09:00-10:30"],
            "wednesday": ["09:00-10:30"]
        }
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course

def test_get_courses(client):
    """Ders listesi testi."""
    response = client.get("/api/v1/courses/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_course(client, test_course):
    """Ders detay testi."""
    response = client.get(f"/api/v1/courses/{test_course.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == test_course.code

def test_create_course(client, test_teacher):
    """Ders oluşturma testi."""
    response = client.post(
        "/api/v1/courses/",
        json={
            "code": "CS102",
            "name": "Data Structures",
            "teacher_id": test_teacher.id,
            "semester": "2024-Spring",
            "schedule": {
                "tuesday": ["13:00-14:30"],
                "thursday": ["13:00-14:30"]
            }
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == "CS102"

def test_update_course(client, test_course):
    """Ders güncelleme testi."""
    response = client.put(
        f"/api/v1/courses/{test_course.id}",
        json={
            "name": "Advanced Programming"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Advanced Programming" 