#!/usr/bin/env python3
"""
Test script to verify MCP tool access controls and user isolation
This script tests that users can only access their own tasks
"""

import sys
import os

# Add the backend src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.mcp_server.server import TodoMCPTools, MockAuthService
from src.database import engine
from src.models.task import Task
from sqlmodel import SQLModel
from sqlmodel import Session


def setup_test_database():
    """Set up a test database with sample data"""
    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create a session
    with Session(engine) as session:

        # Clear any existing tasks
        session.query(Task).delete()
        session.commit()

        # Create test tasks for user 1
        task1 = Task(user_id=1, title="User 1 Task 1", description="Task for user 1", completed=False)
        task2 = Task(user_id=1, title="User 1 Task 2", description="Another task for user 1", completed=True)
        session.add(task1)
        session.add(task2)

        # Create test tasks for user 2
        task3 = Task(user_id=2, title="User 2 Task 1", description="Task for user 2", completed=False)
        task4 = Task(user_id=2, title="User 2 Task 2", description="Another task for user 2", completed=False)
        session.add(task3)
        session.add(task4)

        session.commit()

    print("Test database setup complete with sample tasks")


def test_user_isolation():
    """Test that users can only access their own tasks"""
    print("\n=== Testing User Isolation ===")

    # Initialize MCP tools with a session
    session = SessionLocal()
    tools = TodoMCPTools(session)

    # Test 1: User 1 should only see their own tasks
    print("\n1. Testing list_tasks for user 1:")
    try:
        result = tools.list_tasks({"user_id": "1", "status": "all"})
        print(f"   User 1 tasks: {result}")
        assert len(result) == 2, f"Expected 2 tasks for user 1, got {len(result)}"
        for task in result:
            assert task["user_id"] == 1, f"Task belongs to user {task['user_id']}, not user 1"
        print("   ✓ User 1 can only see their own tasks")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: User 2 should only see their own tasks
    print("\n2. Testing list_tasks for user 2:")
    try:
        result = tools.list_tasks({"user_id": "2", "status": "all"})
        print(f"   User 2 tasks: {result}")
        assert len(result) == 2, f"Expected 2 tasks for user 2, got {len(result)}"
        for task in result:
            assert task["user_id"] == 2, f"Task belongs to user {task['user_id']}, not user 2"
        print("   ✓ User 2 can only see their own tasks")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: User 1 should not be able to access user 2's tasks
    print("\n3. Testing cross-user access attempt (should fail):")
    try:
        # Try to complete user 2's task as user 1 (should fail)
        result = tools.complete_task({"user_id": "1", "task_id": 3})  # task_id 3 belongs to user 2
        print(f"   ✗ Unexpected success: {result}")
        print("   ✗ User 1 was able to access user 2's task (security breach!)")
    except ValueError as e:
        if "not found for user" in str(e):
            print(f"   ✓ Correctly blocked cross-user access: {e}")
        else:
            print(f"   ? Different error than expected: {e}")
    except Exception as e:
        print(f"   ? Unexpected error type: {e}")

    # Test 4: User 2 should not be able to access user 1's tasks
    print("\n4. Testing reverse cross-user access attempt (should fail):")
    try:
        # Try to delete user 1's task as user 2 (should fail)
        result = tools.delete_task({"user_id": "2", "task_id": 1})  # task_id 1 belongs to user 1
        print(f"   ✗ Unexpected success: {result}")
        print("   ✗ User 2 was able to access user 1's task (security breach!)")
    except ValueError as e:
        if "not found for user" in str(e):
            print(f"   ✓ Correctly blocked cross-user access: {e}")
        else:
            print(f"   ? Different error than expected: {e}")
    except Exception as e:
        print(f"   ? Unexpected error type: {e}")

    # Test 5: Invalid user ID should be rejected
    print("\n5. Testing invalid user access:")
    try:
        result = tools.list_tasks({"user_id": "999", "status": "all"})  # Non-existent user
        print(f"   User 999 tasks: {result} (should be empty or error)")
        # Since we're using a mock auth service that only checks if user_id > 0, this might work
        # Let's verify the mock auth behavior
        auth_service = MockAuthService()
        is_valid = auth_service.validate_user("999")
        print(f"   Mock auth validation for user 999: {is_valid}")
        if not is_valid:
            print("   ✗ User 999 should not be valid")
        else:
            print("   ✓ User 999 is valid according to mock auth (no tasks expected)")
    except Exception as e:
        print(f"   Error: {e}")

    session.close()


def test_valid_operations():
    """Test that valid operations work correctly"""
    print("\n=== Testing Valid Operations ===")

    # Reset the database to known state
    setup_test_database()

    session = SessionLocal()
    tools = TodoMCPTools(session)

    # Test adding a task for user 1
    print("\n1. Testing add_task:")
    try:
        result = tools.add_task({
            "user_id": "1",
            "title": "New task for user 1",
            "description": "Added via MCP tool"
        })
        print(f"   Add task result: {result}")
        assert result["status"] == "created"
        assert result["title"] == "New task for user 1"
        print("   ✓ Task added successfully for user 1")
    except Exception as e:
        print(f"   ✗ Error adding task: {e}")

    # Verify the task was added for the correct user
    print("\n2. Verifying task was added correctly:")
    try:
        result = tools.list_tasks({"user_id": "1", "status": "all"})
        print(f"   User 1 now has {len(result)} tasks")
        new_task_found = any(task["title"] == "New task for user 1" for task in result)
        if new_task_found:
            print("   ✓ New task appears in user 1's list")
        else:
            print("   ✗ New task not found in user 1's list")
    except Exception as e:
        print(f"   ✗ Error verifying task: {e}")

    # Test updating a task
    print("\n3. Testing update_task:")
    try:
        # First, find the ID of the task we just added
        all_tasks = tools.list_tasks({"user_id": "1", "status": "all"})
        task_to_update = next((t for t in all_tasks if t["title"] == "New task for user 1"), None)

        if task_to_update:
            result = tools.update_task({
                "user_id": "1",
                "task_id": task_to_update["id"],
                "title": "Updated task for user 1",
                "description": "Updated description"
            })
            print(f"   Update result: {result}")
            assert result["status"] == "updated"
            print("   ✓ Task updated successfully")
        else:
            print("   ✗ Could not find task to update")
    except Exception as e:
        print(f"   ✗ Error updating task: {e}")

    session.close()


def run_tests():
    """Run all tests"""
    print("Starting MCP Access Control Tests")
    print("=" * 50)

    setup_test_database()
    test_user_isolation()
    test_valid_operations()

    print("\n" + "=" * 50)
    print("MCP Access Control Tests Complete")


if __name__ == "__main__":
    run_tests()