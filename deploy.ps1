# ResumeRAG Deployment Script for Windows
Write-Host "🚀 ResumeRAG Deployment Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check git status
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "❌ You have uncommitted changes. Please commit them first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Git is clean" -ForegroundColor Green

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "🎯 DEPLOYMENT INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. BACKEND DEPLOYMENT:" -ForegroundColor Yellow
Write-Host "   - Go to: https://render.com"
Write-Host "   - Click: New → Web Service"
Write-Host "   - Repository: my-python-app"
Write-Host "   - Build Command: pip install -r requirements.txt"
Write-Host "   - Start Command: python main.py"
Write-Host "   - Environment: SECRET_KEY = resumerag-secret-key-2024"
Write-Host ""
Write-Host "2. FRONTEND DEPLOYMENT:" -ForegroundColor Yellow
Write-Host "   - Go to: https://render.com"
Write-Host "   - Click: New → Static Site"
Write-Host "   - Repository: my-python-app"
Write-Host "   - Root Directory: frontend"
Write-Host "   - Build Command: npm install; npm run build"
Write-Host "   - Publish Directory: build"
Write-Host "   - Environment: REACT_APP_API_URL = https://your-backend-url.onrender.com"
Write-Host ""
Write-Host "✅ Code pushed to GitHub successfully!" -ForegroundColor Green
Write-Host "🌐 Your app is ready for deployment!" -ForegroundColor Green

# Open Render.com in browser
Write-Host ""
Write-Host "🌐 Opening Render.com..." -ForegroundColor Blue
Start-Process 'https://render.com'
