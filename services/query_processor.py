import logging
from typing import List
import asyncio

from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from config.settings import settings

logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        self.document_processor = DocumentProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        self._current_document_url = None
    
    async def process_queries(self, document_url: str, questions: List[str]) -> List[str]:
        """Process multiple queries against a document"""
        try:
            logger.info(f"Processing {len(questions)} queries for document: {document_url}")
            
            # Process document if it's different from the current one
            if self._current_document_url != document_url:
                await self._process_document(document_url)
                self._current_document_url = document_url
            
            # Process all questions
            answers = []
            for i, question in enumerate(questions):
                logger.info(f"Processing question {i+1}/{len(questions)}: {question[:100]}...")
                
                try:
                    answer = await self._process_single_query(question)
                    answers.append(answer)
                except Exception as e:
                    logger.error(f"Error processing question {i+1}: {str(e)}")
                    answers.append(f"Error processing question: {str(e)}")
            
            logger.info(f"Successfully processed all {len(questions)} queries")
            return answers
            
        except Exception as e:
            logger.error(f"Error in query processing: {str(e)}")
            raise
    
    async def _process_document(self, document_url: str) -> None:
        """Process and index a document"""
        try:
            logger.info(f"Processing document: {document_url}")
            
            # Extract and chunk document
            chunks = await self.document_processor.process_document(document_url)
            
            if not chunks:
                raise ValueError("No content extracted from document")
            
            # Create embeddings and index
            await self.embedding_service.create_embeddings(chunks)
            
            logger.info(f"Successfully processed document with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def _process_single_query(self, question: str) -> str:
        """Process a single query"""
        try:
            # Search for relevant chunks
            relevant_chunks = await self.embedding_service.search_similar_chunks(
                query=question,
                top_k=settings.TOP_K_RESULTS
            )
            
            if not relevant_chunks:
                return "No relevant information found in the document for this question."
            
            # Generate answer using LLM
            answer = await self.llm_service.generate_answer(question, relevant_chunks)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise