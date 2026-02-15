import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from datetime import datetime
from src.models.user import User
from src.models.task import Task
from src.services.task_service import (
    create_task, get_tasks, get_task, get_task_for_user,
    check_task_ownership, update_task, delete_task
)


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


@pytest.fixture(name="user")
def user_fixture(session):
    """Create a test user"""
    user_data = User(
        email="test@example.com",
        password_hash="$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D",
        is_active=True
    )
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


def test_create_task(session, user):
    """Test creating a new task"""
    task_data = Task(
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id=user.id
    )

    created_task = create_task(session, task_data)

    assert created_task.title == "Test Task"
    assert created_task.description == "Test Description"
    assert created_task.completed is False
    assert created_task.user_id == user.id
    assert created_task.id is not None


def test_get_tasks(session, user):
    """Test getting all tasks for a user"""
    # Create multiple tasks for the user
    task1 = Task(title="Task 1", description="Desc 1", completed=False, user_id=user.id)
    task2 = Task(title="Task 2", description="Desc 2", completed=True, user_id=user.id)

    session.add(task1)
    session.add(task2)
    session.commit()

    tasks = get_tasks(session, user.id)

    assert len(tasks) == 2
    titles = {task.title for task in tasks}
    assert "Task 1" in titles
    assert "Task 2" in titles


def test_get_task(session, user):
    """Test getting a specific task by ID"""
    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    retrieved_task = get_task(session, task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.title == task.title


def test_get_task_not_found(session):
    """Test getting a non-existent task"""
    retrieved_task = get_task(session, 999)
    assert retrieved_task is None


def test_get_task_for_user(session, user):
    """Test getting a task for a specific user"""
    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    retrieved_task = get_task_for_user(session, task.id, user.id)

    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.user_id == user.id


def test_get_task_for_user_wrong_user(session, user):
    """Test getting a task for a different user (should return None)"""
    # Create another user
    other_user = User(
        email="other@example.com",
        password_hash="$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D",
        is_active=True
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Create task for first user
    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Try to get the task for the other user
    retrieved_task = get_task_for_user(session, task.id, other_user.id)

    assert retrieved_task is None


def test_check_task_ownership(session, user):
    """Test checking task ownership"""
    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    is_owner = check_task_ownership(session, task.id, user.id)

    assert is_owner is True


def test_check_task_ownership_not_owner(session, user):
    """Test checking ownership for a task owned by another user"""
    # Create another user
    other_user = User(
        email="other@example.com",
        password_hash="$2b$12$KIX4pQ4/KIX4pQ4KIX4pQeODN4O7D5O7D5O7D5O7D5O7D5O7D5O7D",
        is_active=True
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Create task for first user
    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Check ownership for other user
    is_owner = check_task_ownership(session, task.id, other_user.id)

    assert is_owner is False


def test_update_task(session, user):
    """Test updating a task"""
    task = Task(title="Original Title", description="Original Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Update the task
    task.title = "Updated Title"
    task.description = "Updated Description"
    task.completed = True

    updated_task = update_task(session, task)

    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated Description"
    assert updated_task.completed is True
    assert updated_task.id == task.id


def test_delete_task(session, user):
    """Test deleting a task"""
    task = Task(title="Test Task", description="Test Description", completed=False, user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    result = delete_task(session, task.id)

    assert result is True

    # Verify the task was deleted
    deleted_task = get_task(session, task.id)
    assert deleted_task is None


def test_delete_task_not_found(session):
    """Test deleting a non-existent task"""
    result = delete_task(session, 999)
    assert result is False