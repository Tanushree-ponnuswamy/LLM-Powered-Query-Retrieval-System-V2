from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    documents: str  # URL to the document
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    page_number: Optional[int] = None

class ClauseMatch(BaseModel):
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    source_reference: str

class DecisionResult(BaseModel):
    decision: str
    amount: Optional[float] = None
    justification: str
    clauses_used: List[str]
    confidence_score: float