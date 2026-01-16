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


def test_integration_task_isolation_complete_flow(client, session):
    """Integration test: Complete task isolation flow with multiple users"""
    # Create multiple users
    user1 = User(email="isolation_user1@example.com", password_hash="hash1")
    user2 = User(email="isolation_user2@example.com", password_hash="hash2")
    user3 = User(email="isolation_user3@example.com", password_hash="hash3")
    session.add(user1)
    session.add(user2)
    session.add(user3)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)
    session.refresh(user3)

    # Mock authentication for user1 and create tasks
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        # Create tasks for user1
        user1_task1_response = client.post("/tasks/", json={
            "title": "User1's Task 1",
            "description": "First task for user1",
            "completed": False
        })
        assert user1_task1_response.status_code == 200
        user1_task1_id = user1_task1_response.json()["id"]

        user1_task2_response = client.post("/tasks/", json={
            "title": "User1's Task 2",
            "description": "Second task for user1",
            "completed": True
        })
        assert user1_task2_response.status_code == 200
        user1_task2_id = user1_task2_response.json()["id"]

    # Mock authentication for user2 and create tasks
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # Create tasks for user2
        user2_task1_response = client.post("/tasks/", json={
            "title": "User2's Task 1",
            "description": "First task for user2",
            "completed": False
        })
        assert user2_task1_response.status_code == 200
        user2_task1_id = user2_task1_response.json()["id"]

        user2_task2_response = client.post("/tasks/", json={
            "title": "User2's Task 2",
            "description": "Second task for user2",
            "completed": True
        })
        assert user2_task2_response.status_code == 200
        user2_task2_id = user2_task2_response.json()["id"]

    # Verify user1 only sees their own tasks
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        user1_tasks_response = client.get("/tasks/")
        assert user1_tasks_response.status_code == 200
        user1_tasks = user1_tasks_response.json()
        assert len(user1_tasks) == 2
        user1_task_ids = [task["id"] for task in user1_tasks]
        assert user1_task1_id in user1_task_ids
        assert user1_task2_id in user1_task_ids
        assert user2_task1_id not in user1_task_ids
        assert user2_task2_id not in user1_task_ids

    # Verify user2 only sees their own tasks
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        user2_tasks_response = client.get("/tasks/")
        assert user2_tasks_response.status_code == 200
        user2_tasks = user2_tasks_response.json()
        assert len(user2_tasks) == 2
        user2_task_ids = [task["id"] for task in user2_tasks]
        assert user2_task1_id in user2_task_ids
        assert user2_task2_id in user2_task_ids
        assert user1_task1_id not in user2_task_ids
        assert user1_task2_id not in user2_task_ids

    # Verify cross-user access attempts fail
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        # User1 should not be able to access user2's tasks
        assert client.get(f"/tasks/{user2_task1_id}").status_code == 404
        assert client.get(f"/tasks/{user2_task2_id}").status_code == 404
        assert client.put(f"/tasks/{user2_task1_id}", json={"title": "Hacked"}).status_code == 404
        assert client.delete(f"/tasks/{user2_task1_id}").status_code == 404

    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # User2 should not be able to access user1's tasks
        assert client.get(f"/tasks/{user1_task1_id}").status_code == 404
        assert client.get(f"/tasks/{user1_task2_id}").status_code == 404
        assert client.put(f"/tasks/{user1_task1_id}", json={"title": "Hacked"}).status_code == 404
        assert client.delete(f"/tasks/{user1_task1_id}").status_code == 404


def test_integration_task_isolation_database_level(client, session):
    """Integration test: Verify isolation at the database level"""
    # Create users
    user1 = User(email="db_isolation_user1@example.com", password_hash="hash1")
    user2 = User(email="db_isolation_user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create tasks directly in the database
    task1 = Task(title="DB Isolation Task 1", description="Task for user1", completed=False, user_id=user1.id)
    task2 = Task(title="DB Isolation Task 2", description="Task for user1", completed=True, user_id=user1.id)
    task3 = Task(title="DB Isolation Task 3", description="Task for user2", completed=False, user_id=user2.id)
    task4 = Task(title="DB Isolation Task 4", description="Task for user2", completed=True, user_id=user2.id)
    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.add(task4)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)
    session.refresh(task3)
    session.refresh(task4)

    # Verify user1 only sees their tasks through API
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        response = client.get("/tasks/")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        task_titles = [task["title"] for task in tasks]
        assert "DB Isolation Task 1" in task_titles
        assert "DB Isolation Task 2" in task_titles
        assert "DB Isolation Task 3" not in task_titles
        assert "DB Isolation Task 4" not in task_titles

    # Verify user2 only sees their tasks through API
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        response = client.get("/tasks/")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        task_titles = [task["title"] for task in tasks]
        assert "DB Isolation Task 3" in task_titles
        assert "DB Isolation Task 4" in task_titles
        assert "DB Isolation Task 1" not in task_titles
        assert "DB Isolation Task 2" not in task_titles


