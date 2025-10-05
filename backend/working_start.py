#!/usr/bin/env python3
"""
Working backend startup script - no database dependencies
"""
import sys
import os

# Add the parent directory to the path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import from the backend directory
from working_main import app
import uvicorn

if __name__ == "__main__":
    print("Starting ResumeRAG Backend Server (Working Version)...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "working_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
