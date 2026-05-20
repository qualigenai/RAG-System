from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration for RAG System v2.0"""

    # ============= v1.0 Settings =============
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: str = "./embeddings_cache"
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

    # ============= v2.0 Hugging Face Settings =============
    hf_token: Optional[str] = None
    hf_api_url: str = (
        "https://router.huggingface.co/hf-inference/models/"
        "sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()


if __name__ == "__main__":
    print(f"Database URL: {settings.database_url}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Embedding Cache Dir: {settings.embedding_cache_dir}")
    print(f"HF API URL: {settings.hf_api_url}")
    print(f"HF Token Found: {settings.hf_token is not None}")
    print("✅ Settings loaded successfully!")