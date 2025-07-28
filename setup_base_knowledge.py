import os
import asyncio
import requests
from pathlib import Path
import logging

from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseKnowledgeSetup:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
    
    async def download_pdf_from_url(self, url: str, filename: str) -> str:
        """Download PDF from URL and save locally"""
        try:
            logger.info(f"Downloading PDF from: {url}")
            
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Create data directory if it doesn't exist
            os.makedirs("./data/base_pdfs", exist_ok=True)
            
            # Save file
            file_path = f"./data/base_pdfs/{filename}"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Saved PDF to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            raise
    
    async def setup_base_knowledge_from_urls(self, pdf_urls: list):
        """
        Setup base knowledge from PDF URLs
        
        Args:
            pdf_urls: List of PDF URLs to download and process
        """
        try:
            logger.info(f"Setting up base knowledge from {len(pdf_urls)} PDF URLs")
            
            # Download PDFs
            local_paths = []
            for i, url in enumerate(pdf_urls):
                filename = f"base_policy_{i+1}.pdf"
                local_path = await self.download_pdf_from_url(url, filename)
                local_paths.append(local_path)
            
            # Update settings to use local paths
            settings.BASE_KNOWLEDGE_PDFS = local_paths
            
            # Initialize base knowledge
            await self.embedding_service.initialize_base_knowledge()
            
            logger.info("Base knowledge setup completed successfully!")
            
        except Exception as e:
            logger.error(f"Error setting up base knowledge: {str(e)}")
            raise
    
    async def setup_base_knowledge_from_files(self, pdf_files: list):
        """
        Setup base knowledge from local PDF files
        
        Args:
            pdf_files: List of local PDF file paths
        """
        try:
            logger.info(f"Setting up base knowledge from {len(pdf_files)} local PDF files")
            
            # Verify files exist
            existing_files = []
            for file_path in pdf_files:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
                    logger.info(f"Found: {file_path}")
                else:
                    logger.warning(f"File not found: {file_path}")
            
            if not existing_files:
                raise ValueError("No valid PDF files found")
            
            # Update settings
            settings.BASE_KNOWLEDGE_PDFS = existing_files
            
            # Initialize base knowledge
            await self.embedding_service.initialize_base_knowledge()
            
            logger.info("Base knowledge setup completed successfully!")
            
        except Exception as e:
            logger.error(f"Error setting up base knowledge: {str(e)}")
            raise
    
    def get_sample_pdf_urls(self):
        """Get sample PDF URLs (replace with your actual URLs)"""
        return [
            # Replace these with your actual 5 PDF URLs from HackRX
            "https://hackrx.blob.core.windows.net/assets/policy1.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "https://hackrx.blob.core.windows.net/assets/policy2.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "https://hackrx.blob.core.windows.net/assets/policy3.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "https://hackrx.blob.core.windows.net/assets/policy4.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "https://hackrx.blob.core.windows.net/assets/policy5.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
        ]

async def main():
    """Main setup function"""
    setup = BaseKnowledgeSetup()
    
    print("Base Knowledge Setup")
    print("1. Setup from URLs (download PDFs)")
    print("2. Setup from local files")
    print("3. Use sample URLs")
    
    choice = input("Choose an option (1-3): ").strip()
    
    try:
        if choice == "1":
            print("Enter PDF URLs (one per line, press Enter twice to finish):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                await setup.setup_base_knowledge_from_urls(urls)
            else:
                print("No URLs provided")
        
        elif choice == "2":
            print("Enter PDF file paths (one per line, press Enter twice to finish):")
            files = []
            while True:
                file_path = input().strip()
                if not file_path:
                    break
                files.append(file_path)
            
            if files:
                await setup.setup_base_knowledge_from_files(files)
            else:
                print("No files provided")
        
        elif choice == "3":
            sample_urls = setup.get_sample_pdf_urls()
            await setup.setup_base_knowledge_from_urls(sample_urls)
        
        else:
            print("Invalid choice")
    
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())