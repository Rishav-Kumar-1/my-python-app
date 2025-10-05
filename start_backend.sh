#!/bin/bash

# ResumeRAG Backend Startup Script

echo "Starting ResumeRAG Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Set environment variables
export SECRET_KEY="resumerag-secret-key-2024"
export DATABASE_URL="sqlite:///./resumerag.db"

# Create database tables
echo "Setting up database..."
python3 -c "
from backend.database import engine, Base
from backend.models import *
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Start the server
echo "Starting FastAPI server..."
python3 run.py