def test_integration_task_isolation_with_updates(client, session):
    """Integration test: Verify isolation persists through updates"""
    # Create users
    user1 = User(email="update_isolation_user1@example.com", password_hash="hash1")
    user2 = User(email="update_isolation_user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create tasks
    task1 = Task(title="Original User1 Task", description="Original description", completed=False, user_id=user1.id)
    task2 = Task(title="Original User2 Task", description="Original description", completed=False, user_id=user2.id)
    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    # User1 updates their task
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        update_response = client.put(f"/tasks/{task1.id}", json={
            "title": "Updated User1 Task",
            "description": "Updated description",
            "completed": True
        })
        assert update_response.status_code == 200

    # User2 should still only see their own task
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        tasks_response = client.get("/tasks/")
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Original User2 Task"
        assert tasks[0]["id"] == task2.id

    # User2 should not be able to see updated version of user1's task
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        attempt_response = client.get(f"/tasks/{task1.id}")
        assert attempt_response.status_code == 404


def test_integration_task_isolation_with_deletion(client, session):
    """Integration test: Verify isolation with task deletion"""
    # Create users
    user1 = User(email="delete_isolation_user1@example.com", password_hash="hash1")
    user2 = User(email="delete_isolation_user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create tasks
    task1 = Task(title="User1 Task to Delete", description="Task for user1", completed=False, user_id=user1.id)
    task2 = Task(title="User2 Task to Keep", description="Task for user2", completed=False, user_id=user2.id)
    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    # User1 deletes their task
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        delete_response = client.delete(f"/tasks/{task1.id}")
        assert delete_response.status_code == 200

    # Verify task is deleted for user1
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        tasks_response = client.get("/tasks/")
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        assert len(tasks) == 0

    # User2 should still see their task and not be affected
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        tasks_response = client.get("/tasks/")
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "User2 Task to Keep"

    # User2 should not be able to access user1's deleted task
    with patch("src.middleware.auth.get_current_user", return_value=user2):
        attempt_response = client.get(f"/tasks/{task1.id}")
        assert attempt_response.status_code == 404


def test_integration_task_isolation_edge_cases(client, session):
    """Integration test: Verify isolation with edge cases"""
    # Create users
    user1 = User(email="edge_user1@example.com", password_hash="hash1")
    user2 = User(email="edge_user2@example.com", password_hash="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create tasks with similar titles/descriptions
    task1 = Task(title="Similar Task", description="Common description", completed=False, user_id=user1.id)
    task2 = Task(title="Similar Task", description="Common description", completed=False, user_id=user2.id)
    session.add(task1)
    session.add(task2)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)

    # Verify that tasks with identical content are still isolated
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        user1_tasks = client.get("/tasks/").json()
        assert len(user1_tasks) == 1
        assert user1_tasks[0]["id"] == task1.id
        assert user1_tasks[0]["user_id"] == user1.id

    with patch("src.middleware.auth.get_current_user", return_value=user2):
        user2_tasks = client.get("/tasks/").json()
        assert len(user2_tasks) == 1
        assert user2_tasks[0]["id"] == task2.id
        assert user2_tasks[0]["user_id"] == user2.id

    # Test accessing with wrong user context
    with patch("src.middleware.auth.get_current_user", return_value=user1):
        # Should not be able to access user2's task even with same title
        response = client.get(f"/tasks/{task2.id}")
        assert response.status_code == 404

    with patch("src.middleware.auth.get_current_user", return_value=user2):
        # Should not be able to access user1's task even with same title
        response = client.get(f"/tasks/{task1.id}")
        assert response.status_code == 404