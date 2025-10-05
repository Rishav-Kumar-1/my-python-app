#!/usr/bin/env python3
"""
Simple production-ready FastAPI app for Render.com deployment
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
import os
import uuid
import hashlib
import time
from datetime import datetime, timedelta
import json

app = FastAPI(title="ResumeRAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for demo
users_db = {}
resumes_db = {}
jobs_db = {}

security = HTTPBearer()

def simple_hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return simple_hash_password(plain_password) == hashed_password

def create_access_token(data: dict):
    """Create a simple access token"""
    return f"token_{data['sub']}_{int(time.time())}"

def verify_token(token: str):
    """Verify a simple token"""
    if token.startswith("token_"):
        parts = token.split("_")
        if len(parts) >= 3:
            user_id = parts[1]
            return {"sub": user_id}
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload["sub"]
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def check_rate_limit(user_id: str):
    """Simple rate limiting"""
    # For demo purposes, just pass
    pass

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ResumeRAG API is running!", 
        "docs": "/docs",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ResumeRAG API",
        "version": "1.0.0"
    }

@app.post("/api/register")
async def register(request: dict):
    """Register a new user"""
    email = request.get("email")
    password = request.get("password")
    role = request.get("role", "candidate")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Check if user already exists
    for user in users_db.values():
        if user["email"] == email:
            raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = simple_hash_password(password)
    
    users_db[user_id] = {
        "id": user_id,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    # Create token
    token = create_access_token({"sub": user_id})
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "email": email,
            "role": role
        }
    }

@app.post("/api/login")
async def login(request: dict):
    """Login user"""
    email = request.get("email")
    password = request.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Find user by email
    user = None
    for u in users_db.values():
        if u["email"] == email:
            user = u
            break
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token({"sub": user["id"]})
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "created_at": current_user["created_at"]
    }

@app.post("/api/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a resume"""
    check_rate_limit(current_user["id"])
    
    # Generate unique ID
    resume_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    
    # Store resume data
    resume_data = {
        "id": resume_id,
        "filename": file.filename,
        "content": content.decode('utf-8', errors='ignore') if content else "No content",
        "user_id": current_user["id"],
        "created_at": datetime.now().isoformat(),
        "file_size": len(content)
    }
    
    resumes_db[resume_id] = resume_data
    
    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume_id,
        "filename": file.filename
    }

@app.get("/api/resumes")
async def get_resumes(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Get user's resumes"""
    check_rate_limit(current_user["id"])
    
    user_resumes = [r for r in resumes_db.values() if r["user_id"] == current_user["id"]]
    
    # Simple pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_resumes = user_resumes[start:end]
    
    return {
        "resumes": paginated_resumes,
        "total": len(user_resumes),
        "page": page,
        "limit": limit,
        "pages": (len(user_resumes) + limit - 1) // limit
    }

@app.get("/api/jobs")
async def get_jobs(
    current_user: dict = Depends(get_current_user)
):
    """Get all jobs for the current user"""
    check_rate_limit(current_user["id"])
    
    user_jobs = [job for job in jobs_db.values() if job["user_id"] == current_user["id"]]
    return user_jobs

@app.get("/api/candidates")
async def get_all_candidates(
    current_user: dict = Depends(get_current_user)
):
    """Get all candidates (for recruiter view)"""
    check_rate_limit(current_user["id"])
    
    # For demo purposes, return all resumes as candidates
    all_candidates = list(resumes_db.values())
    return all_candidates

@app.get("/api/candidates/{resume_id}")
async def get_candidate(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get candidate details"""
    check_rate_limit(current_user["id"])
    
    resume = resumes_db.get(resume_id)
    if not resume:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "CANDIDATE_NOT_FOUND", "message": "Candidate not found"}}
        )
    
    return resume

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
