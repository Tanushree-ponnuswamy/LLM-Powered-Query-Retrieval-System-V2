import traceback
import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import uuid

logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler"""
        error_id = str(uuid.uuid4())
        
        # Log the error with full traceback
        logger.error(f"Error ID: {error_id}")
        logger.error(f"Request: {request.method} {request.url}")
        logger.error(f"Exception: {type(exc).__name__}: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Determine error type and response
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "error_id": error_id,
                    "status": "error"
                }
            )
        
        # Generic server error
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_id": error_id,
                "status": "error",
                "message": "An unexpected error occurred. Please contact support with the error ID."
            }
        )
    
    @staticmethod
    def handle_document_processing_error(error: Exception, document_url: str) -> Dict[str, Any]:
        """Handle document processing errors"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "document_url": document_url,
            "suggested_action": "Please check if the document URL is accessible and the format is supported."
        }
        
        if "timeout" in str(error).lower():
            error_info["suggested_action"] = "Document processing timed out. Try with a smaller document or contact support."
        elif "permission" in str(error).lower() or "403" in str(error):
            error_info["suggested_action"] = "Access denied. Please check if the document URL is publicly accessible."
        elif "not found" in str(error).lower() or "404" in str(error):
            error_info["suggested_action"] = "Document not found. Please verify the URL is correct."
        
        return error_info

# Custom exceptions
class DocumentProcessingError(Exception):
    """Custom exception for document processing errors"""
    pass

class EmbeddingError(Exception):
    """Custom exception for embedding-related errors"""
    pass

class LLMServiceError(Exception):
    """Custom exception for LLM service errors"""
    pass