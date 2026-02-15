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


def test_integration_task_crud_flow(client, session):
    """Integration test: Complete CRUD flow for tasks"""
    # Create a user
    user = User(email="crud_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Create a task
        create_response = client.post("/tasks/", json={
            "title": "Integration Test Task",
            "description": "Integration Test Description",
            "completed": False
        })
        assert create_response.status_code == 200
        create_data = create_response.json()
        task_id = create_data["id"]

        # Verify task was created
        assert create_data["title"] == "Integration Test Task"
        assert create_data["description"] == "Integration Test Description"
        assert create_data["completed"] is False

        # Get all tasks
        get_all_response = client.get("/tasks/")
        assert get_all_response.status_code == 200
        get_all_data = get_all_response.json()
        assert len(get_all_data) == 1
        assert get_all_data[0]["id"] == task_id

        # Get specific task
        get_one_response = client.get(f"/tasks/{task_id}")
        assert get_one_response.status_code == 200
        get_one_data = get_one_response.json()
        assert get_one_data["id"] == task_id
        assert get_one_data["title"] == "Integration Test Task"

        # Update the task
        update_response = client.put(f"/tasks/{task_id}", json={
            "title": "Updated Integration Test Task",
            "description": "Updated Integration Test Description",
            "completed": True
        })
        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["id"] == task_id
        assert update_data["title"] == "Updated Integration Test Task"
        assert update_data["completed"] is True

        # Delete the task
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["message"] == "Task deleted successfully"

        # Verify task is deleted
        get_deleted_response = client.get(f"/tasks/{task_id}")
        assert get_deleted_response.status_code == 404


def test_integration_multiple_users_task_isolation(client, session):
    """Integration test: Verify task isolation between users"""
    # Create two users
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Mock authentication for user1
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        # User1 creates a task
        user1_task_response = client.post("/tasks/", json={
            "title": "User1's Task",
            "description": "Task for user1",
            "completed": False
        })
        assert user1_task_response.status_code == 200
        user1_task_data = user1_task_response.json()
        user1_task_id = user1_task_data["id"]

    # Mock authentication for user2
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # User2 creates a task
        user2_task_response = client.post("/tasks/", json={
            "title": "User2's Task",
            "description": "Task for user2",
            "completed": False
        })
        assert user2_task_response.status_code == 200
        user2_task_data = user2_task_response.json()
        user2_task_id = user2_task_data["id"]

        # User2 should only see their own task
        get_tasks_response = client.get("/tasks/")
        assert get_tasks_response.status_code == 200
        get_tasks_data = get_tasks_response.json()
        assert len(get_tasks_data) == 1
        assert get_tasks_data[0]["id"] == user2_task_id
        assert get_tasks_data[0]["title"] == "User2's Task"

        # User2 should not be able to access user1's task
        get_user1_task_response = client.get(f"/tasks/{user1_task_id}")
        assert get_user1_task_response.status_code == 404

        # User2 should not be able to update user1's task
        update_user1_task_response = client.put(f"/tasks/{user1_task_id}", json={
            "title": "Hacked Task",
            "completed": True
        })
        assert update_user1_task_response.status_code == 404

        # User2 should not be able to delete user1's task
        delete_user1_task_response = client.delete(f"/tasks/{user1_task_id}")
        assert delete_user1_task_response.status_code == 404


def test_integration_task_data_validation(client, session):
    """Integration test: Verify task data validation"""
    # Create a user
    user = User(email="validation_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Try to create task with empty title (should fail)
        empty_title_response = client.post("/tasks/", json={
            "title": "",
            "description": "Valid Description",
            "completed": False
        })
        assert empty_title_response.status_code == 400

        # Try to create task with very long title (should fail)
        long_title_response = client.post("/tasks/", json={
            "title": "x" * 201,  # Exceeds max length
            "description": "Valid Description",
            "completed": False
        })
        assert long_title_response.status_code == 400

        # Try to create task with very long description (should fail)
        long_desc_response = client.post("/tasks/", json={
            "title": "Valid Title",
            "description": "x" * 1001,  # Exceeds max length
            "completed": False
        })
        assert long_desc_response.status_code == 400

        # Create a valid task (should succeed)
        valid_task_response = client.post("/tasks/", json={
            "title": "Valid Task Title",
            "description": "Valid Task Description",
            "completed": False
        })
        assert valid_task_response.status_code == 200
        valid_task_data = valid_task_response.json()
        assert valid_task_data["title"] == "Valid Task Title"


def test_integration_task_timestamps(client, session):
    """Integration test: Verify task timestamps are properly set"""
    from datetime import datetime

    # Create a user
    user = User(email="timestamp_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Create a task
        response = client.post("/tasks/", json={
            "title": "Timestamp Test Task",
            "description": "Task to test timestamps",
            "completed": False
        })
        assert response.status_code == 200
        data = response.json()

        # Verify timestamps exist and are in proper format
        assert "created_at" in data
        assert "updated_at" in data

        # Verify timestamps are ISO format strings
        created_at_str = data["created_at"]
        updated_at_str = data["updated_at"]

        # Try to parse the timestamps to verify format
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))

        # created_at and updated_at should be close to now
        now = datetime.utcnow()
        time_diff_created = abs((now - created_at.replace(tzinfo=None)).total_seconds())
        time_diff_updated = abs((now - updated_at.replace(tzinfo=None)).total_seconds())

        # Should be within a few seconds
        assert time_diff_created < 10
        assert time_diff_updated < 10


def test_integration_task_completion_flow(client, session):
    """Integration test: Complete task completion flow"""
    # Create a user
    user = User(email="completion_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Create an incomplete task
        create_response = client.post("/tasks/", json={
            "title": "Completion Test Task",
            "description": "Task to test completion flow",
            "completed": False
        })
        assert create_response.status_code == 200
        create_data = create_response.json()
        task_id = create_data["id"]
        assert create_data["completed"] is False

        # Update task to completed
        update_response = client.put(f"/tasks/{task_id}", json={
            "completed": True
        })
        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["id"] == task_id
        assert update_data["completed"] is True

        # Verify task appears in completed state when retrieved
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["id"] == task_id
        assert get_data["completed"] is True