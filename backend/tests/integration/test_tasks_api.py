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


@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client, session):
    """Create an authenticated client with a logged-in user"""
    # Create a user
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
        # Login to get token
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })

    assert login_response.status_code == 200
    token_data = login_response.json()
    access_token = token_data["access_token"]

    # Add the token to the client headers
    client.headers["Authorization"] = f"Bearer {access_token}"

    return client, user_data


def test_get_tasks_empty(authenticated_client):
    """Test getting tasks when user has no tasks"""
    client, user = authenticated_client

    response = client.get("/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_create_task(authenticated_client):
    """Test creating a new task"""
    client, user = authenticated_client

    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert data["user_id"] == user.id


def test_get_tasks_with_data(authenticated_client, session):
    """Test getting tasks when user has tasks"""
    client, user = authenticated_client

    # Create a task directly in the database
    task = Task(title="Existing Task", description="Existing Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.get("/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Existing Task"


def test_get_specific_task(authenticated_client, session):
    """Test getting a specific task"""
    client, user = authenticated_client

    # Create a task directly in the database
    task = Task(title="Specific Task", description="Specific Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.get(f"/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Task"
    assert data["description"] == "Specific Description"


def test_get_nonexistent_task(authenticated_client):
    """Test getting a non-existent task"""
    client, user = authenticated_client

    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_update_task(authenticated_client, session):
    """Test updating a task"""
    client, user = authenticated_client

    # Create a task directly in the database
    task = Task(title="Original Title", description="Original Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.put(f"/tasks/{task.id}", json={
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True


def test_delete_task(authenticated_client, session):
    """Test deleting a task"""
    client, user = authenticated_client

    # Create a task directly in the database
    task = Task(title="Task to Delete", description="Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task deleted successfully"

    # Verify the task was deleted
    get_response = client.get(f"/tasks/{task.id}")
    assert get_response.status_code == 404


def test_unauthorized_access(client):
    """Test accessing tasks endpoint without authentication"""
    response = client.get("/tasks/")

    assert response.status_code == 401  # Unauthorized


def test_create_task_invalid_data(authenticated_client):
    """Test creating a task with invalid data"""
    client, user = authenticated_client

    response = client.post("/tasks/", json={
        "title": "",  # Empty title should fail validation
        "description": "Valid Description",
        "completed": False
    })

    assert response.status_code == 400  # Validation error


def test_update_task_invalid_data(authenticated_client, session):
    """Test updating a task with invalid data"""
    client, user = authenticated_client

    # Create a task directly in the database
    task = Task(title="Original Title", description="Original Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.put(f"/tasks/{task.id}", json={
        "title": ""  # Empty title should fail validation
    })

    assert response.status_code == 400  # Validation error