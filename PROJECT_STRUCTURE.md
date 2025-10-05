# ResumeRAG Project Structure

```
resumerag/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication utilities
│   ├── rate_limiter.py      # Rate limiting implementation
│   ├── resume_parser.py     # Resume parsing logic
│   ├── embedding_service.py # Embedding generation and search
│   └── pii_redactor.py      # PII redaction utilities
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js           # Main React application
│   │   ├── index.js         # React entry point
│   │   ├── contexts/
│   │   │   └── AuthContext.js # Authentication context
│   │   ├── services/
│   │   │   └── api.js       # API client configuration
│   │   ├── components/
│   │   │   └── Navbar.js    # Navigation component
│   │   └── pages/
│   │       ├── Login.js     # Login page
│   │       ├── Register.js   # Registration page
│   │       ├── Upload.js     # Resume upload page
│   │       ├── Search.js     # Search and query page
│   │       ├── Jobs.js       # Job management page
│   │       └── Candidates.js # Candidate details page
│   └── package.json
├── tests/
│   └── test_api.py         # API tests
├── requirements.txt        # Python dependencies
├── run.py                  # Backend runner
├── start_backend.bat       # Windows backend startup
├── start_frontend.bat      # Windows frontend startup
├── start_all.bat          # Windows full app startup
├── env.example            # Environment variables example
├── README.md              # Project documentation
└── PROJECT_STRUCTURE.md   # This file
```

## Key Features Implemented

### Backend (FastAPI)
- ✅ Authentication with JWT tokens
- ✅ Resume upload (single and bulk ZIP)
- ✅ Resume parsing (PDF, DOCX, DOC, TXT)
- ✅ Semantic search with embeddings
- ✅ Job creation and candidate matching
- ✅ Rate limiting (60 req/min/user)
- ✅ Idempotency support
- ✅ Pagination on all list endpoints
- ✅ PII redaction for non-recruiters
- ✅ Uniform error handling
- ✅ CORS configuration

### Frontend (React)
- ✅ Modern UI with styled-components
- ✅ Authentication pages (login/register)
- ✅ Resume upload with drag & drop
- ✅ Search interface with evidence display
- ✅ Job management and candidate matching
- ✅ Candidate detail pages
- ✅ Responsive design
- ✅ Error handling and loading states

### API Endpoints
- ✅ `POST /api/register` - User registration
- ✅ `POST /api/login` - User login
- ✅ `POST /api/resumes` - Upload resume
- ✅ `POST /api/resumes/bulk` - Bulk upload
- ✅ `GET /api/resumes` - List resumes
- ✅ `GET /api/resumes/{id}` - Get resume
- ✅ `POST /api/ask` - Query resumes
- ✅ `POST /api/jobs` - Create job
- ✅ `GET /api/jobs/{id}` - Get job
- ✅ `POST /api/jobs/{id}/match` - Match candidates

### Testing
- ✅ Comprehensive API tests
- ✅ Authentication tests
- ✅ Rate limiting tests
- ✅ Idempotency tests
- ✅ Error handling tests

## Quick Start

### Windows
1. Run `start_all.bat` to start both backend and frontend
2. Backend: http://localhost:8000
3. Frontend: http://localhost:3000

### Manual Start
1. Backend: `python run.py`
2. Frontend: `cd frontend && npm start`

## Test Credentials
- Candidate: `candidate@example.com` / `password123`
- Recruiter: `recruiter@example.com` / `password123`
