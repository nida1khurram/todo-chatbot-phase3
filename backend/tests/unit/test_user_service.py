import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock
from src.models.user import User
from src.services.user_service import create_user, authenticate_user, get_user_by_email, get_user_by_id


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


def test_create_user(session):
    """Test creating a new user"""
    email = "test@example.com"
    password_hash = "$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D"

    user = create_user(session, email, password_hash)

    assert user.email == email
    assert user.password_hash == password_hash
    assert user.is_active is True


def test_authenticate_user_success(session):
    """Test successful user authentication"""
    # Create a user first
    email = "test@example.com"
    password_hash = "$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D"
    user = create_user(session, email, password_hash)

    # Mock the verify_password function
    import src.services.user_service
    original_verify = src.services.user_service.verify_password
    src.services.user_service.verify_password = Mock(return_value=True)

    try:
        authenticated_user = authenticate_user(session, email, "password")
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == email
    finally:
        # Restore original function
        src.services.user_service.verify_password = original_verify


def test_authenticate_user_wrong_password(session):
    """Test authentication with wrong password"""
    # Create a user first
    email = "test@example.com"
    password_hash = "$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D"
    user = create_user(session, email, password_hash)

    # Mock the verify_password function to return False
    import src.services.user_service
    original_verify = src.services.user_service.verify_password
    src.services.user_service.verify_password = Mock(return_value=False)

    try:
        authenticated_user = authenticate_user(session, email, "wrong_password")
        assert authenticated_user is None
    finally:
        # Restore original function
        src.services.user_service.verify_password = original_verify


def test_authenticate_user_nonexistent_user(session):
    """Test authentication with non-existent user"""
    authenticated_user = authenticate_user(session, "nonexistent@example.com", "password")
    assert authenticated_user is None


def test_get_user_by_email(session):
    """Test getting user by email"""
    email = "test@example.com"
    password_hash = "$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D"

    created_user = create_user(session, email, password_hash)
    retrieved_user = get_user_by_email(session, email)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


def test_get_user_by_email_nonexistent(session):
    """Test getting non-existent user by email"""
    user = get_user_by_email(session, "nonexistent@example.com")
    assert user is None


def test_get_user_by_id(session):
    """Test getting user by ID"""
    email = "test@example.com"
    password_hash = "$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D"

    created_user = create_user(session, email, password_hash)
    retrieved_user = get_user_by_id(session, created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


def test_get_user_by_id_nonexistent(session):
    """Test getting non-existent user by ID"""
    user = get_user_by_id(session, 999)
    assert user is None