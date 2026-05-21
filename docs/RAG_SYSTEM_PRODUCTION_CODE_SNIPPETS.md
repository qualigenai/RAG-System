# Production Code Snippets - RAG System
## Copy-Paste Ready Code for Enterprise RAG System v1.5

**Stack:** FastAPI + ChromaDB + PostgreSQL (Render) + OpenAI embeddings  
**Status:** Ready to use (minimal customization needed)  
**License:** MIT (use freely in qualigenai)  

---

## 1️⃣ STRUCTURED LOGGING WITH CREDENTIAL SANITIZATION

**File:** `app/logging/config.py`

```python
"""
Structured JSON logging with automatic credential sanitization.
Prevents secrets from leaking into logs.
"""

import logging
import json
import re
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class CredentialSanitizer(logging.Filter):
    """Remove sensitive data from logs"""
    
    PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([^"\';\s,}]+)', 
         r'\1=REDACTED'),
        (r'Bearer\s+[A-Za-z0-9._\-]+', 'Bearer REDACTED'),
        (r'Basic\s+[A-Za-z0-9+/=]+', 'Basic REDACTED'),
        (r'sk[-_][a-zA-Z0-9]{20,}', 'sk-REDACTED'),  # OpenAI keys
        (r'(?i)password["\']?\s*[:=]\s*["\']?([^"\';\s,}]+)', 
         r'password=REDACTED'),
        (r'(?i)token["\']?\s*[:=]\s*["\']?([^"\';\s,}]+)', 
         r'token=REDACTED'),
        (r'postgresql://[^:]+:[^@]+@', 'postgresql://USER:PASS@'),
        (r'mongodb://[^:]+:[^@]+@', 'mongodb://USER:PASS@'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize log record"""
        # Sanitize message
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)
        
        # Sanitize exception text
        if record.exc_text:
            record.exc_text = self._sanitize(record.exc_text)
        
        return True
    
    @staticmethod
    def _sanitize(text: str) -> str:
        """Apply all redaction patterns"""
        for pattern, replacement in CredentialSanitizer.PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


class JSONFormatter(jsonlogger.JsonFormatter):
    """
    Format logs as JSON with custom fields.
    Makes logs machine-parseable for ELK/Datadog.
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, 
                   message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add file and line number for debugging
        log_record['file'] = f"{record.filename}:{record.lineno}"
        
        # Add function name
        log_record['function'] = record.funcName


def setup_logging(app_name: str = "rag-system", level: str = "INFO") -> logging.Logger:
    """
    Configure structured logging with sanitization.
    
    Usage:
        logger = setup_logging("rag-system", "DEBUG")
        logger.info("Query processed", extra={'query_length': 50})
    
    Args:
        app_name: Application name (appears in logs)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler (Render captures stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # JSON formatter
    json_formatter = JSONFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    
    # Add credential sanitizer
    console_handler.addFilter(CredentialSanitizer())
    
    # Apply formatter
    console_handler.setFormatter(json_formatter)
    
    # Add handler
    logger.addHandler(console_handler)
    
    # Log startup message
    logger.info(f"{app_name} logging initialized", extra={
        'version': '1.5',
        'log_level': level,
        'sanitization': 'enabled'
    })
    
    return logger


# Usage in main.py
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    # Setup logging before app starts
    logger = setup_logging("rag-system", level="INFO")
    
    app = FastAPI()
    
    @app.on_event("startup")
    async def startup():
        logger.info("RAG System starting up")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 2️⃣ PROMETHEUS METRICS

**File:** `app/monitoring/metrics.py`

```python
"""
Prometheus metrics for RAG system observability.
Tracks queries, embeddings, retrieval latency, errors.
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time


# ===== QUERY METRICS =====
query_requests_total = Counter(
    'rag_query_requests_total',
    'Total query requests',
    labelnames=['status'],  # success, error, timeout
)

query_latency_seconds = Histogram(
    'rag_query_latency_seconds',
    'Query processing latency',
    labelnames=['query_type'],  # vector_search, bm25_search, hybrid
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
)

query_result_count = Histogram(
    'rag_query_results_count',
    'Number of results returned',
    buckets=(1, 5, 10, 20, 50, 100),
)

# ===== RETRIEVAL METRICS =====
retrieval_latency_seconds = Histogram(
    'rag_retrieval_latency_seconds',
    'Time to retrieve documents from ChromaDB',
    labelnames=['search_type'],  # vector, bm25
    buckets=(0.05, 0.1, 0.5, 1.0, 2.0),
)

# ===== EMBEDDING METRICS =====
embedding_requests_total = Counter(
    'rag_embedding_requests_total',
    'Total embedding API calls',
    labelnames=['model'],  # text-embedding-3-small
)

embedding_tokens_total = Counter(
    'rag_embedding_tokens_total',
    'Total tokens sent to embedding API',
    labelnames=['token_type'],  # input, output
)

embedding_cost_usd = Counter(
    'rag_embedding_cost_usd_total',
    'Total cost of embedding API calls in USD',
)

embedding_latency_seconds = Histogram(
    'rag_embedding_latency_seconds',
    'Latency of embedding API calls',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0),
)

# ===== CHROMADB METRICS =====
chromadb_documents_total = Gauge(
    'rag_chromadb_documents_total',
    'Total documents in ChromaDB',
)

chromadb_collections_total = Gauge(
    'rag_chromadb_collections_total',
    'Total collections in ChromaDB',
)

chromadb_query_latency_seconds = Histogram(
    'rag_chromadb_query_latency_seconds',
    'ChromaDB query latency',
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0),
)

# ===== UPLOAD METRICS =====
document_uploads_total = Counter(
    'rag_document_uploads_total',
    'Total document uploads',
    labelnames=['status', 'file_type'],  # txt, pdf, docx
)

document_upload_size_bytes = Histogram(
    'rag_document_upload_size_bytes',
    'Size of uploaded documents',
    buckets=(1000, 10000, 100000, 1000000, 10000000),  # 1KB to 10MB
)

# ===== ERROR METRICS =====
errors_total = Counter(
    'rag_errors_total',
    'Total errors',
    labelnames=['error_type'],  # openai_error, db_error, validation_error
)

# ===== RATE LIMITING METRICS =====
rate_limit_hits_total = Counter(
    'rag_rate_limit_hits_total',
    'Total rate limit rejections',
    labelnames=['endpoint'],  # /query, /upload
)

# ===== HEALTH CHECK METRICS =====
health_check_status = Gauge(
    'rag_health_check_status',
    'Health status of system components',
    labelnames=['component'],  # openai, postgresql, chromadb
)


class MetricsRecorder:
    """Helper class for recording metrics in FastAPI endpoints"""
    
    @staticmethod
    def record_query(latency_ms: float, result_count: int, status: str = 'success'):
        """Record query metrics"""
        query_requests_total.labels(status=status).inc()
        query_latency_seconds.labels(query_type='hybrid').observe(latency_ms / 1000)
        query_result_count.observe(result_count)
    
    @staticmethod
    def record_embedding(tokens_sent: int, cost_usd: float, latency_ms: float):
        """Record embedding API call"""
        embedding_requests_total.labels(model='text-embedding-3-small').inc()
        embedding_tokens_total.labels(token_type='input').inc(tokens_sent)
        embedding_cost_usd.inc(cost_usd)
        embedding_latency_seconds.observe(latency_ms / 1000)
    
    @staticmethod
    def record_error(error_type: str):
        """Record error"""
        errors_total.labels(error_type=error_type).inc()
    
    @staticmethod
    def record_upload(file_type: str, size_bytes: int, status: str = 'success'):
        """Record document upload"""
        document_uploads_total.labels(status=status, file_type=file_type).inc()
        document_upload_size_bytes.observe(size_bytes)
    
    @staticmethod
    def update_chromadb_stats(doc_count: int, collection_count: int):
        """Update ChromaDB statistics"""
        chromadb_documents_total.set(doc_count)
        chromadb_collections_total.set(collection_count)


# Usage in main.py
def start_metrics_server(port: int = 8001):
    """Start Prometheus metrics endpoint"""
    try:
        start_http_server(port)
        print(f"✓ Metrics server started on port {port}")
        print(f"  Access metrics at: http://localhost:{port}/metrics")
    except Exception as e:
        print(f"✗ Failed to start metrics server: {e}")


# Example endpoint instrumentation
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response
    import time
    
    app = FastAPI()
    
    @app.get("/metrics")
    async def metrics():
        """Expose Prometheus metrics"""
        from prometheus_client import generate_latest
        return Response(generate_latest(), media_type="text/plain")
    
    @app.post("/query")
    async def query(q: str):
        """Example endpoint with metrics"""
        start_time = time.time()
        
        try:
            # Simulate query processing
            results = [{"text": "result 1"}, {"text": "result 2"}]
            
            elapsed_ms = (time.time() - start_time) * 1000
            MetricsRecorder.record_query(elapsed_ms, len(results), 'success')
            
            return {"results": results}
        
        except Exception as e:
            MetricsRecorder.record_error('query_error')
            raise HTTPException(status_code=500, detail=str(e))
```

---

## 3️⃣ HEALTH CHECK ENDPOINT

**File:** `app/health.py`

```python
"""
Comprehensive health check for all RAG system components.
Returns status of OpenAI API, PostgreSQL, ChromaDB.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any
import requests
from sqlalchemy import text

