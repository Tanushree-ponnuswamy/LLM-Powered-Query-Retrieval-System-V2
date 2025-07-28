import uuid
import hashlib
from datetime import datetime
import re

def generate_chunk_id() -> str:
    """Generate unique chunk ID"""
    return str(uuid.uuid4())

def generate_hash(text: str) -> str:
    """Generate hash for text content"""
    return hashlib.md5(text.encode()).hexdigest()

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    return text.strip()

def extract_numbers(text: str) -> list[float]:
    """Extract numbers from text"""
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(num) for num in numbers]

def format_response_time(start_time: datetime) -> str:
    """Format response time"""
    elapsed = (datetime.now() - start_time).total_seconds()
    return f"{elapsed:.2f}s"