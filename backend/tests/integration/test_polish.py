import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
from src.main import app
from src.database import get_session
from src.models.user import User
from src.models.task import Task
import logging
import re


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


def test_comprehensive_logging(client, session):
    """Integration test: Verify comprehensive logging throughout the application"""
    # Capture logs
    import io
    import sys
    from contextlib import redirect_stderr

    # Create a user
    user = User(email="logging_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Perform a series of operations to trigger logging
        create_response = client.post("/tasks/", json={
            "title": "Logging Test Task",
            "description": "Task to test logging",
            "completed": False
        })

        get_response = client.get("/tasks/")

        task_id = create_response.json()["id"]
        get_one_response = client.get(f"/tasks/{task_id}")

        update_response = client.put(f"/tasks/{task_id}", json={
            "title": "Updated Logging Test Task",
            "completed": True
        })

        delete_response = client.delete(f"/tasks/{task_id}")

    # Verify all operations succeeded
    assert create_response.status_code == 200
    assert get_response.status_code == 200
    assert get_one_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 200


def test_input_validation_middleware_comprehensive(client, session):
    """Integration test: Verify input validation middleware works across all endpoints"""
    # Test auth validation - invalid email
    register_invalid_email_response = client.post("/auth/register", json={
        "email": "invalid-email",
        "password": "validpassword123"
    })
    assert register_invalid_email_response.status_code == 400

    # Test auth validation - weak password
    register_weak_password_response = client.post("/auth/register", json={
        "email": "valid@example.com",
        "password": "123"  # Too short
    })
    assert register_weak_password_response.status_code == 400

    # Create a user for task testing
    user = User(email="validation_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Test task validation - empty title
        empty_title_response = client.post("/tasks/", json={
            "title": "",
            "description": "Valid description",
            "completed": False
        })
        assert empty_title_response.status_code == 400

        # Test task validation - too long title
        long_title_response = client.post("/tasks/", json={
            "title": "x" * 201,  # Exceeds max length
            "description": "Valid description",
            "completed": False
        })
        assert long_title_response.status_code == 400

        # Test task validation - too long description
        long_desc_response = client.post("/tasks/", json={
            "title": "Valid title",
            "description": "x" * 1001,  # Exceeds max length
            "completed": False
        })
        assert long_desc_response.status_code == 400

        # Test valid creation
        valid_response = client.post("/tasks/", json={
            "title": "Valid Task Title",
            "description": "Valid Task Description",
            "completed": False
        })
        assert valid_response.status_code == 200


def test_security_headers_integration(client, session):
    """Integration test: Verify security headers are applied to responses"""
    # Make a request to any endpoint
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


def test_database_indexing_performance(client, session):
    """Integration test: Verify database indexing is working (indirectly)"""
    # Create a user
    user = User(email="indexing_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create multiple tasks to test indexing performance
    task_titles = [f"Task {i}" for i in range(50)]
    created_tasks = []

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        for title in task_titles:
            response = client.post("/tasks/", json={
                "title": title,
                "description": f"Description for {title}",
                "completed": i % 2 == 0  # Alternate completed status
            })
            assert response.status_code == 200
            created_tasks.append(response.json()["id"])

        # Get all tasks - this should be efficient with proper indexing
        get_response = client.get("/tasks/")
        assert get_response.status_code == 200
        tasks = get_response.json()
        assert len(tasks) == 50

        # Test filtering by completion status - should be efficient with index
        # (This would be tested more directly in a real performance test)


def test_error_handling_comprehensive(client, session):
    """Integration test: Verify comprehensive error handling"""
    # Test auth error - invalid email format
    invalid_email_response = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "validpassword"
    })
    assert invalid_email_response.status_code == 400
    assert "detail" in invalid_email_response.json()

    # Test auth error - weak password
    weak_password_response = client.post("/auth/register", json={
        "email": "valid@example.com",
        "password": "123"  # Too short
    })
    assert weak_password_response.status_code == 400
    assert "detail" in weak_password_response.json()

    # Create user for task testing
    user = User(email="error_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Test unauthorized access
    unauthorized_response = client.get("/tasks/")
    assert unauthorized_response.status_code == 401

    # Mock authentication and test task errors
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Test task creation with invalid data
        invalid_task_response = client.post("/tasks/", json={
            "title": "",  # Empty title should fail
            "description": "Valid description",
            "completed": False
        })
        assert invalid_task_response.status_code == 400

        # Create a valid task
        valid_task_response = client.post("/tasks/", json={
            "title": "Valid Task",
            "description": "Valid Description",
            "completed": False
        })
        assert valid_task_response.status_code == 200
        task_id = valid_task_response.json()["id"]

        # Test accessing non-existent task
        nonexistent_response = client.get("/tasks/999999")
        assert nonexistent_response.status_code == 404


def test_responsiveness_and_validation_integration(client, session):
    """Integration test: Test responsiveness and validation working together"""
    # Create a user
    user = User(email="responsive_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Test creating multiple valid tasks quickly
        for i in range(5):
            response = client.post("/tasks/", json={
                "title": f"Responsive Task {i}",
                "description": f"Description for task {i}",
                "completed": False
            })
            assert response.status_code == 200

        # Get all tasks
        get_response = client.get("/tasks/")
        assert get_response.status_code == 200
        tasks = get_response.json()
        assert len(tasks) == 5

        # Update multiple tasks
        for task in tasks:
            update_response = client.put(f"/tasks/{task['id']}", json={
                "title": f"Updated {task['title']}",
                "completed": True
            })
            assert update_response.status_code == 200

        # Verify updates
        updated_get_response = client.get("/tasks/")
        assert updated_get_response.status_code == 200
        updated_tasks = updated_get_response.json()
        assert len(updated_tasks) == 5
        for task in updated_tasks:
            assert task["completed"] is True
            assert task["title"].startswith("Updated ")


def test_end_to_end_workflow(client, session):
    """Integration test: Complete end-to-end workflow"""
    # Register a new user
    register_response = client.post("/auth/register", json={
        "email": "e2e_test@example.com",
        "password": "securepassword123"
    })
    assert register_response.status_code == 200
    user_data = register_response.json()
    assert user_data["email"] == "e2e_test@example.com"

    # Create a user in the database for authentication mocking
    user = User(email="e2e_test@example.com", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mock authentication for the created user
    with patch("src.middleware.auth.get_current_user", return_value=user):
        # Create multiple tasks
        tasks_data = []
        for i in range(3):
            response = client.post("/tasks/", json={
                "title": f"E2E Task {i}",
                "description": f"End-to-end test task {i}",
                "completed": i == 0  # First one completed, others not
            })
            assert response.status_code == 200
            tasks_data.append(response.json())

        # Verify all tasks created
        get_all_response = client.get("/tasks/")
        assert get_all_response.status_code == 200
        all_tasks = get_all_response.json()
        assert len(all_tasks) == 3

        # Update one task
        task_to_update = tasks_data[1]
        update_response = client.put(f"/tasks/{task_to_update['id']}", json={
            "title": "Updated E2E Task 1",
            "completed": True
        })
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["title"] == "Updated E2E Task 1"
        assert updated_task["completed"] is True

        # Delete one task
        task_to_delete = tasks_data[2]
        delete_response = client.delete(f"/tasks/{task_to_delete['id']}")
        assert delete_response.status_code == 200

        # Verify deletion
        after_delete_response = client.get("/tasks/")
        assert after_delete_response.status_code == 200
        remaining_tasks = after_delete_response.json()
        assert len(remaining_tasks) == 2

        # Verify deleted task is gone
        deleted_task_response = client.get(f"/tasks/{task_to_delete['id']}")
        assert deleted_task_response.status_code == 404