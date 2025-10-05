import io
import re
from typing import Dict, Any
import PyPDF2
import docx2txt
from docx import Document
import zipfile

class ResumeParser:
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
        }
    
    def parse(self, content: bytes, filename: str) -> str:
        """Parse resume content from various file formats"""
        try:
            if filename.lower().endswith('.pdf'):
                return self._parse_pdf(content)
            elif filename.lower().endswith(('.docx', '.doc')):
                return self._parse_docx(content)
            elif filename.lower().endswith('.txt'):
                return content.decode('utf-8', errors='ignore')
            else:
                # Try to decode as text
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            # Fallback to text decoding
            return content.decode('utf-8', errors='ignore')
    
    def _parse_pdf(self, content: bytes) -> str:
        """Parse PDF content"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception:
            return "Error parsing PDF"
    
    def _parse_docx(self, content: bytes) -> str:
        """Parse DOCX content"""
        try:
            # Try using python-docx first
            doc = Document(io.BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception:
            try:
                # Fallback to docx2txt
                return docx2txt.process(io.BytesIO(content))
            except Exception:
                return "Error parsing DOCX"
    
    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract structured sections from resume content"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'experience': r'(?i)(experience|work\s+history|employment|professional\s+experience)',
            'education': r'(?i)(education|academic|qualifications)',
            'skills': r'(?i)(skills|technical\s+skills|competencies)',
            'summary': r'(?i)(summary|profile|objective|about)',
            'projects': r'(?i)(projects|portfolio)',
            'certifications': r'(?i)(certifications|certificates)'
        }
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            section_found = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = section_name
                    current_content = [line]
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def extract_contact_info(self, content: str) -> Dict[str, str]:
        """Extract contact information from resume"""
        contact_info = {}
        
        # Extract email
        email_match = re.search(self.pii_patterns['email'], content)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(self.pii_patterns['phone'], content)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        return contact_info
