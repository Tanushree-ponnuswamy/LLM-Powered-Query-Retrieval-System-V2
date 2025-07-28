import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import spacy
from transformers import pipeline

@dataclass
class ExtractedEntity:
    text: str
    label: str
    start: int
    end: int
    confidence: float

class AdvancedDocumentProcessor:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize NER pipeline
        try:
            self.ner_pipeline = pipeline("ner", 
                                       model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                       aggregation_strategy="simple")
        except:
            self.ner_pipeline = None
    
    def extract_structured_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from text"""
        extracted_info = {
            "entities": self.extract_entities(text),
            "dates": self.extract_dates(text),
            "amounts": self.extract_amounts(text),
            "policy_numbers": self.extract_policy_numbers(text),
            "clauses": self.extract_clauses(text)
        }
        
        return extracted_info
    
    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract named entities from text"""
        entities = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append(ExtractedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=1.0  # spaCy doesn't provide confidence scores
                ))
        
        if self.ner_pipeline:
            try:
                ner_results = self.ner_pipeline(text)
                for result in ner_results:
                    entities.append(ExtractedEntity(
                        text=result['word'],
                        label=result['entity_group'],
                        start=result['start'],
                        end=result['end'],
                        confidence=result['score']
                    ))
            except:
                pass
        
        return entities
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract date patterns from text"""
        date_patterns = [
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # DD/MM/YYYY or DD-MM-YYYY
            r'\b\d{2,4}[-/]\d{1,2}[-/]\d{1,2}\b',  # YYYY/MM/DD or YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{2,4}\b',  # Month DD, YYYY
            r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{2,4}\b'  # DD Month YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates
    
    def extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extract monetary amounts from text"""
        amount_patterns = [
            r'(?:Rs\.?|INR|₹)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Indian Rupees
            r'(?:USD?|\$)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',      # US Dollars
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:Rs\.?|INR|₹)',  # Amount before currency
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD?|\$)'       # Amount before USD
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amounts.append({
                    'amount': match.group(1) if match.groups() else match.group(0),
                    'context': text[max(0, match.start()-50):match.end()+50],
                    'position': match.start()
                })
        
        return amounts
    
    def extract_policy_numbers(self, text: str) -> List[str]:
        """Extract policy numbers from text"""
        policy_patterns = [
            r'Policy\s+No\.?\s*:?\s*([A-Z0-9\-/]+)',
            r'Policy\s+Number\s*:?\s*([A-Z0-9\-/]+)',
            r'Certificate\s+No\.?\s*:?\s*([A-Z0-9\-/]+)',
            r'\b[A-Z]{2,4}\d{6,12}\b'  # General pattern for policy numbers
        ]
        
        policy_numbers = []
        for pattern in policy_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            policy_numbers.extend(matches)
        
        return list(set(policy_numbers))
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Extract clause references from text"""
        clause_patterns = [
            r'(?:Clause|Section|Article)\s+(\d+(?:\.\d+)*)',
            r'(?:Para|Paragraph)\s+(\d+(?:\.\d+)*)',
            r'\b(\d+\.\d+(?:\.\d+)*)\s+[A-Z][a-z]+',  # Numbered clauses
            r'(?:^|\n)\s*(\d+\.)\s+[A-Z]'              # Numbered list items
        ]
        
        clauses = []
        for pattern in clause_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                clauses.append({
                    'clause_id': match.group(1),
                    'context': text[max(0, match.start()-100):match.end()+200],
                    'position': match.start()
                })
        
        return clauses