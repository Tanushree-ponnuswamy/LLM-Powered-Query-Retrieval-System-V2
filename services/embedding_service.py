import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import pickle
import os
import logging

from models.schemas import DocumentChunk, ClauseMatch
from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.index = None
        self.chunks = []
        self.dimension = 384  # MiniLM-L6-v2 dimension
    
    async def create_embeddings(self, chunks: List[DocumentChunk]) -> None:
        """Create embeddings for document chunks"""
        try:
            logger.info(f"Creating embeddings for {len(chunks)} chunks")
            
            # Extract text content
            texts = [chunk.content for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to index
            self.index.add(embeddings.astype('float32'))
            
            # Store chunks for retrieval
            self.chunks = chunks
            
            logger.info(f"Successfully created embeddings and FAISS index")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    async def search_similar_chunks(self, query: str, top_k: int = None) -> List[ClauseMatch]:
        """Search for similar chunks using semantic similarity"""
        if self.index is None:
            raise ValueError("No embeddings index available. Create embeddings first.")
        
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            logger.info(f"Searching for similar chunks: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Convert to ClauseMatch objects
            matches = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    matches.append(ClauseMatch(
                        content=chunk.content,
                        similarity_score=float(score),
                        metadata=chunk.metadata,
                        source_reference=f"Chunk {chunk.chunk_id}"
                    ))
            
            logger.info(f"Found {len(matches)} similar chunks")
            return matches
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            raise
    
    def save_index(self, path: str) -> None:
        """Save FAISS index and chunks to disk"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{path}.faiss")
            
            # Save chunks
            with open(f"{path}.chunks", 'wb') as f:
                pickle.dump(self.chunks, f)
            
            logger.info(f"Saved index to {path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, path: str) -> bool:
        """Load FAISS index and chunks from disk"""
        try:
            if os.path.exists(f"{path}.faiss") and os.path.exists(f"{path}.chunks"):
                # Load FAISS index
                self.index = faiss.read_index(f"{path}.faiss")
                
                # Load chunks
                with open(f"{path}.chunks", 'rb') as f:
                    self.chunks = pickle.load(f)
                
                logger.info(f"Loaded index from {path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False