import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
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


def test_contract_tasks_get_all_success(client):
    """Contract test: GET /tasks endpoint should return list of tasks"""
    # Mock authentication to bypass auth check
    with patch("src.middleware.auth.get_current_user"):
        response = client.get("/tasks/")

    # Contract: Should return 200 OK with empty list if no tasks
    assert response.status_code == 200
    data = response.json()

    # Contract: Response should be a list
    assert isinstance(data, list)


def test_contract_tasks_create_success(client):
    """Contract test: POST /tasks endpoint should accept task data and return created task"""
    # Mock authentication to bypass auth check
    with patch("src.middleware.auth.get_current_user"):
        response = client.post("/tasks/", json={
            "title": "Test Task",
            "description": "Test Description",
            "completed": False
        })

    assert response.status_code == 200
    data = response.json()

    # Contract: Response should contain task fields
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "completed" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Contract: Values should match input
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False


def test_contract_tasks_create_missing_title(client):
    """Contract test: POST /tasks endpoint should reject request without title"""
    # Mock authentication to bypass auth check
    with patch("src.middleware.auth.get_current_user"):
        response = client.post("/tasks/", json={
            "description": "Test Description",
            "completed": False
        })

    # Contract: Should return 400 for validation error
    assert response.status_code == 422  # Validation error


def test_contract_tasks_get_specific_success(client, session):
    """Contract test: GET /tasks/{id} endpoint should return specific task"""
    from src.models.user import User
    from src.models.task import Task

    # Create a user and task in the database
    user = User(email="test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Mock authentication to bypass auth check
    with patch("src.middleware.auth.get_current_user", return_value=user):
        response = client.get(f"/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()

    # Contract: Response should contain task fields
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "completed" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Contract: Values should match created task
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert data["id"] == task.id


def test_contract_tasks_update_success(client, session):
    """Contract test: PUT /tasks/{id} endpoint should update task and return updated task"""
    from src.models.user import User
    from src.models.task import Task

    # Create a user and task in the database
    user = User(email="test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(title="Original Title", description="Original Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Mock authentication to bypass auth check
    with patch("src.middleware.auth.get_current_user", return_value=user):
        response = client.put(f"/tasks/{task.id}", json={
            "title": "Updated Title",
            "description": "Updated Description",
            "completed": True
        })

    assert response.status_code == 200
    data = response.json()

    # Contract: Response should contain task fields
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "completed" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Contract: Updated values should match input
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True


def test_contract_tasks_delete_success(client, session):
    """Contract test: DELETE /tasks/{id} endpoint should delete task and return success message"""
    from src.models.user import User
    from src.models.task import Task

    # Create a user and task in the database
    user = User(email="test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Mock authentication to bypass auth check
    with patch("src.middleware.auth.get_current_user", return_value=user):
        response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()

    # Contract: Response should contain success message
    assert "message" in data
    assert data["message"] == "Task deleted successfully"