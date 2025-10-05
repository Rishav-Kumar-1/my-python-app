#!/usr/bin/env python3
"""
Production startup script for Render.com deployment
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from working_main import app
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting ResumeRAG Backend Server on port {port}...")
    print("API will be available at the Render URL")
    print("API Documentation: /docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
