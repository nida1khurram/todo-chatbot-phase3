import sys
import os
sys.path.insert(0, '.')

# Change to backend directory
os.chdir('backend')

try:
    from src.main import app
    print("[SUCCESS] Application imported successfully")

    import uvicorn
    print("[SUCCESS] Uvicorn imported successfully")
    
    # Try to run the server
    print("Starting server on http://127.0.0.1:8000...")
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, log_level="info")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()