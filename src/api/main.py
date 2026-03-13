from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from typing import List
import os

from src.api.models import (
    QueryRequest, QueryResponse, RetrievedDocument,
    HealthResponse, StatsResponse, UploadResponse
)
from src.core.config import settings
from src.core.retriever import HybridRetriever
from src.core.loader import DocumentProcessor

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Retrieval Augmented Generation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
retriever = None
processor = None
indexed_count = 0

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global retriever, processor, indexed_count
    
    logger.info("Starting RAG system...")
    retriever = HybridRetriever()
    processor = DocumentProcessor()
    indexed_count = 0
    
    # Load existing documents if any
    if os.path.exists("data"):
        documents = processor.process_directory("data")
        if documents:
            retriever.index_documents(documents)
            indexed_count = len(documents)
            logger.info(f"Loaded {indexed_count} documents from data directory")
    
    logger.info("✅ RAG system ready!")

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "RAG System API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    if not retriever:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return HealthResponse(
        status="healthy",
        documents_indexed=indexed_count,
        embedding_model=settings.embedding_model,
        vector_store_type="in-memory"
    )

@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats():
    """Get system statistics"""
    if not retriever:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    vector_info = retriever.vector_db.get_collection_info()
    
    return StatsResponse(
        total_documents=indexed_count,
        total_chunks=vector_info.get("points_count", 0),
        embedding_dimension=retriever.embedder.get_embedding_dimension(),
        vector_store_status=vector_info.get("status", "unknown"),
        bm25_indexed=True
    )

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query(request: QueryRequest):
    """Query the RAG system"""
    if not retriever:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    start_time = time.time()
    
    try:
        # Retrieve relevant documents
        results = retriever.retrieve(request.query, top_k=request.top_k)
        
        # Convert to response format
        retrieved_docs = [
            RetrievedDocument(
                id=r["id"],
                score=r["score"],
                text=r["text"],
                source=r["source"],
                metadata=r.get("metadata", {})
            )
            for r in results
        ]
        
        # Generate answer from retrieved documents
        answer = None
        if retrieved_docs:
            context = "\n\n".join([doc.text for doc in retrieved_docs[:3]])
            answer = f"Based on retrieved documents:\n\n{context}"
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            retrieved_documents=retrieved_docs,
            answer=answer,
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a document"""
    global indexed_count
    
    if not retriever or not processor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Save file
        os.makedirs("data", exist_ok=True)
        filepath = f"data/{file.filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Process and index
        documents = [{
            "text": text,
            "source": filepath,
            "metadata": {"type": "uploaded"}
        }]
        
        chunked = processor.chunk_documents(documents)
        retriever.index_documents(chunked)
        indexed_count += len(chunked)
        
        logger.info(f"Uploaded and indexed {file.filename} - {len(chunked)} chunks")
        
        return UploadResponse(
            filename=file.filename,
            chunks_created=len(chunked),
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear", tags=["Admin"])
async def clear_documents():
    """Clear all indexed documents"""
    global retriever, indexed_count
    
    retriever = HybridRetriever()
    indexed_count = 0
    
    return {"status": "cleared", "message": "All documents cleared"}

# Test
if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    
    print("Starting RAG API server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)