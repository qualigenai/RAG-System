import os
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    RAG System v2.0 — HuggingFace sentence-transformers embeddings.
    Replaces OpenAI text-embedding-3-small (v1.5) with free local model.
    Model  : all-MiniLM-L6-v2
    Dim    : 384
    Cost   : Free — no API key needed
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model or "all-MiniLM-L6-v2"
        self._dimension = 384
        logger.info(f"Loading HuggingFace model: {self.model_name} ...")
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"✅ EmbeddingManager v2.0 initialized with HuggingFace {self.model_name}")

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        if not text or not text.strip():
            return np.zeros(self._dimension)
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed a list of texts in batches."""
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return np.array([])
        logger.info(f"Embedding {len(texts)} texts via HuggingFace sentence-transformers")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Cosine similarity between two embeddings."""
        a = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        b = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        return float(np.dot(a, b))