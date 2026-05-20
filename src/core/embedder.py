import logging
from typing import List

import numpy as np
import requests

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    RAG System v2.0 — HuggingFace Inference API.
    No local model download — pure API calls.
    Dimension: 384 for all-MiniLM-L6-v2
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self._dimension = 384

        self.api_url = settings.hf_api_url
        self.hf_token = settings.hf_token

        if not self.hf_token:
            raise ValueError("HF_TOKEN is missing. Add HF_TOKEN in .env locally and Render environment variables.")

        if not self.api_url:
            raise ValueError("HF_API_URL is missing. Add HF_API_URL in .env locally and Render environment variables.")

        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }

        logger.info("✅ EmbeddingManager v2.0 — HuggingFace Inference API ready")
        logger.info(f"✅ HF API URL being used: {self.api_url}")

    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """Call HuggingFace Inference API using router feature-extraction endpoint."""

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={
                "inputs": texts,
                "options": {
                    "wait_for_model": True
                }
            },
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(
                f"HuggingFace API error: {response.status_code} — {response.text}"
            )

        return response.json()

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string."""

        if not text or not text.strip():
            return np.zeros(self._dimension)

        result = self._call_api([text])
        return np.array(result[0], dtype=np.float32)

    def embed_batch(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
        """Embed multiple text chunks in batches."""

        texts = [t for t in texts if t and t.strip()]

        if not texts:
            return np.array([])

        logger.info(f"Embedding {len(texts)} texts via HuggingFace Inference API")

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self._call_api(batch)
            all_embeddings.extend(result)

        return np.array(all_embeddings, dtype=np.float32)

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Cosine similarity."""

        a = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        b = embedding2 / (np.linalg.norm(embedding2) + 1e-8)

        return float(np.dot(a, b))