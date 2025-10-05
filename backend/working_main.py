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
import zipfile
import io
from pathlib import Path

app = FastAPI(title="ResumeRAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open during judging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for demo
users_db = {}
resumes_db = {}
jobs_db = {}
current_user_id = None

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
            return {"sub": parts[1]}
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def check_rate_limit(user_id: str):
    """Simple rate limiting"""
    # For demo purposes, we'll skip rate limiting
    return True

@app.post("/api/register")
async def register(user_data: dict):
    """Register a new user"""
    email = user_data.get("email")
    password = user_data.get("password")
    full_name = user_data.get("full_name")
    role = user_data.get("role", "candidate")
    
    if not email or not password or not full_name:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "MISSING_FIELDS", "message": "Email, password, and full_name are required"}}
        )
    
    # Check if user already exists
    for user in users_db.values():
        if user["email"] == email:
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "USER_EXISTS", "message": "User already exists"}}
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "hashed_password": simple_hash_password(password)
    }
    
    users_db[user_id] = user
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "id": user_id,
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "access_token": access_token
    }

@app.post("/api/login")
async def login(login_data: dict):
    """Login user"""
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "MISSING_FIELDS", "message": "Email and password are required"}}
        )
    
    # Find user
    user = None
    for u in users_db.values():
        if u["email"] == email:
            user = u
            break
    
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid credentials"}}
        )
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "access_token": access_token
    }

@app.post("/api/resumes")
async def upload_resume(
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: dict = Depends(get_current_user)
):
    """Upload a resume file"""
    check_rate_limit(current_user["id"])
    
    # Check idempotency
    if idempotency_key:
        for resume in resumes_db.values():
            if resume.get("idempotency_key") == idempotency_key and resume["user_id"] == current_user["id"]:
                return resume
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": "Only PDF, DOCX, DOC, and TXT files are allowed"}}
        )
    
    # Read file content
    content = await file.read()
    
    # Simple content parsing (just decode as text for demo)
    try:
        parsed_content = content.decode('utf-8')
    except:
        parsed_content = f"Binary file content: {file.filename}"
    
    # Create resume record
    resume_id = str(uuid.uuid4())
    resume = {
        "id": resume_id,
        "filename": file.filename,
        "content": parsed_content,
        "user_id": current_user["id"],
        "idempotency_key": idempotency_key,
        "created_at": datetime.utcnow().isoformat()
    }
    
    resumes_db[resume_id] = resume
    
    return resume

@app.get("/api/resumes")
async def get_resumes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get resumes with pagination and search"""
    check_rate_limit(current_user["id"])
    
    # Filter resumes by user
    user_resumes = [r for r in resumes_db.values() if r["user_id"] == current_user["id"]]
    
    # Apply search filter
    if q:
        user_resumes = [r for r in user_resumes if q.lower() in r["content"].lower()]
    
    total = len(user_resumes)
    resumes = user_resumes[offset:offset + limit]
    
    next_offset = offset + limit if offset + limit < total else None
    
    return {
        "items": resumes,
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": next_offset
    }

@app.get("/api/resumes/{resume_id}")
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific resume"""
    check_rate_limit(current_user["id"])
    
    resume = resumes_db.get(resume_id)
    if not resume or resume["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "Resume not found"}}
        )
    
    return resume

@app.get("/api/candidates")
async def get_all_candidates(
    current_user: dict = Depends(get_current_user)
):
    """Get all candidates (for recruiter view)"""
    check_rate_limit(current_user["id"])
    
    # For demo purposes, return all resumes as candidates
    # In a real app, you'd filter based on permissions
    all_candidates = list(resumes_db.values())
    return all_candidates

