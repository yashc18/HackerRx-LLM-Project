from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings for HackRx system"""
    
    # Gemini API settings
    gemini_api_key: str = ""
    primary_model: str = "gemini-1.5-flash"
    use_gemini_api: bool = True
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 3072
    
    # Vector search settings (simplified)
    chunk_size: int = 1000
    max_chunks_per_document: int = 50
    
    # Processing settings
    max_document_size_mb: int = 100
    max_processing_time_seconds: int = 120
    max_concurrent_requests: int = 10
    
    # Quality thresholds
    min_text_length: int = 50
    
    # Cache settings
    cache_ttl_seconds: int = 3600
    max_cache_size_mb: int = 2048
    
    # Security settings
    rate_limit_per_minute: int = 100
    max_request_size_mb: int = 50
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file 