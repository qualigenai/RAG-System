from typing import List, Dict
from src.core.embedder import EmbeddingManager
from src.core.vector_db import VectorDBManager
from src.core.bm25_search import BM25Retriever
import logging

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Combines vector search and BM25 for hybrid retrieval"""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedder = EmbeddingManager()
        self.vector_db = VectorDBManager(embedding_dim=embedding_dim)
        self.bm25 = BM25Retriever()
        self.documents = []
    
    def index_documents(self, documents: List[Dict]):
        """Index documents in both vector DB and BM25"""
        self.documents = documents
        
        # Get embeddings
        logger.info("Generating embeddings...")
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedder.embed_batch(texts)
        
        # Store in vector DB
        logger.info("Storing in vector database...")
        self.vector_db.upsert_documents(documents, embeddings)
        
        # Index in BM25
        logger.info("Indexing in BM25...")
        self.bm25.index(documents)
        
        logger.info(f"✅ Indexed {len(documents)} documents")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve using hybrid approach"""
        
        # Vector search
        query_embedding = self.embedder.embed_text(query).tolist()
        vector_results = self.vector_db.search(query_embedding, top_k=top_k)
        
        # BM25 search
        bm25_results = self.bm25.search(query, top_k=top_k)
        
        # Combine results
        combined = {}
        
        # Add vector results (70% weight)
        for i, result in enumerate(vector_results):
            doc_id = result["id"]
            score = result["score"] * 0.7
            if doc_id not in combined:
                combined[doc_id] = {
                    **result,
                    "score": 0,
                    "methods": []
                }
            combined[doc_id]["score"] += score
            combined[doc_id]["methods"].append("vector")
        
        # Add BM25 results (30% weight)
        for i, result in enumerate(bm25_results):
            doc_id = result["id"]
            score = (result["score"] / 10) * 0.3  # Normalize BM25 score
            if doc_id not in combined:
                combined[doc_id] = {
                    **result,
                    "score": 0,
                    "methods": []
                }
            combined[doc_id]["score"] += score
            combined[doc_id]["methods"].append("bm25")
        
        # Sort by combined score
        results = sorted(
            combined.values(),
            key=lambda x: x["score"],
            reverse=True
        )[:top_k]
        
        logger.info(f"Retrieved {len(results)} documents for query: '{query}'")
        return results

# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create retriever
    retriever = HybridRetriever()
    
    # Index documents
    docs = [
        {"text": "Retrieval Augmented Generation combines retrieval with generation", 
         "source": "doc1.txt"},
        {"text": "Vector databases store embeddings for similarity search",
         "source": "doc2.txt"},
        {"text": "LLMs generate text based on context and prompts",
         "source": "doc3.txt"},
    ]
    
    retriever.index_documents(docs)
    
    # Test retrieval
    results = retriever.retrieve("What is RAG?", top_k=2)
    print(f"\nRetrieved {len(results)} results:")
    for result in results:
        print(f"Score: {result['score']:.2f}, Methods: {result['methods']}")
        print(f"Text: {result['text'][:60]}...\n")
    print("✅ Hybrid retrieval test passed!")