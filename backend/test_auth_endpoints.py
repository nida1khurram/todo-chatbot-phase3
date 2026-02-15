#!/usr/bin/env python3
"""
Test script to verify authentication endpoints are working properly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test the registration endpoint"""
    print("Testing registration endpoint...")

    # Create a test user
    test_email = "testuser@example.com"
    test_password = "password123"

    register_data = {
        "email": test_email,
        "password": test_password
    }

    print(f"Sending registration data: {register_data}")

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            print("[SUCCESS] Registration successful!")
            user_data = response.json()
            print(f"User created: {user_data}")
            return True
        elif response.status_code == 400:
            error_data = response.json()
            print(f"[ERROR] Registration failed with validation error: {error_data}")
            return False
        else:
            error_data = response.json()
            print(f"[ERROR] Registration failed with status {response.status_code}: {error_data}")
            return False
    except Exception as e:
        print(f"[ERROR] Error during registration test: {e}")
        return False

def test_login():
    """Test the login endpoint"""
    print("\nTesting login endpoint...")

    login_data = {
        "email": "testuser@example.com",
        "password": "password123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")

        if response.status_code == 200:
            print("[SUCCESS] Login successful!")
            token_data = response.json()
            print(f"Token received: {token_data}")
            return True
        else:
            error_data = response.json()
            print(f"[ERROR] Login failed with status {response.status_code}: {error_data}")
            return False
    except Exception as e:
        print(f"[ERROR] Error during login test: {e}")
        return False

def test_health():
    """Test the health endpoint to ensure server is running"""
    print("\nTesting health endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check status: {response.status_code}")

        if response.status_code == 200:
            health_data = response.json()
            print(f"[SUCCESS] Health check passed: {health_data}")
            return True
        else:
            print("[ERROR] Health check failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error during health check: {e}")
        return False

if __name__ == "__main__":
    print("Testing authentication endpoints...\n")

    # First check if the server is running
    if test_health():
        # Test registration
        if test_register():
            # Test login if registration succeeded
            test_login()
    else:
        print("\nServer is not accessible. Please make sure the backend is running on http://localhost:8000")