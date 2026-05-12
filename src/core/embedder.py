import os
from typing import List
import numpy as np
from openai import OpenAI
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding generation using OpenAI API"""

    def __init__(self, model_name: str = None):
        self.model_name = "text-embedding-3-small"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._dimension = 1536
        logger.info(f"✅ EmbeddingManager initialized with OpenAI {self.model_name}")

    def embed_text(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            return np.zeros(self._dimension)
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return np.array(response.data[0].embedding)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return np.array([])
        logger.info(f"Embedding {len(texts)} texts via OpenAI API")
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return np.array([item.embedding for item in response.data])

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        a = embedding1 / np.linalg.norm(embedding1)
        b = embedding2 / np.linalg.norm(embedding2)
        return float(np.dot(a, b))