import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict

from services.query_processor import QueryProcessor
class BatchProcessor:
    def __init__(self):
        self.query_processor = QueryProcessor()
    
    async def process_batch_file(self, batch_file: str) -> Dict:
        """Process a batch of queries from JSON file"""
        with open(batch_file, 'r') as f:
            batch_data = json.load(f)
        
        results = {
            'processed_at': time.time(),
            'total_documents': len(batch_data.get('documents', [])),
            'results': []
        }
        
        for doc_data in batch_data.get('documents', []):
            doc_url = doc_data['url']
            questions = doc_data['questions']
            
            start_time = time.time()
            try:
                answers = await self.query_processor.process_queries(doc_url, questions)
                
                doc_result = {
                    'document_url': doc_url,
                    'processing_time': time.time() - start_time,
                    'status': 'success',
                    'questions_count': len(questions),
                    'answers': answers
                }
                
            except Exception as e:
                doc_result = {
                    'document_url': doc_url,
                    'processing_time': time.time() - start_time,
                    'status': 'error',
                    'error': str(e)
                }
            
            results['results'].append(doc_result)
        
        return results
    
    async def process_directory(self, directory: str, output_file: str = None):
        """Process all JSON files in a directory"""
        directory_path = Path(directory)
        batch_files = list(directory_path.glob('*.json'))
        
        all_results = []
        
        for batch_file in batch_files:
            print(f"Processing {batch_file}...")
            result = await self.process_batch_file(str(batch_file))
            all_results.append(result)
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(all_results, f, indent=2)
        
        return all_results

# Example batch file format (sample_batch.json)
sample_batch = {
    "documents": [
        {
            "url": "https://example.com/policy1.pdf",
            "questions": [
                "What is the coverage amount?",
                "What are the exclusions?",
                "What is the claim process?"
            ]
        },
        {
            "url": "https://example.com/policy2.pdf",
            "questions": [
                "What is the premium amount?",
                "What is the policy term?",
                "Are pre-existing conditions covered?"
            ]
        }
    ]
}

async def main():
    processor = BatchProcessor()
    
    # Create sample batch file
    with open('sample_batch.json', 'w') as f:
        json.dump(sample_batch, f, indent=2)
    
    # Process batch
    results = await processor.process_batch_file('sample_batch.json')
    
    # Save results
    with open('batch_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Batch processing completed!")

if __name__ == "__main__":
    asyncio.run(main())
