from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_TOKEN: str = "59d150e97f686fcc6859251c02b719e661203b21d4fb2eae792e07e727f07bff"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost/hackrx_db"
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Vector Search Configuration
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Processing Configuration
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.1
    
    class Config:
        env_file = ".env"

settings = Settings()