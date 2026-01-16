import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
from src.main import app
from src.database import get_session
from src.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_register_new_user(client):
    """Test registering a new user"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_active"] is True


def test_register_user_missing_email(client):
    """Test registering a user with missing email"""
    response = client.post("/auth/register", json={
        "password": "testpassword123"
    })

    assert response.status_code == 422  # Validation error


def test_register_user_missing_password(client):
    """Test registering a user with missing password"""
    response = client.post("/auth/register", json={
        "email": "test@example.com"
    })

    assert response.status_code == 422  # Validation error


def test_register_user_invalid_email(client):
    """Test registering a user with invalid email format"""
    response = client.post("/auth/register", json={
        "email": "invalid-email",
        "password": "testpassword123"
    })

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_register_user_short_password(client):
    """Test registering a user with too short password"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "123"
    })

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_login_success(client, session):
    """Test successful login"""
    # Create a user first
    user_data = User(
        email="test@example.com",
        password_hash="$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D",  # bcrypt hash for "testpassword"
        is_active=True
    )
    session.add(user_data)
    session.commit()
    session.refresh(user_data)

    # Mock password verification
    with patch("src.services.user_service.verify_password", return_value=True):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


def test_login_invalid_email(client):
    """Test login with invalid email"""
    response = client.post("/auth/login", json={
        "email": "invalid-email",
        "password": "testpassword"
    })

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_login_wrong_credentials(client):
    """Test login with wrong credentials"""
    # Mock password verification to return False
    with patch("src.services.user_service.verify_password", return_value=False):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


def test_login_nonexistent_user(client):
    """Test login for non-existent user"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "testpassword"
    })

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data