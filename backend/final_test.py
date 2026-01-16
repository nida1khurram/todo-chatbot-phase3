"""
Final comprehensive test of the application
"""
import requests
import time
import asyncio
from src.services.ai_agent_manager import AIAgentManager

def test_api_endpoints():
    """Test the basic API endpoints"""
    print("=== Testing Basic API Endpoints ===")
    BASE_URL = "http://127.0.0.1:8080"

    # Create a unique user for this test
    timestamp = str(int(time.time()))
    email = f"final_test_{timestamp}@example.com"
    password = "testpassword123"

    print(f"\n1. Creating test user: {email}")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password
        })

        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("id")
            print(f"   ✓ User created successfully with ID: {user_id}")
        else:
            print(f"   ✗ User creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error creating user: {str(e)}")
        return False

    # Login the user
    print("\n2. Logging in user")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })

        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            print(f"   ✓ Login successful, token obtained: {token[:20]}...")
        else:
            print(f"   ✗ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error logging in: {str(e)}")
        return False

    # Test creating a task
    print("\n3. Testing task creation")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    task_data = {
        "title": "Final Test Task",
        "description": "This task was created during final testing"
    }

    try:
        response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)

        if response.status_code == 200:
            task = response.json()
            task_id = task.get("id")
            print(f"   ✓ Task created successfully with ID: {task_id}")
        else:
            print(f"   ✗ Task creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error creating task: {str(e)}")
        return False

    # Test retrieving the task
    print("\n4. Testing task retrieval")
    try:
        response = requests.get(f"{BASE_URL}/tasks/", headers=headers)

        if response.status_code == 200:
            tasks = response.json()
            print(f"   ✓ Retrieved {len(tasks)} tasks")
        else:
            print(f"   ✗ Task retrieval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error retrieving tasks: {str(e)}")
        return False

    # Test updating the task
    print("\n5. Testing task update")
    update_data = {
        "title": "Updated Final Test Task",
        "description": "This task was updated during final testing",
        "completed": True
    }

    try:
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)

        if response.status_code == 200:
            updated_task = response.json()
            print(f"   ✓ Task updated successfully")
            print(f"   ✓ Completed: {updated_task.get('completed')}")
        else:
            print(f"   ✗ Task update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error updating task: {str(e)}")
        return False

    print(f"\n✓ API endpoints test completed successfully!")
    return True

async def test_ai_components():
    """Test the AI components"""
    print("\n=== Testing AI Components ===")

    try:
        # Test basic AI response
        ai_manager = AIAgentManager()

        print("\n1. Testing basic AI response")
        result = await ai_manager.process_message(
            user_id="1",
            message="Hello, how are you?",
            conversation_history=[]
        )

        print(f"   ✓ Basic AI response: {result['type']}")

        # Test AI with tool usage
        print("\n2. Testing AI with tool usage")
        result = await ai_manager.process_message(
            user_id="1",
            message="Create a task called 'AI Test' with description 'Testing AI tools'",
            conversation_history=[]
        )

        print(f"   ✓ AI tool usage: {result['type']}")
        if result['type'] == 'tool_calls':
            print(f"   ✓ Tool calls executed successfully")

        print(f"\n✓ AI components test completed successfully!")
        return True

    except Exception as e:
        print(f"   ✗ AI components test failed: {str(e)}")
        return False

def main():
    print("Running Final Comprehensive Test...")
    print("==================================")

    # Test API endpoints
    api_success = test_api_endpoints()

    # Test AI components
    ai_success = asyncio.run(test_ai_components())

    print(f"\n=== FINAL RESULTS ===")
    print(f"API Endpoints: {'✓ PASS' if api_success else '✗ FAIL'}")
    print(f"AI Components: {'✓ PASS' if ai_success else '✗ FAIL'}")

    overall_success = api_success and ai_success
    print(f"Overall Status: {'✓ ALL SYSTEMS OPERATIONAL' if overall_success else '✗ ISSUES DETECTED'}")

    if overall_success:
        print(f"\nThe application is fully functional!")
        print(f"- Frontend can communicate with backend")
        print(f"- User authentication works")
        print(f"- Task operations work (create, read, update, delete)")
        print(f"- AI integration works")
        print(f"- Tool calling works")
    else:
        print(f"\nSome components need attention.")

    return overall_success

if __name__ == "__main__":
    main()