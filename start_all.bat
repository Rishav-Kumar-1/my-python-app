@echo off
REM ResumeRAG Full Application Startup Script for Windows

echo Starting ResumeRAG Full Application...

REM Start backend in new window
echo Starting backend server...
start "ResumeRAG Backend" cmd /k start_backend.bat

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend
echo Starting frontend server...
start "ResumeRAG Frontend" cmd /k start_frontend.bat

echo Both servers are starting...
echo Backend will be available at http://localhost:8000
echo Frontend will be available at http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
