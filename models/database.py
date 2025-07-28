from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from config.settings import settings

Base = declarative_base()

class DocumentProcessingLog(Base):
    __tablename__ = "document_processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_url = Column(String, nullable=False)
    processing_status = Column(String, nullable=False)  # success, error, processing
    chunks_count = Column(Integer)
    processing_time = Column(Float)  # in seconds
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    document_metadata = Column(JSON)  # ✅ renamed to avoid conflict

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_url = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    processing_time = Column(Float)
    similarity_scores = Column(JSON)  # Store top similarity scores
    created_at = Column(DateTime, default=datetime.utcnow)
    document_metadata = Column(JSON)  # ✅ renamed to avoid conflict

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_usage = Column(Float)
    active_queries = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()