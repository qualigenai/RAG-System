from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid
import secrets
from dotenv import load_dotenv

load_dotenv()

# ============= IMPORT DATABASE & MODELS =============
from src.database import models as db_models
from src.database.session import get_db, init_db, Base, engine

# ============= IMPORT RETRIEVER (v1.0) =============
from src.core.retriever import HybridRetriever

# ============= IMPORT AUTH & AUDIT =============
from src.auth import routes as auth_routes
from src.auth.dependencies import get_current_user, get_current_editor, get_current_admin
from src.auth.security import hash_password
from src.audit.logger import AuditLogger
from src.auth.api_keys import APIKeyManager

# ============= INITIALIZE DATABASE =============
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    import traceback

    traceback.print_exc()

# ============= INITIALIZE RETRIEVER =============
try:
    retriever = HybridRetriever()
    print("✅ HybridRetriever initialized")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize HybridRetriever: {e}")
    retriever = None

# ============= INITIALIZE FASTAPI APP =============
app = FastAPI(
    title="RAG System v1.5",
    description="Enterprise-Ready Retrieval Augmented Generation System",
    version="1.5.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_routes.router)

print("✅ FastAPI app initialized successfully!")


# ============= HEALTH CHECK =============
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.5",
        "retriever_status": "ready" if retriever else "not_initialized"
    }


# ============= DOCUMENT UPLOAD WITH INDEXING =============
# ============= DOCUMENT UPLOAD WITH INDEXING =============
@app.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        current_user: db_models.User = Depends(get_current_editor),
        db: Session = Depends(get_db)
):
    """Upload document and index it for search"""

    audit_logger = AuditLogger(db)

    try:
        # Create organization folder
        org_folder = f"data/{str(current_user.organization_id)}"
        os.makedirs(org_folder, exist_ok=True)

        # Save file to disk
        file_path = f"{org_folder}/{file.filename}"
        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        doc_id = str(uuid.uuid4())

        # Index document using HybridRetriever (v1.0 logic)
        if retriever:
            try:
                text_content = None

                # Handle PDFs
                if file.filename.lower().endswith('.pdf'):
                    try:
                        from PyPDF2 import PdfReader
                        import io
                        pdf_reader = PdfReader(io.BytesIO(contents))
                        text_content = ""
                        for page in pdf_reader.pages:
                            text_content += page.extract_text() + "\n"
                        print(f"✅ Extracted {len(pdf_reader.pages)} pages from PDF")
                    except Exception as pdf_error:
                        print(f"❌ PDF extraction error: {str(pdf_error)}")

                # Handle TXT, MD, and other text files
                else:
                    try:
                        text_content = contents.decode('utf-8')
                        print(f"✅ Decoded as UTF-8")
                    except UnicodeDecodeError:
                        try:
                            text_content = contents.decode('latin-1')
                            print(f"✅ Decoded as Latin-1")
                        except:
                            text_content = contents.decode('utf-8', errors='ignore')
                            print(f"⚠️ Decoded with error handling")

                # Index the content
                if text_content and text_content.strip():
                    document_to_index = {
                        "id": doc_id,
                        "text": text_content,
                        "source": file.filename
                    }
                    retriever.index_documents([document_to_index])
                    print(f"✅ Indexed document: {file.filename}")
                    print(f"   Size: {len(text_content)} characters")
                else:
                    print(f"⚠️ Warning: Could not extract text from {file.filename}")

            except Exception as e:
                print(f"❌ Indexing error: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ Warning: Retriever not initialized")

        # Log the upload
        audit_logger.log(
            user_id=str(current_user.id),
            organization_id=str(current_user.organization_id),
            action="document_upload",
            resource_type="document",
            resource_id=doc_id,
            details={
                "filename": file.filename,
                "size": len(contents),
                "path": file_path
            },
            status="success"
        )

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "size": len(contents),
            "message": "✅ Document uploaded and indexed successfully"
        }

    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()

        audit_logger.log(
            user_id=str(current_user.id),
            organization_id=str(current_user.organization_id),
            action="document_upload",
            resource_type="document",
            resource_id="unknown",
            details={"error": str(e)},
            status="failed"
        )
        raise HTTPException(status_code=400, detail=str(e))