@app.get("/api/candidates/{resume_id}")
async def get_candidate(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get candidate details (for job matching results)"""
    check_rate_limit(current_user["id"])
    
    resume = resumes_db.get(resume_id)
    if not resume:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "CANDIDATE_NOT_FOUND", "message": "Candidate not found"}}
        )
    
    # For demo purposes, allow viewing any candidate
    # In a real app, you'd check if the user has permission to view this candidate
    return resume

@app.post("/api/ask")
async def ask_question(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Ask a question about resumes"""
    check_rate_limit(current_user["id"])
    
    query = request.get("query", "")
    k = request.get("k", 5)
    
    # Get user's resumes
    user_resumes = [r for r in resumes_db.values() if r["user_id"] == current_user["id"]]
    
    if not user_resumes:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NO_RESUMES", "message": "No resumes found"}}
        )
    
    # Simple text search for relevant content
    evidence = []
    for resume in user_resumes:
        content = resume["content"].lower()
        query_lower = query.lower()
        
        if query_lower in content:
            # Find the relevant snippet
            start = content.find(query_lower)
            snippet_start = max(0, start - 100)
            snippet_end = min(len(resume["content"]), start + len(query) + 100)
            snippet = resume["content"][snippet_start:snippet_end]
            
            evidence.append({
                "resume_id": resume["id"],
                "filename": resume["filename"],
                "snippet": snippet,
                "score": 0.8  # Simple score
            })
    
    answer = f"Based on your {len(user_resumes)} resume(s), here's what I found:"
    
    return {
        "query": query,
        "answer": answer,
        "evidence": evidence[:k]
    }

@app.post("/api/jobs")
async def create_job(
    job_data: dict,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job posting"""
    check_rate_limit(current_user["id"])
    
    title = job_data.get("title")
    description = job_data.get("description")
    requirements = job_data.get("requirements")
    
    if not title or not description or not requirements:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "MISSING_FIELDS", "message": "Title, description, and requirements are required"}}
        )
    
    # Check idempotency
    if idempotency_key:
        for job in jobs_db.values():
            if job.get("idempotency_key") == idempotency_key and job["user_id"] == current_user["id"]:
                return job
    
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "title": title,
        "description": description,
        "requirements": requirements,
        "user_id": current_user["id"],
        "idempotency_key": idempotency_key,
        "created_at": datetime.utcnow().isoformat()
    }
    
    jobs_db[job_id] = job
    
    return job

@app.get("/api/jobs")
async def get_jobs(
    current_user: dict = Depends(get_current_user)
):
    """Get all jobs for the current user"""
    check_rate_limit(current_user["id"])
    
    user_jobs = [job for job in jobs_db.values() if job["user_id"] == current_user["id"]]
    return user_jobs

@app.get("/api/jobs/{job_id}")
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific job"""
    check_rate_limit(current_user["id"])
    
    job = jobs_db.get(job_id)
    if not job or job["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "JOB_NOT_FOUND", "message": "Job not found"}}
        )
    
    return job

@app.post("/api/jobs/{job_id}/match")
async def match_candidates(
    job_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Match candidates to a job"""
    check_rate_limit(current_user["id"])
    
    job = jobs_db.get(job_id)
    if not job or job["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "JOB_NOT_FOUND", "message": "Job not found"}}
        )
    
    # Get all resumes
    user_resumes = [r for r in resumes_db.values() if r["user_id"] == current_user["id"]]
    
    if not user_resumes:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NO_RESUMES", "message": "No resumes found"}}
        )
    
    # Simple matching based on keyword overlap
    candidates = []
    job_text = (job["description"] + " " + job["requirements"]).lower()
    job_keywords = set(job_text.split())
    
    for resume in user_resumes:
        resume_text = resume["content"].lower()
        resume_keywords = set(resume_text.split())
        
        # Calculate simple overlap score
        overlap = len(job_keywords.intersection(resume_keywords))
        total_keywords = len(job_keywords.union(resume_keywords))
        score = overlap / total_keywords if total_keywords > 0 else 0
        
        # Find evidence snippets
        evidence = []
        for keyword in list(job_keywords)[:5]:  # Top 5 keywords
            if keyword in resume_text:
                start = resume_text.find(keyword)
                snippet_start = max(0, start - 50)
                snippet_end = min(len(resume["content"]), start + len(keyword) + 50)
                evidence.append(resume["content"][snippet_start:snippet_end])
        
        # Find missing requirements
        missing = list(job_keywords - resume_keywords)[:5]
        
        candidates.append({
            "resume_id": resume["id"],
            "filename": resume["filename"],
            "match_score": score,
            "evidence": evidence[:3],
            "missing_requirements": missing
        })
    
    # Sort by score
    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    
    top_n = request.get("top_n", 10)
    
    return {
        "job_id": job_id,
        "candidates": candidates[:top_n]
    }

@app.get("/")
async def root():
    return {"message": "ResumeRAG API is running!", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
