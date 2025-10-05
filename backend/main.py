from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
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

from database import get_db, engine, Base
from models import User, Resume, Job, ResumeEmbedding, UserRole
from schemas import (
    UserCreate, UserLogin, UserResponse, ResumeResponse, ResumeUpload,
    JobCreate, JobResponse, AskRequest, AskResponse, MatchRequest, MatchResponse,
    ErrorResponse, PaginatedResponse
)
from auth import create_access_token, verify_token, get_password_hash, verify_password
from rate_limiter import RateLimiter
from resume_parser import ResumeParser
from embedding_service import EmbeddingService
from pii_redactor import PIIRedactor

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResumeRAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open during judging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
rate_limiter = RateLimiter()
security = HTTPBearer()

# Services
resume_parser = ResumeParser()
embedding_service = EmbeddingService()
pii_redactor = PIIRedactor()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def check_rate_limit(user_id: str):
    """Check rate limit for user"""
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail={"error": {"code": "RATE_LIMIT", "message": "Rate limit exceeded"}}
        )

@app.post("/api/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "USER_EXISTS", "message": "User already exists"}}
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.RECRUITER if user_data.role == "recruiter" else UserRole.CANDIDATE
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        access_token=access_token
    )

@app.post("/api/login", response_model=UserResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid credentials"}}
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        access_token=access_token
    )

@app.post("/api/resumes", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume file"""
    check_rate_limit(str(current_user.id))
    
    # Check idempotency
    if idempotency_key:
        existing_resume = db.query(Resume).filter(
            Resume.idempotency_key == idempotency_key,
            Resume.user_id == current_user.id
        ).first()
        if existing_resume:
            return ResumeResponse.from_orm(existing_resume)
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": "Only PDF, DOCX, DOC, and TXT files are allowed"}}
        )
    
    # Read file content
    content = await file.read()
    
    # Parse resume content
    parsed_content = resume_parser.parse(content, file.filename)
    
    # Create resume record
    resume = Resume(
        filename=file.filename,
        content=parsed_content,
        user_id=current_user.id,
        idempotency_key=idempotency_key
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    # Generate embeddings asynchronously
    embedding_service.generate_embeddings_async(str(resume.id), parsed_content)
    
    return ResumeResponse.from_orm(resume)

@app.post("/api/resumes/bulk", response_model=List[ResumeResponse])
async def upload_resumes_bulk(
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple resumes from ZIP file"""
    check_rate_limit(str(current_user.id))
    
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": "Only ZIP files are allowed for bulk upload"}}
        )
    
    content = await file.read()
    resumes = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            for filename in zip_file.namelist():
                if filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
                    file_content = zip_file.read(filename)
                    parsed_content = resume_parser.parse(file_content, filename)
                    
                    resume = Resume(
                        filename=filename,
                        content=parsed_content,
                        user_id=current_user.id,
                        idempotency_key=idempotency_key
                    )
                    
                    db.add(resume)
                    resumes.append(resume)
        
        db.commit()
        
        # Generate embeddings for all resumes
        for resume in resumes:
            db.refresh(resume)
            embedding_service.generate_embeddings_async(str(resume.id), resume.content)
        
        return [ResumeResponse.from_orm(resume) for resume in resumes]
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "BULK_UPLOAD_ERROR", "message": f"Error processing ZIP file: {str(e)}"}}
        )

@app.get("/api/resumes", response_model=PaginatedResponse)
async def get_resumes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resumes with pagination and search"""
    check_rate_limit(str(current_user.id))
    
    query = db.query(Resume).filter(Resume.user_id == current_user.id)
    
    if q:
        # Simple text search in content
        query = query.filter(Resume.content.ilike(f"%{q}%"))
    
    total = query.count()
    resumes = query.offset(offset).limit(limit).all()
    
    # Redact PII if user is not a recruiter
    resume_responses = []
    for resume in resumes:
        response = ResumeResponse.from_orm(resume)
        if current_user.role != UserRole.RECRUITER:
            response.content = pii_redactor.redact(response.content)
        resume_responses.append(response)
    
    next_offset = offset + limit if offset + limit < total else None
    
    return PaginatedResponse(
        items=resume_responses,
        total=total,
        limit=limit,
        offset=offset,
        next_offset=next_offset
    )

@app.get("/api/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume"""
    check_rate_limit(str(current_user.id))
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "Resume not found"}}
        )
    
    response = ResumeResponse.from_orm(resume)
    
    # Redact PII if user is not a recruiter
    if current_user.role != UserRole.RECRUITER:
        response.content = pii_redactor.redact(response.content)
    
    return response

@app.post("/api/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about resumes"""
    check_rate_limit(str(current_user.id))
    
    # Get user's resumes
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    
    if not resumes:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NO_RESUMES", "message": "No resumes found"}}
        )
    
    # Search for relevant content
    results = embedding_service.search(request.query, [str(r.id) for r in resumes], request.k)
    
    # Format response with evidence
    answer = f"Based on your {len(resumes)} resume(s), here's what I found:"
    evidence = []
    
    for result in results:
        resume = next(r for r in resumes if str(r.id) == result['resume_id'])
        evidence.append({
            "resume_id": str(resume.id),
            "filename": resume.filename,
            "snippet": result['snippet'],
            "score": result['score']
        })
    
    return AskResponse(
        query=request.query,
        answer=answer,
        evidence=evidence
    )

@app.post("/api/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    check_rate_limit(str(current_user.id))
    
    # Check idempotency
    if idempotency_key:
        existing_job = db.query(Job).filter(
            Job.idempotency_key == idempotency_key,
            Job.user_id == current_user.id
        ).first()
        if existing_job:
            return JobResponse.from_orm(existing_job)
    
    job = Job(
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        user_id=current_user.id,
        idempotency_key=idempotency_key
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return JobResponse.from_orm(job)

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job"""
    check_rate_limit(str(current_user.id))
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "JOB_NOT_FOUND", "message": "Job not found"}}
        )
    
    return JobResponse.from_orm(job)

@app.post("/api/jobs/{job_id}/match", response_model=MatchResponse)
async def match_candidates(
    job_id: str,
    request: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Match candidates to a job"""
    check_rate_limit(str(current_user.id))
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "JOB_NOT_FOUND", "message": "Job not found"}}
        )
    
    # Get all resumes
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    
    if not resumes:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NO_RESUMES", "message": "No resumes found"}}
        )
    
    # Match candidates
    matches = embedding_service.match_job_to_resumes(
        job.description + " " + job.requirements,
        [str(r.id) for r in resumes],
        request.top_n
    )
    
    # Format response
    candidates = []
    for match in matches:
        resume = next(r for r in resumes if str(r.id) == match['resume_id'])
        candidates.append({
            "resume_id": str(resume.id),
            "filename": resume.filename,
            "match_score": match['score'],
            "evidence": match['evidence'],
            "missing_requirements": match['missing_requirements']
        })
    
    return MatchResponse(
        job_id=job_id,
        candidates=candidates
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
