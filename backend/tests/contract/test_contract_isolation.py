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


def test_contract_isolation_get_other_user_task(client, session):
    """Contract test: Users should not be able to access other users' tasks"""
    from src.models.user import User
    from src.models.task import Task

    # Create two users and a task for user1
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    task = Task(title="User1's Task", description="Task for user1", completed=False, user_id=user1.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Mock authentication as user2
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # User2 should not be able to access user1's task
        response = client.get(f"/tasks/{task.id}")

        # Contract: Should return 404 (not found) instead of 403 (forbidden)
        # This prevents information leakage about whether the task exists
        assert response.status_code == 404


def test_contract_isolation_update_other_user_task(client, session):
    """Contract test: Users should not be able to update other users' tasks"""
    from src.models.user import User
    from src.models.task import Task

    # Create two users and a task for user1
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    task = Task(title="User1's Task", description="Task for user1", completed=False, user_id=user1.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Mock authentication as user2
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # User2 should not be able to update user1's task
        response = client.put(f"/tasks/{task.id}", json={
            "title": "Hacked Task",
            "completed": True
        })

        # Contract: Should return 404 (not found) instead of 403 (forbidden)
        assert response.status_code == 404


def test_contract_isolation_delete_other_user_task(client, session):
    """Contract test: Users should not be able to delete other users' tasks"""
    from src.models.user import User
    from src.models.task import Task

    # Create two users and a task for user1
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    task = Task(title="User1's Task", description="Task for user1", completed=False, user_id=user1.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Mock authentication as user2
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # User2 should not be able to delete user1's task
        response = client.delete(f"/tasks/{task.id}")

        # Contract: Should return 404 (not found) instead of 403 (forbidden)
        assert response.status_code == 404


def test_contract_isolation_task_list(client, session):
    """Contract test: Users should only see their own tasks in the list"""
    from src.models.user import User
    from src.models.task import Task

    # Create two users and tasks for each
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create tasks for user1
    task1 = Task(title="User1's Task 1", description="Task 1 for user1", completed=False, user_id=user1.id)
    task2 = Task(title="User1's Task 2", description="Task 2 for user1", completed=True, user_id=user1.id)
    session.add(task1)
    session.add(task2)

    # Create tasks for user2
    task3 = Task(title="User2's Task 1", description="Task 1 for user2", completed=False, user_id=user2.id)
    task4 = Task(title="User2's Task 2", description="Task 2 for user2", completed=True, user_id=user2.id)
    session.add(task3)
    session.add(task4)

    session.commit()

    # Mock authentication as user1
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        # User1 should only see their own tasks
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()

        # Contract: Response should be a list containing only user1's tasks
        assert isinstance(data, list)
        assert len(data) == 2  # user1 has 2 tasks

        # Contract: All tasks in the list should belong to user1
        for task in data:
            assert task["user_id"] == user1.id
            assert task["title"] in ["User1's Task 1", "User1's Task 2"]


def test_contract_isolation_user_authentication_required(client, session):
    """Contract test: Task endpoints should require authentication"""
    from src.models.user import User
    from src.models.task import Task

    # Create a user and a task
    user = User(email="auth_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(title="Auth Test Task", description="Task for auth test", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Make request without authentication
    response = client.get(f"/tasks/{task.id}")

    # Contract: Should return 401 Unauthorized
    assert response.status_code == 401


def test_contract_isolation_cross_user_data_protection(client, session):
    """Contract test: API responses should not expose other users' data"""
    from src.models.user import User
    from src.models.task import Task

    # Create users and tasks
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    task1 = Task(title="User1's Task", description="Task for user1", completed=False, user_id=user1.id)
    session.add(task1)
    session.commit()
    session.refresh(task1)

    # Mock authentication as user2
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # Try to access user1's task
        response = client.get(f"/tasks/{task1.id}")

        # Contract: Should return 404, not expose any information about the task
        assert response.status_code == 404

        # Verify that the response doesn't leak any information about the task
        response_data = response.json()
        assert "detail" in response_data  # Standard error response