#services/llm_service.py
import ollama
import json
import logging
from typing import List, Dict, Any, Optional
import re

from config.settings import settings
from models.schemas import ClauseMatch, DecisionResult

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.LLM_MODEL
    
    async def generate_answer(self, question: str, context_chunks: List[ClauseMatch]) -> str:
        """Generate answer using LLM based on question and context"""
        try:
            logger.info(f"Generating answer for question: {question[:100]}...")
            
            # Prepare context
            context = self._prepare_context(context_chunks)
            
            # Create prompt
            prompt = self._create_answer_prompt(question, context)
            
            # Generate response
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': settings.TEMPERATURE,
                    'num_predict': settings.MAX_TOKENS,
                    'top_p': 0.9,
                    'top_k': 40
                }
            )
            
            answer = response['response'].strip()
            
            # Clean the response to remove chunk references
            cleaned_answer = self._clean_chunk_references(answer)
            
            logger.info(f"Generated answer: {cleaned_answer[:200]}...")
            return cleaned_answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    async def extract_structured_decision(self, question: str, context_chunks: List[ClauseMatch]) -> DecisionResult:
        """Extract structured decision with JSON output"""
        try:
            logger.info(f"Extracting structured decision for: {question[:100]}...")
            
            context = self._prepare_context(context_chunks)
            prompt = self._create_decision_prompt(question, context)
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Lower temperature for structured output
                    'num_predict': settings.MAX_TOKENS
                }
            )
            
            # Try to parse JSON response
            try:
                result_text = response['response'].strip()
                
                # Extract JSON from response if it contains other text
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group()
                
                result_data = json.loads(result_text)
                
                return DecisionResult(
                    decision=result_data.get('decision', 'unknown'),
                    amount=result_data.get('amount'),
                    justification=result_data.get('justification', ''),
                    clauses_used=result_data.get('clauses_used', []),
                    confidence_score=result_data.get('confidence_score', 0.0)
                )
                
            except json.JSONDecodeError:
                # Fallback to text response
                return DecisionResult(
                    decision='processed',
                    justification=response['response'].strip(),
                    clauses_used=[f"Chunk {i}" for i in range(len(context_chunks))],
                    confidence_score=0.8
                )
            
        except Exception as e:
            logger.error(f"Error extracting structured decision: {str(e)}")
            raise
    
    def _prepare_context(self, chunks: List[ClauseMatch]) -> str:
        """Prepare context from retrieved chunks without chunk numbers"""
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            # Add chunk without chunk numbers or references
            chunk_text = f"Document Section:\n"
            chunk_text += f"{chunk.content}\n"
            
            # Only add page number if available, without chunk reference
            if chunk.metadata.get('page_number'):
                chunk_text += f"(Page {chunk.metadata['page_number']})\n"
            
            context_parts.append(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    def _create_answer_prompt(self, question: str, context: str) -> str:
        """Create prompt for answer generation"""
        return f"""You are an expert document analyst. Based on the provided document context, answer the following question accurately and concisely.

Question: {question}

Document Context:
{context}

Instructions:
1. Answer based ONLY on the information provided in the context
2. Provide a direct, factual answer in 1-3 sentences maximum
3. Do NOT use bullet points, lists, or extensive explanations
4. Do NOT mention "Based on the provided document context" or similar phrases
5. Do NOT mention chunk numbers, sections, or any document structure references
6. Start your answer directly with the factual information
7. Be concise and professional
8. If multiple conditions exist, summarize them in flowing sentences, not lists
9. Focus on the key facts that directly answer the question

Answer:"""
    
    def _create_decision_prompt(self, question: str, context: str) -> str:
        """Create prompt for structured decision extraction"""
        return f"""You are an expert policy analyzer. Based on the provided document context, analyze the question and provide a structured decision.

Question: {question}

Document Context:
{context}

Instructions:
1. Analyze the question and context to make a decision
2. Provide a structured JSON response with the following format:
{{
    "decision": "approved/rejected/pending/not_applicable",
    "amount": null_or_numeric_value,
    "justification": "detailed_explanation_with_specific_references",
    "clauses_used": ["list", "of", "relevant", "clause", "references"],
    "confidence_score": 0.0_to_1.0
}}

3. Base your decision ONLY on the provided context
4. Reference specific clauses or sections in your justification
5. Be precise and professional
6. Do not include any chunk numbers or identifiers in the JSON response
7. Do not mention or reference chunk numbers or metadata directly
8. Focus only on the actual policy content and rules

JSON Response:"""
    
    def _clean_chunk_references(self, text: str) -> str:
        """Remove chunk references and verbose phrases from the generated text"""
        # Remove common verbose beginnings
        verbose_patterns = [
            r'^[Bb]ased on the provided document context,?\s*',
            r'^[Aa]ccording to the document,?\s*',
            r'^[Aa]ccording to the policy,?\s*',
            r'^[Aa]ccording to the provided document context,?\s*',
            r'^[Tt]he document states that\s*',
            r'^[Ff]rom the provided context,?\s*',
            r'^[Ii]n the document,?\s*',
            r'^[Aa]s per the policy,?\s*',
            r'^[Tt]he policy states that\s*',
        ]
        
        # Patterns to remove chunk references
        chunk_patterns = [
            r'\s*[Tt]his is stated in [Cc]hunk \d+.*?\.?',
            r'\s*[Aa]s mentioned in [Cc]hunk \d+.*?\.?',
            r'\s*and reiterated in [Cc]hunk \d+.*?\.?',
            r'\s*\([Cc]hunk \d+.*?\)',
            r'\s*[Aa]ccording to [Cc]hunk \d+.*?\.?',
            r'\s*[Cc]hunk \d+ (?:states|mentions|indicates).*?\.?',
            r'\s*[Bb]ased on [Cc]hunk \d+.*?\.?',
            r'\s*[Ii]n [Cc]hunk \d+.*?\.?',
            r'\s*[Ff]rom [Cc]hunk \d+.*?\.?',
            r'\s*[Cc]hunk \d+[:\-\s]',
        ]
        
        cleaned = text
        
        # Remove verbose beginnings
        for pattern in verbose_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove chunk references
        for pattern in chunk_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Convert bullet points to flowing text
        cleaned = self._convert_bullets_to_text(cleaned)
        
        # Remove technical section references
        cleaned = re.sub(r'\s*as per Section [a-zA-Z0-9\.]+\.?', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*under Section [a-zA-Z0-9\.]+\.?', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up multiple spaces and periods
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'\.+', '.', cleaned)
        
        # Remove any trailing/leading punctuation issues
        cleaned = cleaned.strip(' .,')
        
        # Ensure proper capitalization
        if cleaned and not cleaned[0].isupper():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        # Ensure it ends with a period if it doesn't already
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += '.'
        
        return cleaned
    
    def _convert_bullets_to_text(self, text: str) -> str:
        """Convert bullet points to flowing text"""
        # Remove bullet point markers
        text = re.sub(r'\n?\s*[\*\-\•]\s*', ' ', text)
        text = re.sub(r'\n?\s*\d+\.\s*', ' ', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text