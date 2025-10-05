#!/usr/bin/env python3
"""
Simple database fix without bcrypt issues
"""
import sys
import os
import hashlib

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, Base
from models import User, Resume, Job, ResumeEmbedding, UserRole
from sqlalchemy.orm import sessionmaker

def simple_hash_password(password):
    """Simple password hashing without bcrypt"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_database():
    """Fix the database with simple password hashing"""
    print("Fixing ResumeRAG database...")
    
    try:
        # Drop all tables first
        Base.metadata.drop_all(bind=engine)
        print("Dropped existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Created new tables")
        
        # Create test users
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create candidate user
        candidate = User(
            email="candidate@example.com",
            hashed_password=simple_hash_password("test"),
            full_name="Test Candidate",
            role=UserRole.CANDIDATE
        )
        db.add(candidate)
        print("Created test candidate user")
        
        # Create recruiter user
        recruiter = User(
            email="recruiter@example.com",
            hashed_password=simple_hash_password("test"),
            full_name="Test Recruiter",
            role=UserRole.RECRUITER
        )
        db.add(recruiter)
        print("Created test recruiter user")
        
        db.commit()
        print("Database fix complete!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database()
