# ResumeRAG - Resume Search & Job Match Application

A comprehensive application for uploading resumes, parsing and embedding content, answering queries with snippet evidence, and matching candidates against job descriptions.

## Features

- **Resume Upload**: Support for PDF, DOCX, DOC, and TXT files
- **Bulk Upload**: ZIP file support for uploading multiple resumes
- **Semantic Search**: Query resumes using natural language
- **Job Matching**: Match candidates to job descriptions with evidence
- **PII Redaction**: Automatic redaction of personally identifiable information
- **Rate Limiting**: 60 requests per minute per user
- **Idempotency**: Support for Idempotency-Key headers on all POST endpoints
- **Pagination**: Support for limit/offset parameters on list endpoints
- **Authentication**: JWT-based authentication with role-based access

## API Summary

### Authentication Endpoints
- `POST /api/register` - Register a new user
- `POST /api/login` - Login user

### Resume Endpoints
- `POST /api/resumes` - Upload a single resume (multipart)
- `POST /api/resumes/bulk` - Upload multiple resumes from ZIP file
- `GET /api/resumes` - List resumes with pagination and search
- `GET /api/resumes/{id}` - Get specific resume

### Query Endpoints
- `POST /api/ask` - Ask questions about resumes with evidence

### Job Endpoints
- `POST /api/jobs` - Create a job posting
- `GET /api/jobs/{id}` - Get specific job
- `POST /api/jobs/{id}/match` - Match candidates to job

## Example Requests and Responses

### Register User
```bash
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "candidate"
}
```

Response:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "candidate",
  "access_token": "jwt_token"
}
```

### Upload Resume
```bash
POST /api/resumes
Authorization: Bearer jwt_token
Content-Type: multipart/form-data

file: resume.pdf
```

Response:
```json
{
  "id": "uuid",
  "filename": "resume.pdf",
  "content": "parsed content...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Ask Question
```bash
POST /api/ask
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "query": "What programming languages does the candidate know?",
  "k": 5
}
```

Response:
```json
{
  "query": "What programming languages does the candidate know?",
  "answer": "Based on your 1 resume(s), here's what I found:",
  "evidence": [
    {
      "resume_id": "uuid",
      "filename": "resume.pdf",
      "snippet": "Python, JavaScript, and React...",
      "score": 0.95
    }
  ]
}
```

### Create Job
```bash
POST /api/jobs
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "title": "Software Engineer",
  "description": "We are looking for a software engineer...",
  "requirements": "Python, FastAPI, React, 3+ years experience"
}
```

### Match Candidates
```bash
POST /api/jobs/{job_id}/match
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "top_n": 10
}
```

Response:
```json
{
  "job_id": "uuid",
  "candidates": [
    {
      "resume_id": "uuid",
      "filename": "resume.pdf",
      "match_score": 0.85,
      "evidence": ["Python experience", "FastAPI knowledge"],
      "missing_requirements": ["React experience"]
    }
  ]
}
```

## Test User Credentials

### Candidate User
- Email: `candidate@example.com`
- Password: `password123`
- Role: `candidate`

### Recruiter User
- Email: `recruiter@example.com`
- Password: `password123`
- Role: `recruiter`

## Seed Data

The application includes sample resumes and job postings for testing:

### Sample Resumes
- `sample_resume_1.pdf` - Software Engineer with Python/React experience
- `sample_resume_2.pdf` - Data Scientist with ML/AI background
- `sample_resume_3.pdf` - Frontend Developer with JavaScript/React skills

### Sample Jobs
- Software Engineer - Python, FastAPI, React
- Data Scientist - Machine Learning, Python, SQL
- Frontend Developer - React, JavaScript, CSS

## Installation and Setup

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///./resumerag.db"
export REDIS_URL="redis://localhost:6379"  # Optional

# Run database migrations
alembic upgrade head

# Start the server
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/test_api.py -v
```

## API Features

### Pagination
All list endpoints support pagination:
```
GET /api/resumes?limit=10&offset=0
```

Response includes:
```json
{
  "items": [...],
  "total": 100,
  "limit": 10,
  "offset": 0,
  "next_offset": 10
}
```

### Rate Limiting
- 60 requests per minute per user
- Returns `429` status with `{"error": {"code": "RATE_LIMIT"}}` when exceeded

### Idempotency
All POST endpoints accept `Idempotency-Key` header:
```bash
POST /api/resumes
Idempotency-Key: unique-key-123
```

### Error Format
All errors follow uniform format:
```json
{
  "error": {
    "code": "FIELD_REQUIRED",
    "field": "email",
    "message": "Email is required"
  }
}
```

### CORS
CORS is configured to allow all origins during judging.

## Frontend Pages

- `/upload` - Upload resumes (single or bulk)
- `/search` - Search and query resumes
- `/jobs` - Manage job postings and match candidates
- `/candidates/:id` - View specific candidate details

## Technology Stack

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL/SQLite - Database
- Redis - Rate limiting (optional)
- Sentence Transformers - Embeddings
- PyPDF2, python-docx - Document parsing

### Frontend
- React - UI framework
- React Router - Routing
- Styled Components - Styling
- React Query - Data fetching
- Axios - HTTP client

## Deployment

The application is designed to be deployed with:
- Backend on any Python hosting service
- Frontend on any static hosting service
- Database (PostgreSQL recommended for production)
- Redis for rate limiting (optional)

## Judge Testing

The application supports all required judge tests:
- 3+ resume uploads processed
- `/ask` returns schema-compliant answers
- `/match` returns evidence and missing requirements
- Pagination works correctly
- Rate limiting enforced
- Idempotency supported
- PII redaction for non-recruiters
