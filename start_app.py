#!/usr/bin/env python3
"""
ResumeRAG Application Startup Script
"""
import subprocess
import sys
import os
import time
import threading
import webbrowser

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting ResumeRAG Backend...")
    os.chdir("backend")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def start_frontend():
    """Start the React frontend server"""
    print("🎨 Starting ResumeRAG Frontend...")
    os.chdir("../frontend")
    try:
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Frontend stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    print("🎯 ResumeRAG Application Starting...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the project root directory")
        print("   Make sure 'backend' and 'frontend' folders exist")
        return
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    print("\n✅ ResumeRAG is starting up!")
    print("🌐 Backend API: http://localhost:8000")
    print("🎨 Frontend UI: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n⏳ Opening browser in 10 seconds...")
    
    # Wait and open browser
    time.sleep(10)
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass
    
    print("\n🔄 Press Ctrl+C to stop both servers")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down ResumeRAG...")
        print("✅ Goodbye!")

if __name__ == "__main__":
    main()
