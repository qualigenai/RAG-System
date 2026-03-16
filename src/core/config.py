from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration for RAG System v1.0 + v1.5"""

    # ============= v1.0 Settings =============
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: str = "./embeddings_cache"  # ← ADDED!
    chunk_size: int = 500
    llm_provider: str = "local"
    llm_model: str = "mistral"
    qdrant_url: str = "http://localhost:6333"
    debug: bool = True

    # ============= v1.5 Settings =============
    database_url: str = "sqlite:///./rag_system.db"
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_url: str = "http://localhost:8000"
    streamlit_url: str = "http://localhost:8501"
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
settings = Settings()


# Verify settings
if __name__ == "__main__":
    print(f"Database URL: {settings.database_url}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Embedding Cache Dir: {settings.embedding_cache_dir}")
    print(f"LLM Provider: {settings.llm_provider}")
    print("✅ Settings loaded successfully!")