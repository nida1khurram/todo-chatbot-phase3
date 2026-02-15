import sys
import traceback
from src.main import app
import uvicorn

if __name__ == "__main__":
    try:
        print("Starting server...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)