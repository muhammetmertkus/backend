import pytest
from fastapi import status
from app.models.student import Student
from app.models.user import User, UserRole

@pytest.fixture
def test_student(db_session):
    """Test öğrencisi oluştur."""
    # Önce kullanıcı oluştur
    user = User(
        email="student@example.com",
        password="testpass123",
        name="Test",
        surname="Student",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Sonra öğrenci oluştur
    student = Student(
        user_id=user.id,
        student_number="12345678",
        department="Computer Science"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student

def test_get_students(client):
    """Öğrenci listesi testi."""
    response = client.get("/api/v1/students/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_student(client, test_student):
    """Öğrenci detay testi."""
    response = client.get(f"/api/v1/students/{test_student.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["student_number"] == test_student.student_number

def test_create_student(client, db_session):
    """Öğrenci oluşturma testi."""
    # Önce kullanıcı oluştur
    user = User(
        email="new.student@example.com",
        password="testpass123",
        name="New",
        surname="Student",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/students/",
        json={
            "user_id": user.id,
            "student_number": "87654321",
            "department": "Physics"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["student_number"] == "87654321"

def test_update_student(client, test_student):
    """Öğrenci güncelleme testi."""
    response = client.put(
        f"/api/v1/students/{test_student.id}",
        json={
            "department": "Mathematics"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["department"] == "Mathematics" 