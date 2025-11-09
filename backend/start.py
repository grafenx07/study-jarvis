"""
Start script for Study Jarvis backend
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))

    print("🚀 Starting Study Jarvis Backend...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📖 API docs at: http://127.0.0.1:8000/docs")
    print("\n⏳ Initializing... (this may take a moment)\n")

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
