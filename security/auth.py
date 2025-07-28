import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from passlib.context import CryptContext

class SecurityManager:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = "HS256"
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def rate_limit_check(self, user_id: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """Simple rate limiting (implement with Redis in production)"""
        # This is a simplified implementation
        # In production, use Redis or similar for distributed rate limiting
        return True

# Middleware for request validation
class RequestValidator:
    @staticmethod
    def validate_document_url(url: str) -> bool:
        """Validate document URL"""
        allowed_domains = [
            'hackrx.blob.core.windows.net',
            'example.com',
            'localhost'
        ]
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        return parsed.hostname in allowed_domains
    
    @staticmethod
    def validate_questions(questions: list) -> bool:
        """Validate questions list"""
        if not isinstance(questions, list):
            return False
        
        if len(questions) == 0 or len(questions) > 20:
            return False
        
        for question in questions:
            if not isinstance(question, str) or len(question.strip()) == 0:
                return False
            
            if len(question) > 1000:  # Max question length
                return False
        
        return True