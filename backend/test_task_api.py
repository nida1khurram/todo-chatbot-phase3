"""
Test script to verify task API endpoints are working properly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_task_operations():
    """Test task API operations"""
    print("Testing Task API endpoints...")

    # First, let's try to register a test user
    print("\n1. Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            print("+ User registration successful")
            user = response.json()
            print(f"  User ID: {user.get('id')}")
        else:
            print(f"x User registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"x Error registering user: {str(e)}")
        return False

    # Now try to login
    print("\n2. Testing user login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
        if response.status_code == 200:
            print("+ User login successful")
            auth_data = response.json()
            token = auth_data.get("access_token")
            print(f"  Token: {token[:20]}..." if token else "No token")
        else:
            print(f"x User login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"x Error logging in user: {str(e)}")
        return False

    # Test creating a task
    print("\n3. Testing task creation...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    task_data = {
        "title": "Test Task",
        "description": "This is a test task created via API"
    }

    try:
        response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
        if response.status_code == 200:
            print("+ Task creation successful")
            task = response.json()
            task_id = task.get("id")
            print(f"  Task ID: {task_id}")
            print(f"  Task Title: {task.get('title')}")
        else:
            print(f"x Task creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"x Error creating task: {str(e)}")
        return False

    # Test getting all tasks
    print("\n4. Testing task retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"+ Task retrieval successful - Found {len(tasks)} tasks")
            for task in tasks:
                print(f"  - Task {task.get('id')}: {task.get('title')}")
        else:
            print(f"x Task retrieval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"x Error retrieving tasks: {str(e)}")
        return False

    # Test updating the task
    print("\n5. Testing task update...")
    update_data = {
        "title": "Updated Test Task",
        "description": "This is an updated test task",
        "completed": True
    }

    try:
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            print("+ Task update successful")
            updated_task = response.json()
            print(f"  Updated Title: {updated_task.get('title')}")
            print(f"  Completed: {updated_task.get('completed')}")
        else:
            print(f"x Task update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"x Error updating task: {str(e)}")
        return False

    # Test deleting the task
    print("\n6. Testing task deletion...")
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
        if response.status_code in [200, 204]:
            print("+ Task deletion successful")
        else:
            print(f"x Task deletion failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"x Error deleting task: {str(e)}")
        return False

    print("\n+ All task operations completed successfully!")
    return True

if __name__ == "__main__":
    test_task_operations()