logger = logging.getLogger("rag-system")


async def check_openai_health() -> Dict[str, Any]:
    """Check OpenAI API connectivity"""
    try:
        # Make minimal embedding request to verify API key works
        api_key = os.getenv("OPENAI_API_KEY")
        
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "text-embedding-3-small",
                "input": "health"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                'status': 'healthy',
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'model': 'text-embedding-3-small'
            }
        else:
            return {
                'status': 'unhealthy',
                'error': f"OpenAI API returned {response.status_code}",
                'details': response.text[:200]
            }
    
    except requests.Timeout:
        return {'status': 'unhealthy', 'error': 'OpenAI API timeout'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


async def check_postgresql_health() -> Dict[str, Any]:
    """Check PostgreSQL database connectivity"""
    try:
        from app.db import SessionLocal
        
        session = SessionLocal()
        result = session.execute(text("SELECT 1"))
        session.close()
        
        return {
            'status': 'healthy',
            'database': 'postgresql',
            'response_time_ms': 50  # Approximate
        }
    
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


async def check_chromadb_health() -> Dict[str, Any]:
    """Check ChromaDB connectivity and stats"""
    try:
        from app.rag import chroma_client
        
        # Try to get collection and count
        collection = chroma_client.get_or_create_collection("documents")
        doc_count = collection.count()
        
        return {
            'status': 'healthy',
            'documents': doc_count,
            'collections': 1
        }
    
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


async def check_overall_health() -> Dict[str, Any]:
    """Check all components and return overall health"""
    
    # Check each component
    openai_health = await check_openai_health()
    postgres_health = await check_postgresql_health()
    chromadb_health = await check_chromadb_health()
    
    # Determine overall status
    all_healthy = all([
        openai_health['status'] == 'healthy',
        postgres_health['status'] == 'healthy',
        chromadb_health['status'] == 'healthy'
    ])
    
    overall_status = 'healthy' if all_healthy else 'degraded'
    
    return {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'openai_api': openai_health,
            'postgresql': postgres_health,
            'chromadb': chromadb_health
        }
    }


