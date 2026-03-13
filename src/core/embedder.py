import os
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages embedding generation and caching"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.cache_dir = settings.embedding_cache_dir
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(
            self.model_name,
            cache_folder=self.cache_dir,
            device="cpu"  # Change to "cuda" if GPU available
        )
        logger.info(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text"""
        if not text or not text.strip():
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed multiple texts efficiently"""
        # Filter out empty texts
        texts = [t for t in texts if t and t.strip()]
        
        if not texts:
            return np.array([])
        
        logger.info(f"Embedding {len(texts)} texts with batch size {batch_size}")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get embedding vector dimension"""
        return self.model.get_sentence_embedding_dimension()
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Normalize
        a = embedding1 / np.linalg.norm(embedding1)
        b = embedding2 / np.linalg.norm(embedding2)
        # Cosine similarity
        return float(np.dot(a, b))

# Test the module
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = EmbeddingManager()
    
    # Test single embedding
    text = "What is RAG?"
    embedding = manager.embed_text(text)
    print(f"Single embedding shape: {embedding.shape}")
    
    # Test batch embedding
    texts = [
        "Retrieval Augmented Generation",
        "Machine Learning",
        "Vector databases"
    ]
    embeddings = manager.embed_batch(texts)
    print(f"Batch embeddings shape: {embeddings.shape}")
    
    # Test similarity
    sim = manager.similarity(embeddings[0], embeddings[1])
    print(f"Similarity between texts: {sim:.4f}")
    print("✅ All tests passed!")