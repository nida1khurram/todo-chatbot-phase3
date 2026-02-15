import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database import get_session


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


def test_contract_auth_register_success(client):
    """Contract test: register endpoint should accept valid user data and return user object"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })

    assert response.status_code == 200
    data = response.json()

    # Contract: Response should contain user fields
    assert "id" in data
    assert "email" in data
    assert "is_active" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Contract: Email should match input
    assert data["email"] == "test@example.com"

    # Contract: User should be active by default
    assert data["is_active"] is True


def test_contract_auth_register_invalid_email(client):
    """Contract test: register endpoint should reject invalid email format"""
    response = client.post("/auth/register", json={
        "email": "invalid-email",
        "password": "testpassword123"
    })

    assert response.status_code == 400
    data = response.json()

    # Contract: Should return error detail
    assert "detail" in data


def test_contract_auth_register_short_password(client):
    """Contract test: register endpoint should reject short passwords"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "123"  # Too short
    })

    assert response.status_code == 400
    data = response.json()

    # Contract: Should return error detail
    assert "detail" in data


def test_contract_auth_login_success(client, session):
    """Contract test: login endpoint should accept valid credentials and return token"""
    from src.models.user import User
    from src.middleware.auth import get_password_hash

    # Create a user first
    hashed_password = get_password_hash("testpassword123")
    user = User(email="test@example.com", password_hash=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })

    assert response.status_code == 200
    data = response.json()

    # Contract: Response should contain access token and token type
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Contract: Token should be a string
    assert isinstance(data["access_token"], str)


def test_contract_auth_login_invalid_credentials(client):
    """Contract test: login endpoint should reject invalid credentials"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    data = response.json()

    # Contract: Should return error detail
    assert "detail" in data


def test_contract_auth_login_invalid_email_format(client):
    """Contract test: login endpoint should reject invalid email format"""
    response = client.post("/auth/login", json={
        "email": "invalid-email",
        "password": "password"
    })

    assert response.status_code == 400
    data = response.json()

    # Contract: Should return error detail
    assert "detail" in data