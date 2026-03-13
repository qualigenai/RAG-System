from pydantic import BaseModel
from typing import List, Optional, Dict

# Request Models
class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    top_k: int = 5
    
class UploadRequest(BaseModel):
    """Request model for upload endpoint"""
    filename: str
    content: str

# Response Models
class RetrievedDocument(BaseModel):
    """Retrieved document with similarity score"""
    id: int
    score: float
    text: str
    source: str
    metadata: Dict = {}

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    query: str
    retrieved_documents: List[RetrievedDocument]
    answer: Optional[str] = None
    processing_time: float

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    documents_indexed: int
    embedding_model: str
    vector_store_type: str

class StatsResponse(BaseModel):
    """Response model for stats endpoint"""
    total_documents: int
    total_chunks: int
    embedding_dimension: int
    vector_store_status: str
    bm25_indexed: bool

class UploadResponse(BaseModel):
    """Response model for upload endpoint"""
    filename: str
    chunks_created: int
    status: str

# Test
if __name__ == "__main__":
    # Test model creation
    req = QueryRequest(query="What is RAG?", top_k=5)
    print(f"✅ QueryRequest created: {req}")
    
    doc = RetrievedDocument(id=0, score=0.95, text="RAG is...", source="doc.txt")
    print(f"✅ RetrievedDocument created: {doc}")
    
    print("✅ All models test passed!")