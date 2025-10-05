#!/usr/bin/env python3
"""
Database initialization script for ResumeRAG
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, Base
from models import User, Resume, Job, ResumeEmbedding, UserRole

def init_database():
    """Initialize the database with all tables"""
    print("Initializing ResumeRAG database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Create test users
        from auth import get_password_hash
        from sqlalchemy.orm import sessionmaker
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if test users already exist
            existing_candidate = db.query(User).filter(User.email == "candidate@example.com").first()
            existing_recruiter = db.query(User).filter(User.email == "recruiter@example.com").first()
            
            if not existing_candidate:
                candidate = User(
                    email="candidate@example.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="Test Candidate",
                    role=UserRole.CANDIDATE
                )
                db.add(candidate)
                print("Test candidate user created")
            
            if not existing_recruiter:
                recruiter = User(
                    email="recruiter@example.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="Test Recruiter",
                    role=UserRole.RECRUITER
                )
                db.add(recruiter)
                print("Test recruiter user created")
            
            db.commit()
            print("Database initialization complete!")
            
        except Exception as e:
            print(f"Error creating test users: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    init_database()
