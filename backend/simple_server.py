import uvicorn
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

# Change to backend directory
os.chdir('..')

try:
    # Import the app
    from src.main import app
    print("App imported successfully")
    
    # Run the server
    print("Starting server on http://127.0.0.1:8000")
    uvicorn.run(
        "src.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()