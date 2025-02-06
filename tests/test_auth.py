import pytest
from fastapi import status
from app.core.security import get_password_hash
from app.models.user import User, UserRole

@pytest.fixture
def test_user(db_session):
    """Test kullanıcısı oluştur."""
    user = User(
        email="test@example.com",
        password=get_password_hash("testpass123"),
        name="Test",
        surname="User",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_login(client, test_user):
    """Giriş testi."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Yanlış şifre ile giriş testi."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpass"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_register(client):
    """Kayıt testi."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "newpass123",
            "name": "New",
            "surname": "User",
            "role": "STUDENT"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "new@example.com"
    assert response.json()["role"] == "STUDENT" 