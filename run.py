#!/usr/bin/env python3
"""
ResumeRAG Application Runner
"""
import uvicorn
import os
from backend.main import app

if __name__ == "__main__":
    # Set default environment variables
    os.environ.setdefault("SECRET_KEY", "your-secret-key-here")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./resumerag.db")
    
    # Run the application
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
