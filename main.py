from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from contextlib import asynccontextmanager

from models.schemas import QueryRequest, QueryResponse
from services.query_processor import QueryProcessor
from config.settings import settings
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up the application...")
    # Initialize services here if needed
    yield
    # Shutdown
    logger.info("Shutting down the application...")

app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="Process natural language queries and retrieve relevant information from documents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize query processor
query_processor = QueryProcessor()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the bearer token"""
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

@app.get("/")
async def root():
    return {"message": "LLM-Powered Intelligent Query-Retrieval System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_queries(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """
    Process natural language queries against documents
    """
    try:
        logger.info(f"Processing {len(request.questions)} queries for document: {request.documents}")
        
        # Process the queries
        answers = await query_processor.process_queries(
            document_url=request.documents,
            questions=request.questions
        )
        
        logger.info(f"Successfully processed {len(answers)} queries")
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        logger.error(f"Error processing queries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing queries: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )