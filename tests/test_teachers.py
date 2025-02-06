import pytest
from fastapi import status
from app.models.teacher import Teacher
from app.models.user import User, UserRole

@pytest.fixture
def test_teacher(db_session):
    """Test öğretmeni oluştur."""
    # Önce kullanıcı oluştur
    user = User(
        email="teacher@example.com",
        password="testpass123",
        name="Test",
        surname="Teacher",
        role=UserRole.TEACHER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Sonra öğretmen oluştur
    teacher = Teacher(
        user_id=user.id,
        department="Computer Science",
        title="Professor"
    )
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher

def test_get_teachers(client):
    """Öğretmen listesi testi."""
    response = client.get("/api/v1/teachers/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_teacher(client, test_teacher):
    """Öğretmen detay testi."""
    response = client.get(f"/api/v1/teachers/{test_teacher.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["department"] == test_teacher.department

def test_create_teacher(client, db_session):
    """Öğretmen oluşturma testi."""
    # Önce kullanıcı oluştur
    user = User(
        email="new.teacher@example.com",
        password="testpass123",
        name="New",
        surname="Teacher",
        role=UserRole.TEACHER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/teachers/",
        json={
            "user_id": user.id,
            "department": "Physics",
            "title": "Associate Professor"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["department"] == "Physics"

def test_update_teacher(client, test_teacher):
    """Öğretmen güncelleme testi."""
    response = client.put(
        f"/api/v1/teachers/{test_teacher.id}",
        json={
            "title": "Full Professor"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Full Professor" 