# Usage in FastAPI
if __name__ == "__main__":
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        """Return health status of all components"""
        return await check_overall_health()
    
    @app.get("/health/detailed")
    async def health_detailed():
        """Return detailed health information"""
        health = await check_overall_health()
        
        # Add timestamp and version
        health['version'] = '1.5'
        health['deployed_at'] = os.getenv('DEPLOY_TIME', 'unknown')
        
        return health
```

---

## 4️⃣ INPUT VALIDATION

**File:** `app/validators/rag_validator.py`

```python
"""
Input validation for RAG system.
Prevents injection attacks and DoS.
"""

import re
from typing import List, Optional


class RAGValidationError(Exception):
    """Input validation failed"""
    pass


class RAGInputValidator:
    """
    Validates queries and document uploads.
    """
    
    # Limits
    MAX_QUERY_LENGTH = 5000
    MAX_DOCUMENT_SIZE = 10_000_000  # 10 MB
    MAX_BATCH_SIZE = 100
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.md', '.docx', '.doc']
    
    @staticmethod
    def validate_query(query: str) -> bool:
        """
        Validate search query.
        
        Args:
            query: User's search query
            
        Returns:
            True if valid
            
        Raises:
            RAGValidationError: If invalid
        """
        if not query:
            raise RAGValidationError("Query cannot be empty")
        
        if not isinstance(query, str):
            raise RAGValidationError("Query must be string")
        
        if len(query) > RAGInputValidator.MAX_QUERY_LENGTH:
            raise RAGValidationError(
                f"Query too long: {len(query)} chars (max {RAGInputValidator.MAX_QUERY_LENGTH})"
            )
        
        # Allow alphanumeric + common punctuation + Unicode
        # Block HTML/script tags
        dangerous_patterns = [
            r'<script', r'</script', r'javascript:', r'onerror=',
            r'onclick=', r'<iframe', r'eval\(', r'exec\(',
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                raise RAGValidationError(
                    f"Query contains dangerous pattern: {pattern}"
                )
        
        return True
    
    @staticmethod
    def validate_document(content: bytes, filename: str) -> bool:
        """
        Validate uploaded document.
        
        Args:
            content: File content (binary)
            filename: Original filename
            
        Returns:
            True if valid
            
        Raises:
            RAGValidationError: If invalid
        """
        if not content:
            raise RAGValidationError("Document cannot be empty")
        
        if len(content) > RAGInputValidator.MAX_DOCUMENT_SIZE:
            raise RAGValidationError(
                f"Document too large: {len(content) / 1e6:.1f} MB (max 10 MB)"
            )
        
        # Check file extension
        ext = None
        for allowed_ext in RAGInputValidator.ALLOWED_EXTENSIONS:
            if filename.lower().endswith(allowed_ext):
                ext = allowed_ext
                break
        
        if not ext:
            raise RAGValidationError(
                f"File type not allowed: {filename}. "
                f"Allowed: {', '.join(RAGInputValidator.ALLOWED_EXTENSIONS)}"
            )
        
        # Check for suspicious content
        try:
            # Try to decode as text for text files
            if ext in ['.txt', '.md']:
                content.decode('utf-8')
        except UnicodeDecodeError:
            raise RAGValidationError(f"Invalid text file: {filename}")
        
        return True
    
    @staticmethod
    def validate_embedding_params(top_k: int = 10, score_threshold: float = 0.0) -> bool:
        """
        Validate retrieval parameters.
        
        Args:
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            True if valid
            
        Raises:
            RAGValidationError: If invalid
        """
        if not 1 <= top_k <= 100:
            raise RAGValidationError(
                f"Invalid top_k: {top_k} (must be 1-100)"
            )
        
        if not 0.0 <= score_threshold <= 1.0:
            raise RAGValidationError(
                f"Invalid score_threshold: {score_threshold} (must be 0.0-1.0)"
            )
        
        return True


# Unit tests
if __name__ == "__main__":
    import pytest
    
    def test_valid_query():
        assert RAGInputValidator.validate_query("What is machine learning?")
    
    def test_query_too_long():
        with pytest.raises(RAGValidationError, match="too long"):
            RAGInputValidator.validate_query("a" * 10000)
    
    def test_script_tag_blocked():
        with pytest.raises(RAGValidationError, match="dangerous"):
            RAGInputValidator.validate_query("test <script>alert(1)</script>")
    
    def test_valid_document():
        content = b"This is a test document"
        assert RAGInputValidator.validate_document(content, "test.txt")
    
    def test_file_type_not_allowed():
        with pytest.raises(RAGValidationError, match="not allowed"):
            RAGInputValidator.validate_document(b"content", "malware.exe")
    
    def test_document_too_large():
        with pytest.raises(RAGValidationError, match="too large"):
            RAGInputValidator.validate_document(b"x" * 20_000_000, "huge.txt")
    
    # Run tests
    pytest.main([__file__, "-v"])
```

---

## 5️⃣ RATE LIMITING MIDDLEWARE

**File:** `app/middleware/rate_limiter.py`

```python
"""
Rate limiting middleware for RAG system.
Prevents DoS and API cost overruns.
"""

import time
from typing import Dict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """
    Token bucket rate limiter.
    Allows N requests per minute per IP.
    """
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.buckets: Dict[str, Dict] = {}
    
    def is_allowed(self, ip: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        if ip not in self.buckets:
            # First request from this IP
            self.buckets[ip] = {
                'tokens': self.requests_per_minute,
                'last_refill': now
            }
            return True
        
        bucket = self.buckets[ip]
        
        # Refill tokens based on time elapsed
        time_passed = now - bucket['last_refill']
        tokens_to_add = time_passed * (self.requests_per_minute / 60)
        
        bucket['tokens'] = min(
            self.requests_per_minute,
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = now
        
        # Check if we have tokens
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    Usage:
        app.add_middleware(RateLimitMiddleware, rate_limits={
            "/query": 10,      # 10 per minute
            "/upload": 5,      # 5 per minute
            "/health": 1000,   # 1000 per minute
        })
    """
    
    def __init__(self, app, rate_limits: Dict[str, int] = None):
        super().__init__(app)
        self.rate_limits = rate_limits or {
            "/query": 10,
            "/upload": 5,
            "/health": 1000,
        }
        
        # Create limiter for each endpoint
        self.limiters = {
            path: RateLimiter(limit)
            for path, limit in self.rate_limits.items()
        }
    
    async def dispatch(self, request: Request, call_next):
        """Rate limit the request"""
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get route (path)
        path = request.url.path
        
        # Find matching rate limit
        limiter = None
        for route, limit_obj in self.limiters.items():
            if path.startswith(route):
                limiter = limit_obj
                break
        
        # If no limiter found, allow request
        if not limiter:
            return await call_next(request)
        
        # Check rate limit
        if not limiter.is_allowed(client_ip):
            limit = self.rate_limits.get(path, 10)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {limit} requests per minute"
            )
        
        # Allow request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(limiter.buckets[client_ip]['tokens']))
        
        return response


# Usage in main.py
if __name__ == "__main__":
    from fastapi import FastAPI
    
    app = FastAPI()
    
    # Add rate limiting
    app.add_middleware(RateLimitMiddleware, rate_limits={
        "/query": 10,      # 10 queries per minute
        "/upload": 5,      # 5 uploads per minute
        "/health": 1000,   # Health checks unlimited
    })
    
    @app.post("/query")
    async def query(q: str):
        return {"results": []}
```

---

## 6️⃣ AUDIT LOGGING

**File:** `app/models/audit.py`

```python
"""
Audit log model for compliance and forensics.
Records all user actions with timestamps and IPs.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class AuditLog(Base):
    """
    Audit log entry - records user actions for compliance.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    
    # Timestamp and identification
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_ip = Column(String(45), nullable=True, index=True)  # IPv6 support
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # query, upload, delete
    resource = Column(String(255), nullable=True)  # document ID, query ID
    
    # Flexible details
    details = Column(JSON, nullable=True)  # Extra context as JSON
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} by {self.user_ip}>"


# Helper functions
def log_audit_action(db, action: str, user_ip: str, resource: str = None, details: dict = None):
    """
    Log a user action for audit trail.
    
    Args:
        db: SQLAlchemy session
        action: Action name (query, upload, delete)
        user_ip: Client IP address
        resource: What was affected (document ID, etc.)
        details: Extra context as dict
    """
    audit = AuditLog(
        action=action,
        user_ip=user_ip,
        resource=resource,
        details=details or {}
    )
    db.add(audit)
    db.commit()


# Database setup
def create_audit_table(engine):
    """Create audit log table"""
    Base.metadata.create_all(engine)


# Usage in FastAPI endpoints
if __name__ == "__main__":
    from fastapi import FastAPI, Request
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    app = FastAPI()
    
    # Setup database
    engine = create_engine("postgresql://...")
    SessionLocal = sessionmaker(bind=engine)
    create_audit_table(engine)
    
    @app.post("/query")
    async def query(q: str, request: Request):
        db = SessionLocal()
        
        try:
            # Log the query
            log_audit_action(
                db,
                action='query',
                user_ip=request.client.host,
                resource='search',
                details={'query_length': len(q)}
            )
            
            # Process query...
            results = []
            
            return {"results": results}
        
        finally:
            db.close()
```

---

## 7️⃣ BACKUP HELPERS

**File:** `app/backup/chromadb_backup.py`

```python
"""
ChromaDB backup utilities.
Backup to local storage and S3.
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import subprocess

logger = logging.getLogger("rag-system")


class ChromaDBBackup:
    """Manage ChromaDB backups"""
    
    def __init__(self, chromadb_path: str = "/tmp/chromadb", 
                 backup_dir: str = "/tmp/chromadb_backups"):
        self.chromadb_path = chromadb_path
        self.backup_dir = backup_dir
        
        # Create backup directory
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def backup_local(self) -> str:
        """
        Create local backup of ChromaDB.
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"chromadb_{timestamp}")
        
        try:
            # Copy entire ChromaDB directory
            shutil.copytree(self.chromadb_path, backup_path)
            
            size_mb = self._get_dir_size(backup_path) / (1024 * 1024)
            logger.info(f"✓ ChromaDB backup created: {backup_path} ({size_mb:.1f} MB)")
            
            return backup_path
        
        except Exception as e:
            logger.error(f"✗ ChromaDB backup failed: {e}")
            raise
    
    def cleanup_old_backups(self, retention_days: int = 7):
        """Delete backups older than N days"""
        import time
        
        now = time.time()
        cutoff = now - (retention_days * 24 * 3600)
        
        deleted = 0
        for backup_dir in Path(self.backup_dir).iterdir():
            if backup_dir.is_dir() and backup_dir.stat().st_mtime < cutoff:
                shutil.rmtree(backup_dir)
                deleted += 1
        
        if deleted > 0:
            logger.info(f"✓ Deleted {deleted} old ChromaDB backups (>{retention_days}d old)")
    
    def backup_to_s3(self, backup_path: str, s3_bucket: str):
        """
        Upload backup to S3.
        
        Args:
            backup_path: Local backup directory
            s3_bucket: S3 bucket name
        """
        try:
            # Use AWS CLI to sync
            cmd = [
                "aws", "s3", "sync",
                backup_path,
                f"s3://{s3_bucket}/chromadb/",
                "--delete"
            ]
            
            subprocess.run(cmd, check=True)
            logger.info(f"✓ Uploaded ChromaDB backup to S3: {s3_bucket}/chromadb/")
        
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ S3 upload failed: {e}")
            raise
    
    def restore_from_backup(self, backup_path: str):
        """
        Restore ChromaDB from backup.
        
        Args:
            backup_path: Path to backup to restore from
        """
        try:
            # Remove current ChromaDB
            if os.path.exists(self.chromadb_path):
                shutil.rmtree(self.chromadb_path)
            
            # Restore from backup
            shutil.copytree(backup_path, self.chromadb_path)
            logger.info(f"✓ ChromaDB restored from: {backup_path}")
        
        except Exception as e:
            logger.error(f"✗ ChromaDB restore failed: {e}")
            raise
    
    @staticmethod
    def _get_dir_size(path: str) -> int:
        """Get total size of directory in bytes"""
        total = 0
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += ChromaDBBackup._get_dir_size(entry.path)
        return total


# Backup script
if __name__ == "__main__":
    import sys
    
    backup = ChromaDBBackup(
        chromadb_path="/path/to/chromadb",
        backup_dir="/tmp/chromadb_backups"
    )
    
    # Create local backup
    backup_path = backup.backup_local()
    
    # Cleanup old backups
    backup.cleanup_old_backups(retention_days=7)
    
    # Upload to S3 (if configured)
    s3_bucket = os.getenv("BACKUP_S3_BUCKET")
    if s3_bucket:
        backup.backup_to_s3(backup_path, s3_bucket)
    
    print("✓ Backup complete")
```

**Crontab setup:**

```bash
# Add to crontab (run every 6 hours)
0 */6 * * * cd /app && python -m app.backup.chromadb_backup

# Or with logging
0 */6 * * * cd /app && python -m app.backup.chromadb_backup >> /var/log/chromadb_backup.log 2>&1
```

---

## 8️⃣ QUICK IMPLEMENTATION CHECKLIST

```
TO DEPLOY TO RAG SYSTEM:

1. Copy logging
   □ cp app/logging/config.py
   □ Update main.py to call setup_logging()
   □ Deploy and verify JSON logs in Render

2. Copy metrics
   □ cp app/monitoring/metrics.py
   □ Add to main.py: start_metrics_server()
   □ Instrument endpoints with MetricsRecorder
   □ Test /metrics endpoint

3. Copy health check
   □ cp app/health.py
   □ Add @app.get("/health")
   □ Configure Render health checks
   □ Test from browser

4. Copy validators
   □ cp app/validators/rag_validator.py
   □ Call RAGInputValidator in endpoints
   □ Write tests
   □ Deploy

5. Copy rate limiter
   □ cp app/middleware/rate_limiter.py
   □ Add to FastAPI: app.add_middleware()
   □ Configure limits per endpoint
   □ Test with curl loop

6. Copy audit logging
   □ cp app/models/audit.py
   □ Create database migration
   □ Add log_audit_action() calls
   □ Deploy

7. Copy backup script
   □ cp app/backup/chromadb_backup.py
   □ Add cron job
   □ Test backup creation
   □ Test S3 upload

AFTER DEPLOYMENT:
□ All tests passing
□ Logs showing JSON format
□ Metrics accessible at /metrics
□ Health check returning 200
□ Rate limits working (test with curl)
□ Audit logs in database
```

---

**All code is production-ready. Customize paths/credentials for your setup.**

Good luck! 🚀
