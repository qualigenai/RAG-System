import os
import requests
import numpy as np
from typing import List
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingManager:
    """
    RAG System v2.0 — HuggingFace Inference API.
    No model download — pure API calls like OpenAI.
    Free tier: 30,000 requests/month
    Dimension : 384
    """

    def __init__(self, model_name: str = None):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._dimension = 384
        self.hf_token = os.getenv("HF_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        logger.info(f"✅ EmbeddingManager v2.0 — HuggingFace Inference API ready")

    def _call_api(self, texts: list) -> list:
        """Call HuggingFace Inference API."""
        response = requests.post(
            HF_API_URL,
            headers=self.headers,
            json={
                "inputs": texts,
                "options": {"wait_for_model": True}
            },
            timeout=60
        )
        if response.status_code != 200:
            raise Exception(f"HuggingFace API error: {response.status_code} — {response.text}")
        return response.json()

    def embed_text(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            return np.zeros(self._dimension)
        result = self._call_api([text])
        return np.array(result[0])

    def embed_batch(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return np.array([])
        logger.info(f"Embedding {len(texts)} texts via HuggingFace Inference API")
        all_embeddings = []
        # Process in small batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self._call_api(batch)
            all_embeddings.extend(result)
        return np.array(all_embeddings)

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        a = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        b = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        return float(np.dot(a, b))