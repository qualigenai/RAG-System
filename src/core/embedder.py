from typing import List
import numpy as np
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    RAG System v2.0 — HuggingFace sentence-transformers.
    Uses lazy loading — model downloads on first use, not at startup.
    This prevents Render port timeout during deployment.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model or "all-MiniLM-L6-v2"
        self._dimension = 384
        self._model = None  # ← lazy load, not at startup
        logger.info(f"✅ EmbeddingManager v2.0 ready — model loads on first request")

    def _get_model(self):
        """Load model only when first needed — not at startup."""
        if self._model is None:
            logger.info(f"📥 Loading HuggingFace model: {self.model_name} ...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"✅ HuggingFace model loaded successfully")
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            return np.zeros(self._dimension)
        return self._get_model().encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return np.array([])
        logger.info(f"Embedding {len(texts)} texts via HuggingFace")
        return self._get_model().encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        a = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        b = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        return float(np.dot(a, b))