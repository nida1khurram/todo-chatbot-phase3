import sys
import os
sys.path.insert(0, './backend')

try:
    from backend.src.main import app
    print("[SUCCESS] Application imported successfully")

    import uvicorn
    print("[SUCCESS] Uvicorn imported successfully")

    # Try to run the server on port 8003
    print("Starting server on http://127.0.0.1:8003...")
    uvicorn.run("backend.src.main:app", host="127.0.0.1", port=8003, log_level="info")

except ImportError as e:
    print(f"[IMPORT ERROR] Error importing app: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()