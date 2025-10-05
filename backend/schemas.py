from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "candidate"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    access_token: str
    
    class Config:
        from_attributes = True

class ResumeUpload(BaseModel):
    filename: str
    content: str

class ResumeResponse(BaseModel):
    id: str
    filename: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str

class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    requirements: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AskRequest(BaseModel):
    query: str
    k: int = 5

class EvidenceItem(BaseModel):
    resume_id: str
    filename: str
    snippet: str
    score: float

class AskResponse(BaseModel):
    query: str
    answer: str
    evidence: List[EvidenceItem]

class MatchRequest(BaseModel):
    top_n: int = 10

class CandidateMatch(BaseModel):
    resume_id: str
    filename: str
    match_score: float
    evidence: List[str]
    missing_requirements: List[str]

class MatchResponse(BaseModel):
    job_id: str
    candidates: List[CandidateMatch]

class ErrorResponse(BaseModel):
    error: Dict[str, Any]

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    limit: int
    offset: int
    next_offset: Optional[int] = None
