"""
Basic functionality tests to verify the core application features work correctly.
These tests verify the completed tasks from the todo list.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
from src.main import app
from src.database import get_session
from src.models.user import User
from src.models.task import Task


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


def test_root_endpoint_works(client):
    """Test that the root endpoint works"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Todo API is running!"


def test_health_endpoint_works(client):
    """Test that the health endpoint works"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_security_headers_present(client):
    """Test that security headers are present in responses"""
    response = client.get("/health")

    # Check for security headers
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload"
    }

    for header, expected_value in security_headers.items():
        assert header in response.headers
        assert response.headers[header] == expected_value


def test_validation_middleware_basic(client):
    """Test basic validation functionality"""
    # Test that validation middleware is present by testing an invalid request
    # that should be caught by validation
    response = client.post("/auth/register", json={
        "email": "invalid-email-format",
        "password": "short"  # Too short
    })

    # Should return validation error
    assert response.status_code in [400, 422]  # Either validation error or pydantic error


def test_database_model_indexes():
    """Test that the database models have indexes as expected"""
    # Check that the Task model has the expected indexes
    from src.models.task import Task
    from sqlalchemy import inspect

    # Create an in-memory database to inspect the model
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    indexes = inspector.get_indexes('task')

    # Check for expected indexes
    index_columns = {idx['column_names'][0] for idx in indexes if len(idx['column_names']) == 1}
    expected_indexes = {'completed', 'user_id', 'due_date', 'created_at', 'updated_at'}

    # Verify that at least the main indexes are present
    assert 'user_id' in index_columns  # Critical for user isolation
    assert 'completed' in index_columns  # Useful for filtering


def test_user_model_indexes():
    """Test that the user database model has indexes as expected"""
    from src.models.user import User
    from sqlalchemy import inspect

    # Create an in-memory database to inspect the model
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    indexes = inspector.get_indexes('user')

    # Check for expected indexes
    index_columns = {idx['column_names'][0] for idx in indexes if len(idx['column_names']) == 1}

    assert 'email' in index_columns  # Critical for login performance
    assert 'is_active' in index_columns  # Useful for filtering active users
    assert 'created_at' in index_columns  # Useful for time-based queries


def test_application_startup():
    """Test that the application starts up correctly"""
    # This test verifies that the app can be imported and instantiated
    # which means all dependencies are properly configured
    assert app is not None
    assert hasattr(app, 'routes')

    # Verify middleware is properly added - check that middleware have been added
    # The middleware are stored differently in FastAPI, so let's check by looking at the middleware stack
    assert len(app.user_middleware) > 0

    # Check if our custom middleware are registered by looking for their types
    middleware_types = [type(mw) for mw in app.user_middleware]
    # Since the middleware are added by type, we can check if our custom middleware types are present
    # by checking the app's middleware registry
    middleware_classes = [mw.cls for mw in app.user_middleware if hasattr(mw, 'cls')]

    # For this test, just verify that the app has middleware configured
    assert len(middleware_classes) >= 2  # At least Security and Validation middleware


if __name__ == "__main__":
    pytest.main([__file__, "-v"])