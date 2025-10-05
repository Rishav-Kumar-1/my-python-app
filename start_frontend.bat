@echo off
REM ResumeRAG Frontend Startup Script for Windows

echo Starting ResumeRAG Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is required but not installed.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd frontend

REM Install dependencies
echo Installing frontend dependencies...
npm install

REM Set environment variables
set REACT_APP_API_URL=http://localhost:8000

REM Start the development server
echo Starting React development server...
npm start

pause
