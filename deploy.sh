#!/bin/bash

echo "🚀 ResumeRAG Deployment Script"
echo "================================"

# Check if git is clean
if [[ -n $(git status -s) ]]; then
    echo "❌ You have uncommitted changes. Please commit them first."
    exit 1
fi

echo "✅ Git is clean"

# Push latest changes
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "🎯 DEPLOYMENT INSTRUCTIONS:"
echo "=========================="
echo ""
echo "1. BACKEND DEPLOYMENT:"
echo "   - Go to: https://render.com"
echo "   - Click: New → Web Service"
echo "   - Repository: my-python-app"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python main.py"
echo "   - Environment: SECRET_KEY = resumerag-secret-key-2024"
echo ""
echo "2. FRONTEND DEPLOYMENT:"
echo "   - Go to: https://render.com"
echo "   - Click: New → Static Site"
echo "   - Repository: my-python-app"
echo "   - Root Directory: frontend"
echo "   - Build Command: npm install && npm run build"
echo "   - Publish Directory: build"
echo "   - Environment: REACT_APP_API_URL = https://your-backend-url.onrender.com"
echo ""
echo "✅ Code pushed to GitHub successfully!"
echo "🌐 Your app is ready for deployment!"
