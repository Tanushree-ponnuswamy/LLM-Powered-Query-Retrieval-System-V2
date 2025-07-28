import asyncio
import time
from typing import List, Dict, Any
from collections import defaultdict
import logging

from services.embedding_service import EmbeddingService
from models.schemas import DocumentChunk, ClauseMatch

logger = logging.getLogger(__name__)

class QueryOptimizer:
    def __init__(self):
        self.query_cache = {}
        self.performance_stats = defaultdict(list)
    
    def should_use_cache(self, query: str, document_url: str) -> bool:
        """Determine if cached result should be used"""
        cache_key = f"{document_url}:{hash(query)}"
        
        if cache_key in self.query_cache:
            cached_time = self.query_cache[cache_key]['timestamp']
            # Use cache if less than 1 hour old
            return time.time() - cached_time < 3600
        
        return False
    
    def get_cached_result(self, query: str, document_url: str) -> str:
        """Get cached result"""
        cache_key = f"{document_url}:{hash(query)}"
        return self.query_cache[cache_key]['result']
    
    def cache_result(self, query: str, document_url: str, result: str):
        """Cache query result"""
        cache_key = f"{document_url}:{hash(query)}"
        self.query_cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def optimize_chunk_selection(self, chunks: List[ClauseMatch], query: str) -> List[ClauseMatch]:
        """Optimize chunk selection based on relevance and diversity"""
        if len(chunks) <= 3:
            return chunks
        
        # Sort by similarity score
        sorted_chunks = sorted(chunks, key=lambda x: x.similarity_score, reverse=True)
        
        # Select top chunks with diversity
        selected_chunks = [sorted_chunks[0]]  # Always include the best match
        
        for chunk in sorted_chunks[1:]:
            # Check diversity - avoid very similar chunks
            is_diverse = True
            for selected in selected_chunks:
                if self._calculate_text_similarity(chunk.content, selected.content) > 0.8:
                    is_diverse = False
                    break
            
            if is_diverse:
                selected_chunks.append(chunk)
            
            if len(selected_chunks) >= 5:  # Limit to top 5 diverse chunks
                break
        
        return selected_chunks
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def log_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """Log performance metrics"""
        self.performance_stats[operation].append({
            'duration': duration,
            'timestamp': time.time(),
            'metadata': metadata or {}
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        report = {}
        
        for operation, stats in self.performance_stats.items():
            if stats:
                durations = [s['duration'] for s in stats]
                report[operation] = {
                    'count': len(stats),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'total_duration': sum(durations)
                }
        
        return report