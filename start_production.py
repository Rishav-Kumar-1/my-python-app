#!/usr/bin/env python3
"""
Production startup script for Render.com deployment
"""
import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print(f"Python path: {sys.path}")
print(f"Backend path: {backend_path}")
print(f"Current directory: {os.getcwd()}")

try:
    from working_main import app
    print("✅ Successfully imported working_main")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    try:
        import backend.working_main as working_main
        app = working_main.app
        print("✅ Successfully imported via backend.working_main")
    except ImportError as e2:
        print(f"❌ Alternative import failed: {e2}")
        sys.exit(1)

import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting ResumeRAG Backend Server on port {port}...")
    print("🌐 API will be available at the Render URL")
    print("📚 API Documentation: /docs")
    print("🔧 Environment: Production")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
