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


def test_integration_user_registration_flow(client, session):
    """Integration test: Complete user registration flow"""
    # Register a new user
    response = client.post("/auth/register", json={
        "email": "integration_test@example.com",
        "password": "securepassword123"
    })

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["email"] == "integration_test@example.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify user was created in database
    created_user = session.get(User, data["id"])
    assert created_user is not None
    assert created_user.email == "integration_test@example.com"
    assert created_user.is_active is True


def test_integration_user_login_flow(client, session):
    """Integration test: Complete user login flow"""
    from src.middleware.auth import get_password_hash

    # Create a user in the database
    hashed_password = get_password_hash("testpassword123")
    user = User(email="login_test@example.com", password_hash=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock password verification to return True
    with patch("src.services.user_service.verify_password", return_value=True):
        # Login with valid credentials
        response = client.post("/auth/login", json={
            "email": "login_test@example.com",
            "password": "testpassword123"
        })

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid format
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0


def test_integration_register_then_login(client, session):
    """Integration test: Register a user then immediately login"""
    # Register a new user
    register_response = client.post("/auth/register", json={
        "email": "register_then_login@example.com",
        "password": "testpassword123"
    })

    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data["email"] == "register_then_login@example.com"

    # Verify user exists in database
    user_id = register_data["id"]
    user = session.get(User, user_id)
    assert user is not None
    assert user.email == "register_then_login@example.com"

    # Login with the same credentials
    with patch("src.services.user_service.verify_password", return_value=True):
        login_response = client.post("/auth/login", json={
            "email": "register_then_login@example.com",
            "password": "testpassword123"
        })

        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"


def test_integration_duplicate_email_registration(client, session):
    """Integration test: Attempt to register with duplicate email"""
    # Register first user
    response1 = client.post("/auth/register", json={
        "email": "duplicate_test@example.com",
        "password": "password1"
    })
    assert response1.status_code == 200

    # Try to register with same email
    response2 = client.post("/auth/register", json={
        "email": "duplicate_test@example.com",
        "password": "password2"
    })

    # Should fail due to unique constraint
    assert response2.status_code == 400


def test_integration_password_hashing_integration(client, session):
    """Integration test: Verify password is properly hashed during registration"""
    from src.middleware.auth import verify_password

    # Register a user
    response = client.post("/auth/register", json={
        "email": "hash_test@example.com",
        "password": "original_password"
    })

    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]

    # Retrieve user from database
    user = session.get(User, user_id)
    assert user is not None

    # Verify the password was hashed (not stored in plain text)
    assert user.password_hash != "original_password"

    # Verify password verification works with original password
    assert verify_password("original_password", user.password_hash)

    # Verify password verification fails with wrong password
    assert not verify_password("wrong_password", user.password_hash)