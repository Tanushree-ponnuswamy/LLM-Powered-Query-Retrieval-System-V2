from enum import Enum
from config.settings import Settings

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    CHUNK_SIZE: int = 1000
    ENABLE_QUERY_CACHE: bool = False

class TestingSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "postgresql://test_user:test_pass@localhost/test_hackrx_db"
    CHUNK_SIZE: int = 500
    TOP_K_RESULTS: int = 3

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 5
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.05
    ENABLE_QUERY_CACHE: bool = True

def get_settings(env: Environment = Environment.DEVELOPMENT) -> Settings:
    """Get settings based on environment"""
    if env == Environment.DEVELOPMENT:
        return DevelopmentSettings()
    elif env == Environment.TESTING:
        return TestingSettings()
    elif env == Environment.PRODUCTION:
        return ProductionSettings()
    else:
        return Settings()