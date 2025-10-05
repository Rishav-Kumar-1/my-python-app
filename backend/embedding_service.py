import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ResumeEmbedding
import re

class EmbeddingService:
    def __init__(self):
        # Load a lightweight sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    def generate_embeddings_async(self, resume_id: str, content: str):
        """Generate embeddings for resume content asynchronously"""
        asyncio.create_task(self._generate_embeddings_task(resume_id, content))
    
    async def _generate_embeddings_task(self, resume_id: str, content: str):
        """Background task to generate embeddings"""
        try:
            # Split content into chunks
            chunks = self._split_into_chunks(content)
            
            # Generate embeddings for each chunk
            embeddings = self.model.encode(chunks)
            
            # Store in database
            db = SessionLocal()
            try:
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    embedding_record = ResumeEmbedding(
                        resume_id=resume_id,
                        chunk_text=chunk,
                        embedding=json.dumps(embedding.tolist()),
                        chunk_index=i
                    )
                    db.add(embedding_record)
                
                db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"Error generating embeddings for resume {resume_id}: {e}")
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at sentence boundary
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + self.chunk_size // 2:
                end = sentence_end + 1
            
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        
        return chunks
    
    def search(self, query: str, resume_ids: List[str], k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant content in resumes"""
        db = SessionLocal()
        try:
            # Get all embeddings for the specified resumes
            embeddings = db.query(ResumeEmbedding).filter(
                ResumeEmbedding.resume_id.in_(resume_ids)
            ).all()
            
            if not embeddings:
                return []
            
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Calculate similarities
            results = []
            for embedding in embeddings:
                stored_embedding = np.array(json.loads(embedding.embedding))
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                results.append({
                    'resume_id': str(embedding.resume_id),
                    'chunk_text': embedding.chunk_text,
                    'score': float(similarity),
                    'snippet': self._extract_snippet(embedding.chunk_text, query)
                })
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
            
        finally:
            db.close()
    
    def match_job_to_resumes(self, job_description: str, resume_ids: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
        """Match job description to resumes"""
        db = SessionLocal()
        try:
            # Get all embeddings for the specified resumes
            embeddings = db.query(ResumeEmbedding).filter(
                ResumeEmbedding.resume_id.in_(resume_ids)
            ).all()
            
            if not embeddings:
                return []
            
            # Generate job embedding
            job_embedding = self.model.encode([job_description])[0]
            
            # Calculate similarities
            results = []
            for embedding in embeddings:
                stored_embedding = np.array(json.loads(embedding.embedding))
                similarity = np.dot(job_embedding, stored_embedding) / (
                    np.linalg.norm(job_embedding) * np.linalg.norm(stored_embedding)
                )
                
                results.append({
                    'resume_id': str(embedding.resume_id),
                    'chunk_text': embedding.chunk_text,
                    'score': float(similarity)
                })
            
            # Group by resume and calculate average score
            resume_scores = {}
            for result in results:
                resume_id = result['resume_id']
                if resume_id not in resume_scores:
                    resume_scores[resume_id] = []
                resume_scores[resume_id].append(result['score'])
            
            # Calculate final scores and evidence
            final_results = []
            for resume_id, scores in resume_scores.items():
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                
                # Get evidence snippets
                evidence = [
                    r['chunk_text'] for r in results 
                    if r['resume_id'] == resume_id and r['score'] > avg_score * 0.8
                ][:3]  # Top 3 evidence snippets
                
                # Extract missing requirements (simplified)
                missing_requirements = self._extract_missing_requirements(
                    job_description, evidence
                )
                
                final_results.append({
                    'resume_id': resume_id,
                    'score': avg_score,
                    'evidence': evidence,
                    'missing_requirements': missing_requirements
                })
            
            # Sort by score and return top n
            final_results.sort(key=lambda x: x['score'], reverse=True)
            return final_results[:top_n]
            
        finally:
            db.close()
    
    def _extract_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Extract a relevant snippet around the query"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find query position
        pos = text_lower.find(query_lower)
        if pos == -1:
            # If exact match not found, return beginning of text
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Extract snippet around the match
        start = max(0, pos - max_length // 2)
        end = min(len(text), pos + len(query) + max_length // 2)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def _extract_missing_requirements(self, job_description: str, evidence: List[str]) -> List[str]:
        """Extract missing requirements by comparing job description with evidence"""
        # This is a simplified implementation
        # In a real system, you'd use more sophisticated NLP techniques
        
        job_keywords = set(re.findall(r'\b\w+\b', job_description.lower()))
        evidence_text = ' '.join(evidence).lower()
        evidence_keywords = set(re.findall(r'\b\w+\b', evidence_text))
        
        # Find keywords in job description that are not in evidence
        missing = job_keywords - evidence_keywords
        
        # Filter out common words and return top missing requirements
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        missing = missing - common_words
        
        return list(missing)[:5]  # Return top 5 missing requirements
