@echo off
REM ResumeRAG Backend Startup Script for Windows

echo Starting ResumeRAG Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not installed.
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Set environment variables
set SECRET_KEY=resumerag-secret-key-2024
set DATABASE_URL=sqlite:///./resumerag.db

REM Create database tables
echo Setting up database...
python -c "from backend.database import engine, Base; from backend.models import *; Base.metadata.create_all(bind=engine); print('Database tables created successfully!')"

REM Start the server
echo Starting FastAPI server...
python run.py

pause
