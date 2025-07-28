import requests
import PyPDF2
import docx
from io import BytesIO
from typing import List, Dict, Any
import re
import logging
from email import message_from_string
from bs4 import BeautifulSoup

from models.schemas import DocumentChunk
from utils.helpers import generate_chunk_id

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def process_document(self, document_url: str) -> List[DocumentChunk]:
        """
        Download and process document from URL
        """
        try:
            logger.info(f"Downloading document from: {document_url}")
            
            # Download document
            response = requests.get(document_url, timeout=30)
            response.raise_for_status()
            
            # Determine document type from URL or content-type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type or document_url.lower().endswith('.pdf'):
                return await self._process_pdf(BytesIO(response.content))
            elif 'word' in content_type or document_url.lower().endswith(('.docx', '.doc')):
                return await self._process_docx(BytesIO(response.content))
            elif 'text' in content_type or 'email' in content_type:
                return await self._process_text(response.text)
            else:
                # Try to process as text
                return await self._process_text(response.text)
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def _process_pdf(self, file_stream: BytesIO) -> List[DocumentChunk]:
        """Process PDF document"""
        chunks = []
        
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    page_chunks = self._chunk_text(
                        text, 
                        metadata={"page_number": page_num + 1, "document_type": "pdf"}
                    )
                    chunks.extend(page_chunks)
            
            logger.info(f"Extracted {len(chunks)} chunks from PDF")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    async def _process_docx(self, file_stream: BytesIO) -> List[DocumentChunk]:
        """Process DOCX document"""
        chunks = []
        
        try:
            doc = docx.Document(file_stream)
            
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text)
            
            text = "\n".join(full_text)
            chunks = self._chunk_text(
                text,
                metadata={"document_type": "docx"}
            )
            
            logger.info(f"Extracted {len(chunks)} chunks from DOCX")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing DOCX: {str(e)}")
            raise
    
    async def _process_text(self, text: str) -> List[DocumentChunk]:
        """Process plain text or email"""
        try:
            # Try to parse as email first
            if "@" in text and ("From:" in text or "To:" in text):
                return await self._process_email(text)
            
            # Process as plain text
            chunks = self._chunk_text(
                text,
                metadata={"document_type": "text"}
            )
            
            logger.info(f"Extracted {len(chunks)} chunks from text")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            raise
    
    async def _process_email(self, email_content: str) -> List[DocumentChunk]:
        """Process email content"""
        try:
            msg = message_from_string(email_content)
            
            # Extract email metadata
            metadata = {
                "document_type": "email",
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "subject": msg.get("Subject", ""),
                "date": msg.get("Date", "")
            }
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/html":
                        soup = BeautifulSoup(part.get_payload(decode=True), 'html.parser')
                        body += soup.get_text()
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            chunks = self._chunk_text(body, metadata=metadata)
            
            logger.info(f"Extracted {len(chunks)} chunks from email")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            # Fallback to text processing
            return await self._process_text(email_content)
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Split text into chunks with overlap"""
        chunks = []
        
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= self.chunk_size:
            chunks.append(DocumentChunk(
                content=text,
                metadata=metadata,
                chunk_id=generate_chunk_id(),
                page_number=metadata.get("page_number")
            ))
            return chunks
        
        start = 0
        chunk_num = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                # Find the last sentence or paragraph break
                last_sentence = text.rfind('.', start, end)
                last_paragraph = text.rfind('\n', start, end)
                
                if last_sentence > start:
                    end = last_sentence + 1
                elif last_paragraph > start:
                    end = last_paragraph
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_number"] = chunk_num
                
                chunks.append(DocumentChunk(
                    content=chunk_content,
                    metadata=chunk_metadata,
                    chunk_id=generate_chunk_id(),
                    page_number=metadata.get("page_number")
                ))
            
            start = max(start + 1, end - self.chunk_overlap)
            chunk_num += 1
        
        return chunks