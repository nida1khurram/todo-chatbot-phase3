import requests
import time

# Wait a moment for server to start
time.sleep(2)

try:
    response = requests.options(
        'http://localhost:8000/auth/register',
        headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
    )
    print(f"OPTIONS request status: {response.status_code}")
    print(f"CORS headers: {dict(response.headers)}")
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to server - server is not running")
except Exception as e:
    print(f"ERROR: {e}")