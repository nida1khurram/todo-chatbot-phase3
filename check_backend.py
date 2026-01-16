#!/usr/bin/env python3
"""
Script to check if the backend server is running with proper CORS configuration
"""

import requests
import subprocess
import time
import sys
import os

def check_backend_running():
    """Check if backend is accessible"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Backend server is running and accessible")
            return True
        else:
            print(f"[ERROR] Backend server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Backend server is not running or not accessible on port 8000")
        return False
    except Exception as e:
        print(f"[ERROR] Error connecting to backend: {e}")
        return False

def restart_backend():
    """Provide instructions to restart the backend server"""
    print("\nTo fix the CORS issue, please restart the backend server:")
    print("1. Stop the current backend server (if running)")
    print("2. Navigate to the backend directory:")
    print("   cd todo2-chatbot/backend")
    print("3. Restart the server:")
    print("   uvicorn src.main:app --reload")
    print("4. Keep the server running while using the frontend")

if __name__ == "__main__":
    print("Checking backend server status...")

    if not check_backend_running():
        print("\nThe backend server needs to be started/restarted.")
        restart_backend()
    else:
        print("\nBackend server is running. Checking CORS configuration...")
        print("The CORS policy should allow requests from http://localhost:3000")
        print("If you're still getting CORS errors, restart the backend server.")
        restart_backend()