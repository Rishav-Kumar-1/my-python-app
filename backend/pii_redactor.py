import re
from typing import Dict, Any, List

class PIIRedactor:
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'date_of_birth': r'\b(?:0[1-9]|1[0-2])[-\/](?:0[1-9]|[12][0-9]|3[01])[-\/](?:19|20)\d{2}\b'
        }
        
        self.replacement_map = {
            'email': '[EMAIL REDACTED]',
            'phone': '[PHONE REDACTED]',
            'ssn': '[SSN REDACTED]',
            'address': '[ADDRESS REDACTED]',
            'credit_card': '[CARD REDACTED]',
            'date_of_birth': '[DOB REDACTED]'
        }
    
    def redact(self, text: str) -> str:
        """Redact PII from text"""
        redacted_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            redacted_text = re.sub(
                pattern, 
                self.replacement_map[pii_type], 
                redacted_text, 
                flags=re.IGNORECASE
            )
        
        return redacted_text
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text without redacting"""
        detected_pii = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                detected_pii[pii_type] = matches
        
        return detected_pii
    
    def is_pii_present(self, text: str) -> bool:
        """Check if any PII is present in text"""
        for pattern in self.pii_patterns.values():
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        return False
