from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///rag.db"
    
    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: str = "models"
    
    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # LLM
    llm_provider: str = "local"  # local, openai, anthropic
    llm_model: str = "mistral"
    temperature: float = 0.7
    max_tokens: int = 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Verify settings
if __name__ == "__main__":
    print(f"Database URL: {settings.database_url}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"LLM Provider: {settings.llm_provider}")
    print("✅ Settings loaded successfully!")