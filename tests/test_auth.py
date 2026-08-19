import pytest
from django.contrib.auth.hashers import make_password

from accounts.models import UserABS


@pytest.fixture
def user(db):
    return UserABS.objects.create(
        email="test@wallet.local",
        first_name="Test",
        last_name="User",
        password=make_password("TestPass123!"),
    )


@pytest.mark.django_db
def test_register(client):
    response = client.post(
        "/api/auth/register/",
        {
            "email": "new@wallet.local",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        },
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json()["__email__"] == "new@wallet.local"


@pytest.mark.django_db
def test_login(client, user):
    response = client.post(
        "/api/auth/login/",
        {"email": "test@wallet.local", "password": "TestPass123!"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["__email__"] == "test@wallet.local"


@pytest.mark.django_db
def test_me_after_login(client, user):
    client.post(
        "/api/auth/login/",
        {"email": "test@wallet.local", "password": "TestPass123!"},
        content_type="application/json",
    )
    response = client.get("/api/auth/me/")
    assert response.status_code == 200
    assert response.json()["__email__"] == "test@wallet.local"
