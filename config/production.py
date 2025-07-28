from config.settings import Settings

class ProductionSettings(Settings):
    # Production-specific overrides
    DATABASE_URL: str = "postgresql://postgres:postgre#2025@prod_host:5432/hackrx_prod"
    
    # Optimized settings for production
    CHUNK_SIZE: int = 800  # Smaller chunks for better precision
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 3  # Fewer results for faster processing
    MAX_TOKENS: int = 2000  # Reduced for cost efficiency
    TEMPERATURE: float = 0.05  # More deterministic
    
    # Caching and performance
    ENABLE_QUERY_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CONCURRENT_QUERIES: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_PERFORMANCE_LOGGING: bool = True

production_settings = ProductionSettings()