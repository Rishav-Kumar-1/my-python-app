#!/usr/bin/env python3
"""
Ultra-simple FastAPI app for Render deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="ResumeRAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "ResumeRAG API is running!", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/register")
async def register():
    return {"message": "Registration endpoint working"}

@app.post("/api/login")
async def login():
    return {"message": "Login endpoint working"}

@app.post("/api/upload")
async def upload():
    return {"message": "Upload endpoint working"}

@app.get("/api/resumes")
async def resumes():
    return {"message": "Resumes endpoint working"}

@app.get("/api/jobs")
async def jobs():
    return {"message": "Jobs endpoint working"}

@app.get("/api/candidates")
async def candidates():
    return {"message": "Candidates endpoint working"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