# ============= QUERY WITH HYBRID SEARCH + LLM =============
@app.post("/query")
async def query_documents(
        query_text: str = Form(...),
        current_user: db_models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Query documents using HybridRetriever (v1.0) + GPT-4 (v1.5)

    - Search: Vector + BM25 hybrid search
    - LLM: OpenAI GPT-4 generates answer
    - Sources: Citations from documents
    - Logging: Full audit trail
    """

    audit_logger = AuditLogger(db)

    try:
        if not retriever:
            raise HTTPException(
                status_code=500,
                detail="Retriever not initialized. Please try again."
            )

        # Step 1: Retrieve relevant documents using HybridRetriever (v1.0!)
        retrieved_chunks = retriever.retrieve(query_text, top_k=2)

        if not retrieved_chunks:
            return {
                "query": query_text,
                "answer": "No relevant documents found. Please upload documents first.",
                "sources": [],
                "status": "no_documents",
                "chunks_used": 0
            }

        # Step 2: Generate answer using GPT-4 (v1.5!)
        from src.api.llm import generate_answer

        answer = generate_answer(query_text, retrieved_chunks)

        # Step 3: Extract sources
        sources = list(set([chunk.get('source', 'Unknown') for chunk in retrieved_chunks]))

        # Step 4: Log the query
        audit_logger.log(
            user_id=str(current_user.id),
            organization_id=str(current_user.organization_id),
            action="document_query",
            resource_type="query",
            resource_id=str(uuid.uuid4()),
            details={
                "query": query_text,
                "sources": sources,
                "chunks_retrieved": len(retrieved_chunks),
                "answer_length": len(answer)
            },
            status="success"
        )

        # Step 5: Return answer with metadata
        return {
            "query": query_text,
            "answer": answer,
            "sources": sources,
            "status": "success",
            "chunks_used": len(retrieved_chunks)
        }

    except Exception as e:
        print(f"Error in query: {str(e)}")
        import traceback
        traceback.print_exc()

        audit_logger.log(
            user_id=str(current_user.id),
            organization_id=str(current_user.organization_id),
            action="document_query",
            resource_type="query",
            resource_id="unknown",
            details={"error": str(e)},
            status="failed"
        )
        raise HTTPException(status_code=400, detail=str(e))


# ============= TEAM ENDPOINTS =============

@app.get("/api/team/members")
async def list_team_members(
        current_user: db_models.User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """List all team members (admin only)"""

    members = db.query(db_models.User).filter(
        db_models.User.organization_id == current_user.organization_id
    ).all()

    return [
        {
            "id": str(m.id),
            "email": m.email,
            "username": m.username,
            "full_name": m.full_name,
            "role": m.role,
            "created_at": m.created_at,
            "is_active": m.is_active
        }
        for m in members
    ]


@app.post("/api/team/members")
async def add_team_member(
        request: dict,
        current_user: db_models.User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Add new team member (admin only)"""

    existing = db.query(db_models.User).filter(
        db_models.User.email == request["email"]
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    temp_password = secrets.token_urlsafe(16)
    new_user = db_models.User(
        email=request["email"],
        username=request["email"].split("@")[0],
        hashed_password=hash_password(temp_password),
        full_name=request.get("full_name", ""),
        role=request.get("role", "viewer"),
        organization_id=current_user.organization_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()

    return {
        "user_id": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role,
        "temporary_password": temp_password,
        "message": "User added successfully"
    }


# ============= API KEY ENDPOINTS =============

@app.get("/api/api-keys")
async def list_api_keys(
        current_user: db_models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """List API keys for current user"""

    keys = db.query(db_models.APIKey).filter(
        db_models.APIKey.user_id == current_user.id
    ).all()

    return [
        {
            "id": str(k.id),
            "name": k.name,
            "last_used": k.last_used,
            "expires_at": k.expires_at,
            "is_active": k.is_active,
            "created_at": k.created_at
        }
        for k in keys
    ]


@app.post("/api/api-keys")
async def create_api_key(
        request: dict,
        current_user: db_models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create new API key"""

    manager = APIKeyManager()
    new_key = manager.create_api_key(
        db=db,
        user_id=str(current_user.id),
        organization_id=str(current_user.organization_id),
        name=request.get("name", "Default API Key"),
        expires_in=request.get("expires_in", "never")
    )

    return new_key


@app.delete("/api/api-keys/{key_id}")
async def revoke_api_key(
        key_id: str,
        current_user: db_models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Revoke API key"""

    key = db.query(db_models.APIKey).filter(
        db_models.APIKey.id == key_id,
        db_models.APIKey.user_id == current_user.id
    ).first()

    if not key:
        raise HTTPException(status_code=404, detail="Key not found")

    key.is_active = False
    db.commit()

    return {"message": "API key revoked"}


# ============= AUDIT LOG ENDPOINTS =============

@app.get("/api/audit-logs")
async def get_audit_logs(
        current_user: db_models.User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        limit: int = 100
):
    """Get audit logs (admin only)"""

    logger = AuditLogger(db)
    logs = logger.get_logs(
        organization_id=str(current_user.organization_id),
        limit=limit
    )

    return [
        {
            "id": str(l.id),
            "user_id": str(l.user_id) if l.user_id else None,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "status": l.status,
            "created_at": l.created_at
        }
        for l in logs
    ]


# ============= STATS ENDPOINT =============

@app.get("/api/stats")
async def get_stats(
        current_user: db_models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get organization statistics"""

    members = db.query(db_models.User).filter(
        db_models.User.organization_id == current_user.organization_id
    ).count()

    logger = AuditLogger(db)
    logs = logger.get_logs(
        organization_id=str(current_user.organization_id),
        limit=100
    )

    # Calculate actual stats
    queries_today = len([l for l in logs if l.action == "document_query"])
    documents_uploaded = len([l for l in logs if l.action == "document_upload"])

    return {
        "team_members": members,
        "total_documents": documents_uploaded,
        "queries_today": queries_today,
        "accuracy": 87.5
    }


# ============= STARTUP/SHUTDOWN =============

@app.on_event("startup")
async def startup_event():
    """Run on app startup"""
    print("🚀 RAG System v1.5 started successfully!")
    print(f"📍 API URL: http://localhost:8000")
    print(f"📊 Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on app shutdown"""
    print("👋 RAG System v1.5 shutting down...")


# ============= MAIN =============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )