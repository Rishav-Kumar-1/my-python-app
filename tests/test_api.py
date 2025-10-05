import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import get_db, Base
from backend.models import User, Resume, Job
from backend.auth import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "role": "candidate"
    }

@pytest.fixture
def test_recruiter():
    return {
        "email": "recruiter@example.com",
        "password": "testpassword",
        "full_name": "Test Recruiter",
        "role": "recruiter"
    }

def test_register_user(setup_database, test_user):
    response = client.post("/api/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert "access_token" in data

def test_register_duplicate_user(setup_database, test_user):
    # Register first user
    client.post("/api/register", json=test_user)
    
    # Try to register same user again
    response = client.post("/api/register", json=test_user)
    assert response.status_code == 400
    assert "USER_EXISTS" in response.json()["detail"]["error"]["code"]

def test_login_user(setup_database, test_user):
    # Register user first
    client.post("/api/register", json=test_user)
    
    # Login
    response = client.post("/api/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "access_token" in data

def test_login_invalid_credentials(setup_database, test_user):
    # Register user first
    client.post("/api/register", json=test_user)
    
    # Try to login with wrong password
    response = client.post("/api/login", json={
        "email": test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "INVALID_CREDENTIALS" in response.json()["detail"]["error"]["code"]

def test_upload_resume(setup_database, test_user):
    # Register and login
    register_response = client.post("/api/register", json=test_user)
    token = register_response.json()["access_token"]
    
    # Upload resume
    with open("test_resume.txt", "w") as f:
        f.write("Test resume content")
    
    with open("test_resume.txt", "rb") as f:
        response = client.post(
            "/api/resumes",
            files={"file": ("test_resume.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_resume.txt"
    assert "content" in data

def test_get_resumes(setup_database, test_user):
    # Register and login
    register_response = client.post("/api/register", json=test_user)
    token = register_response.json()["access_token"]
    
    # Get resumes
    response = client.get(
        "/api/resumes",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

def test_create_job(setup_database, test_recruiter):
    # Register and login as recruiter
    register_response = client.post("/api/register", json=test_recruiter)
    token = register_response.json()["access_token"]
    
    # Create job
    job_data = {
        "title": "Software Engineer",
        "description": "We are looking for a software engineer",
        "requirements": "Python, FastAPI, React"
    }
    
    response = client.post(
        "/api/jobs",
        json=job_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["description"] == job_data["description"]

def test_ask_question(setup_database, test_user):
    # Register and login
    register_response = client.post("/api/register", json=test_user)
    token = register_response.json()["access_token"]
    
    # Upload a resume first
    with open("test_resume.txt", "w") as f:
        f.write("John Doe is a Python developer with 5 years of experience")
    
    with open("test_resume.txt", "rb") as f:
        client.post(
            "/api/resumes",
            files={"file": ("test_resume.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Ask question
    response = client.post(
        "/api/ask",
        json={"query": "What programming languages does John know?", "k": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "answer" in data
    assert "evidence" in data

def test_rate_limiting(setup_database, test_user):
    # Register and login
    register_response = client.post("/api/register", json=test_user)
    token = register_response.json()["access_token"]
    
    # Make many requests to trigger rate limit
    for i in range(65):  # More than the 60 req/min limit
        response = client.get(
            "/api/resumes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if i >= 60:
            assert response.status_code == 429
            assert "RATE_LIMIT" in response.json()["detail"]["error"]["code"]
            break

def test_idempotency(setup_database, test_user):
    # Register and login
    register_response = client.post("/api/register", json=test_user)
    token = register_response.json()["access_token"]
    
    idempotency_key = "test-key-123"
    
    # Create job with idempotency key
    job_data = {
        "title": "Test Job",
        "description": "Test description",
        "requirements": "Test requirements"
    }
    
    response1 = client.post(
        "/api/jobs",
        json=job_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idempotency_key
        }
    )
    
    response2 = client.post(
        "/api/jobs",
        json=job_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idempotency_key
        }
    )
    
    # Both responses should return the same job
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["id"] == response2.json()["id"]

if __name__ == "__main__":
    pytest.main([__file__])
