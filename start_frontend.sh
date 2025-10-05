#!/bin/bash

# ResumeRAG Frontend Startup Script

echo "Starting ResumeRAG Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is required but not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is required but not installed."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Set environment variables
export REACT_APP_API_URL=http://localhost:8000

# Start the development server
echo "Starting React development server..."
npm start
