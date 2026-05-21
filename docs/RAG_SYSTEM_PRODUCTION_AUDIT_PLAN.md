# Production Audit & Hardening Plan
## Enterprise RAG System v1.5 (Post-Deployment)

**System Status:** LIVE IN PRODUCTION (May 2026)  
**Deployment Platform:** Render (Free Tier)  
**Backend:** rag-system-api-s09i.onrender.com  
**Frontend:** rag-system-frontend-53uy.onrender.com  
**Owner:** qualigenai (Ram)  

---

## Executive Summary

Your RAG System is live but **operating blind**. The deployment works, but critical controls are missing:

```
✓ Deployed
✓ Accessible
✗ Monitored
✗ Secured
✗ Recoverable
✗ Scalable
✗ Compliant
```

This audit identifies gaps in the 7 control pillars and provides a **30-day hardening roadmap** to move from "works" to "production-grade."

---

## 🔍 CURRENT STATE ASSESSMENT

### What's Working
- FastAPI backend responds (health check: `GET /health`)
- ChromaDB hybrid retrieval operational (70% vector + 30% BM25)
- OpenAI embeddings (text-embedding-3-small) functional
- PostgreSQL storage connected (Render-hosted)
- Frontend accessible to users

### What's Missing (Audit Findings)
| Control Pillar | Status | Gap | Risk |
|---|---|---|---|
| **Risk Assessment** | ❌ None | No threat model | Unknown vulnerabilities |
| **Risk Treatment** | ⚠️ Partial | No input validation, rate limiting | Injection attacks, DoS |
| **Validation** | ❌ None | No integration tests, security tests | Regressions, silent failures |
| **Monitoring** | ❌ None | No logs, metrics, alerts | Blind to issues (mean time to detect: ∞) |
| **Access Control** | ⚠️ Partial | OpenAI key in env vars, no RBAC | Credential compromise risk |
| **Recovery** | ❌ None | No backups, no rollback procedure | Data loss, prolonged outages |
| **Governance** | ❌ None | No runbooks, no audit trail | Uncontrolled operations |

---

## 1. RISK ASSESSMENT (Current Deployment)

### 1.1 Threat Model - RAG System

```
┌─────────────────────────────────────────────────────────┐
│  Internet Users / Clients                              │
│  (Documents uploaded, queries submitted)                │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS
                   ▼
        ┌──────────────────────┐
        │  Frontend (React)    │
        │  rag-system-frontend │
        │  (Render)            │
        └──────────┬───────────┘
                   │ API calls
                   ▼
        ┌──────────────────────────┐
        │  FastAPI Backend         │
        │  rag-system-api (Render) │
        │  - Input validation ⚠️   │
        │  - Rate limiting ❌      │
        │  - Error handling ⚠️     │
        └──────┬──────────────┬────┘
               │              │
               ▼              ▼
        ┌──────────────┐  ┌──────────────┐
        │ ChromaDB     │  │ PostgreSQL   │
        │ (Vector DB)  │  │ (Render)     │
        │ - No auth ❌ │  │ - Encrypted? │
        │ - No backup? │  │ - Backed up? │
        └──────────────┘  └──────────────┘
               │
               ▼
        ┌──────────────────────┐
        │ OpenAI API           │
        │ (text-embedding-*)   │
        │ - Key in env vars ⚠️ │
        │ - Rate limited       │
        └──────────────────────┘

KEY TRUST BOUNDARIES:
  1. Internet → Frontend (HTTPS ✓)
  2. Frontend → API (API auth? ❌)
  3. API → ChromaDB (local, no auth ❌)
  4. API → PostgreSQL (credentials in env vars ⚠️)
  5. API → OpenAI (API key in env vars ⚠️)
```

---

### 1.2 Risks by Component

#### **Frontend (React App)**

| Risk | Severity | Likelihood | Impact | Mitigation Needed |
|------|----------|-----------|--------|------------------|
| XSS in document display | HIGH | Medium | Code injection, session theft | Input sanitization, CSP headers |
| CSRF attacks | MEDIUM | Medium | Unauthorized actions | CSRF tokens |
| Large file upload DoS | MEDIUM | High | Frontend crash | File size limits, chunking |
| Sensitive data in localStorage | HIGH | High | Credential theft | Secure storage, no secrets in client |
| No authentication | CRITICAL | High | Unauthorized access | Add auth (if needed) |

**Current State:** ⚠️ Basic React app, no security headers detected

---

#### **FastAPI Backend**

| Risk | Severity | Likelihood | Impact | Mitigation Needed |
|------|----------|-----------|--------|------------------|
| SQL injection (ChromaDB queries) | HIGH | Medium | Data theft/corruption | Input validation, parameterized queries |
| Prompt injection (LLM attacks) | MEDIUM | High | Model manipulation | Prompt sanitization, instruction guardrails |
| Rate limiting absent | MEDIUM | High | API DoS, cost overrun | Rate limiter per IP/key |
| No input validation | HIGH | High | Invalid data in DB | Request validation layer |
| Unhandled exceptions | MEDIUM | Medium | Information disclosure | Error handling, logging |
| Large request body crash | MEDIUM | High | Memory exhaustion | Body size limits |
| Sensitive data in logs | CRITICAL | High | Credential leakage | Log sanitization |

**Current State:** ⚠️ Error handling present, but no validation/rate limiting

---

#### **Data Storage**

| Risk | Severity | Likelihood | Impact | Mitigation Needed |
|------|----------|-----------|--------|------------------|
| ChromaDB data loss (no backup) | CRITICAL | Medium | Permanent data loss | Automated backups, replication |
| PostgreSQL data loss | CRITICAL | Medium | Complete system failure | Automated backups (Render has? verify) |
| Unauthorized DB access | HIGH | Low | Data theft/corruption | Connection auth, IP whitelist |
| Unencrypted at rest | HIGH | Medium | Data exposure if breached | Encryption at rest (Render provides?) |
| Unencrypted in transit | MEDIUM | Low | Man-in-the-middle | TLS connections (verify) |

**Current State:** ⚠️ PostgreSQL on Render (managed), ChromaDB unprotected

---

#### **External Dependencies (OpenAI)**

| Risk | Severity | Likelihood | Impact | Mitigation Needed |
|------|----------|-----------|--------|------------------|
| API key leaked in code/logs | CRITICAL | Medium | Unauthorized API usage, cost spike | Vault, sanitized logs |
| Rate limit exhaustion | MEDIUM | High | Service degradation | Rate limiting, budget alerts |
| API availability loss | MEDIUM | Low | Embeddings fail, queries fail | Fallback strategy, caching |
| Unexpected API changes | LOW | Low | System breaks | API version pinning, monitoring |

**Current State:** ⚠️ Key in env vars (good), no rate limiting

---

### 1.3 Risk Register

**Create file:** `risk_register_rag_system.xlsx`

| Component | Risk | Severity | Likelihood | Impact | Owner | Status | Target Mitigation |
|-----------|------|----------|-----------|--------|-------|--------|------------------|
| Frontend | XSS in doc display | HIGH | Medium | Code injection | Ram | Not Started | Implement input sanitization |
| Frontend | No auth | CRITICAL | High | Unauthorized access | Ram | Not Started | Add API key auth or OAuth |
| Backend | SQL injection | HIGH | Medium | Data theft | Ram | Not Started | Input validation layer |
| Backend | Prompt injection | MEDIUM | High | LLM manipulation | Ram | Not Started | Prompt sanitization |
| Backend | No rate limiting | MEDIUM | High | API DoS | Ram | Not Started | Rate limiter middleware |
| Backend | Logs leak credentials | CRITICAL | High | Key theft | Ram | Not Started | Sanitization formatter |
| ChromaDB | No backup | CRITICAL | Medium | Data loss | Ram | Not Started | Backup cron job |
| PostgreSQL | No backup verification | HIGH | Medium | Lost recovery ability | Ram | Not Started | Test restore procedure |
| OpenAI | Key exposed | CRITICAL | Medium | Cost spike | Ram | Not Started | Vault + key rotation |

---

## 2. RISK TREATMENT (Recommended Fixes)

### 2.1 Input Validation Layer

**File:** `app/validators/rag_validator.py`

```python
from typing import List, Dict
import re

class RAGInputValidator:
    """
    Validates inputs to RAG system.
    Prevents injection attacks and invalid data.
    """
    
    # Maximum sizes to prevent DoS
    MAX_QUERY_LENGTH = 5000        # characters
    MAX_DOCUMENT_SIZE = 10_000_000  # 10MB
    MAX_BATCH_SIZE = 100           # docs per upload
    
    @staticmethod
    def validate_query(query: str) -> bool:
        """Validate user search query"""
        if not query or len(query) > RAGInputValidator.MAX_QUERY_LENGTH:
            raise ValueError(f"Query too long: {len(query)} chars (max {RAGInputValidator.MAX_QUERY_LENGTH})")
        
        # Allow alphanumeric + common punctuation
        if not re.match(r'^[a-zA-Z0-9\s\.,!?\-\(\)]+$', query):
            raise ValueError("Query contains invalid characters")
        
        return True
    
    @staticmethod
    def validate_document(doc_content: str, filename: str) -> bool:
        """Validate uploaded document"""
        if len(doc_content) > RAGInputValidator.MAX_DOCUMENT_SIZE:
            raise ValueError(f"Document too large: {len(doc_content)} bytes")
        
        # Whitelist file types
        allowed_extensions = ['.txt', '.pdf', '.md', '.docx']
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File type not allowed: {filename}")
        
        return True
    
    @staticmethod
    def validate_embedding_params(top_k: int = 10) -> bool:
        """Validate retrieval parameters"""
        if not 1 <= top_k <= 100:
            raise ValueError(f"Invalid top_k: {top_k} (must be 1-100)")
        
        return True
```

---

### 2.2 Rate Limiting Middleware

**File:** `app/middleware/rate_limiter.py`

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Rate limit policies
RATE_LIMITS = {
    "/query": "10/minute",        # Search queries
    "/upload": "5/minute",         # Document uploads
    "/health": "1000/minute",      # Health checks (less critical)
}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get route
        route = request.url.path
        
        # Apply rate limit
        limit = RATE_LIMITS.get(route, "100/minute")
        
        # Check rate limit
        # ... implementation ...
        
        return await call_next(request)
```

---

### 2.3 Credential Management

**Current:** OpenAI key in env vars (risky)

**Improved:** Use Render's built-in secrets

```bash
# Render dashboard → Settings → Environment
# Add secrets (not exposed in code):
OPENAI_API_KEY=sk-...
POSTGRES_URL=postgresql://...
CHROMADB_PATH=/tmp/chroma_data
```

**Better:** Use Render's native PostgreSQL + managed backups

```python
# app/config.py
import os
from typing import Optional

class Settings:
    # Secrets from Render environment
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL")
    
    # Feature flags
    ENABLE_AUTH: bool = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # Limits
    MAX_QUERY_LENGTH: int = 5000
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # Verify secrets are set
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set")
        if not cls.POSTGRES_URL:
            raise RuntimeError("POSTGRES_URL not set")

settings = Settings()
settings.validate()
```

---

### 2.4 Log Sanitization

**File:** `app/logging/sanitizer.py`

```python
import logging
import re

class CredentialSanitizer(logging.Filter):
    """Remove secrets from logs"""
    
    PATTERNS = [
        (r'(api_key|apikey)["\']?\s*[:=]\s*["\']?([^"\';\s]+)', r'\1=REDACTED'),
        (r'Bearer\s+[A-Za-z0-9._\-]+', 'Bearer REDACTED'),
        (r'sk[-_][a-zA-Z0-9]+', 'sk-REDACTED'),
        (r'postgresql://[^@]+@', 'postgresql://USER:PASS@'),
    ]
    
    def filter(self, record):
        record.msg = str(record.msg)
        for pattern, replacement in self.PATTERNS:
            record.msg = re.sub(pattern, replacement, record.msg, flags=re.IGNORECASE)
        return True

# Add filter to logger
logger = logging.getLogger("rag_system")
logger.addFilter(CredentialSanitizer())
```

---

## 3. VALIDATION (Testing Existing System)

### 3.1 Current State Testing

**Run these tests immediately (add to CI/CD):**

```bash
# Test 1: API responds
curl https://rag-system-api-s09i.onrender.com/health
# Expected: {"status": "healthy"}

# Test 2: Embeddings work
curl -X POST https://rag-system-api-s09i.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
# Expected: 200 with results

# Test 3: Large payload rejected
curl -X POST https://rag-system-api-s09i.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "'"$(python -c 'print("a" * 100000)')"'"}'
# Expected: 413 Payload Too Large (after we add validation)

# Test 4: Rate limiting works (after implementation)
for i in {1..20}; do
  curl https://rag-system-api-s09i.onrender.com/query \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}'
done
# Expected: After 10 requests → 429 Too Many Requests
```

---

### 3.2 Integration Tests (Write New)

**File:** `tests/test_rag_system.py`

```python
import pytest
from app.validators import RAGInputValidator

class TestRAGValidation:
    """Test input validation"""
    
    def test_query_too_long_rejected(self):
        """Queries >5000 chars must fail"""
        long_query = "a" * 10000
        with pytest.raises(ValueError, match="too long"):
            RAGInputValidator.validate_query(long_query)
    
    def test_invalid_characters_rejected(self):
        """Queries with special chars must fail"""
        invalid = "query with <script> tag"
        with pytest.raises(ValueError, match="invalid characters"):
            RAGInputValidator.validate_query(invalid)
    
    def test_valid_query_accepted(self):
        """Normal queries must pass"""
        assert RAGInputValidator.validate_query("What is machine learning?")

class TestEmbeddingsIntegration:
    """Test OpenAI integration"""
    
    def test_embedding_api_responsive(self):
        """OpenAI embeddings must work"""
        # Make actual API call (costs $)
        from app.embeddings import get_embedding
        result = get_embedding("test query")
        assert result is not None
        assert len(result) > 0
    
    def test_retrieval_latency(self):
        """Query must complete in <5 seconds"""
        import time
        start = time.time()
        # Make query...
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Query too slow: {elapsed}s"
```

---

### 3.3 Security Tests

**File:** `tests/test_security.py`

```python
import pytest

class TestInjectionPrevention:
    """Test injection attack prevention"""
    
    def test_sql_injection_blocked(self):
        """SQL injection attempts must fail"""
        payloads = [
            'test"; DROP TABLE embeddings; --',
            "test' OR '1'='1",
            'test\"; UNION SELECT * FROM users; --',
        ]
        
        from app.validators import RAGInputValidator
        for payload in payloads:
            with pytest.raises(ValueError):
                RAGInputValidator.validate_query(payload)
    
    def test_no_credentials_in_logs(self):
        """Logs must never contain API keys"""
        import logging
        from app.logging.sanitizer import CredentialSanitizer
        
        # Create test logger
        logger = logging.getLogger("test")
        logger.addFilter(CredentialSanitizer())
        
        # Try to log credential
        with patch('logging.Logger.info') as mock:
            logger.info("API key = sk-1234567890")
            # Verify redaction happened
            assert "sk-1234567890" not in str(mock.call_args)
            assert "REDACTED" in str(mock.call_args)

class TestRateLimiting:
    """Test rate limiter"""
    
    def test_rate_limit_enforced(self):
        """Requests >10/min must be rejected"""
        from app.middleware.rate_limiter import limiter
        
        # Simulate 15 requests
        for i in range(15):
            response = client.get("/query?q=test")
            if i < 10:
                assert response.status_code == 200
            else:
                assert response.status_code == 429  # Too Many Requests
```

---

## 4. MONITORING (Critical Gaps)

Your system is **operating blind**. Add observability immediately.

### 4.1 Application Logging

**File:** `app/logging/config.py`

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Output logs as JSON for easy parsing"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'path': record.pathname,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure logging
def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler (Render captures stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # Log important events
    logger = logging.getLogger("rag_system")
    
    logger.info("RAG System starting", extra={
        'version': '1.5',
        'deployment': 'render',
    })

# In main.py
from app.logging.config import setup_logging
setup_logging()
```

---

### 4.2 Prometheus Metrics

**Add to FastAPI:**

```python
from prometheus_client import Counter, Histogram, Gauge
from fastapi import FastAPI
from prometheus_client.exposition import generate_latest

app = FastAPI()

# Define metrics
query_count = Counter(
    'rag_queries_total',
    'Total queries processed',
    labelnames=['status']
)

query_latency = Histogram(
    'rag_query_latency_seconds',
    'Query latency',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

embedding_cost = Counter(
    'openai_embedding_cost_usd_total',
    'Total OpenAI API cost'
)

chromadb_documents = Gauge(
    'chromadb_documents_total',
    'Total documents in ChromaDB'
)

# Expose metrics endpoint
@app.get("/metrics")
def metrics():
    return generate_latest()

# Instrument query endpoint
@app.post("/query")
async def query(q: str):
    import time
    start = time.time()
    
    try:
        # Your query logic...
        results = perform_query(q)
        query_count.labels(status='success').inc()
        elapsed = time.time() - start
        query_latency.observe(elapsed)
        return results
    except Exception as e:
        query_count.labels(status='error').inc()
        raise
```

---

### 4.3 Health Checks & Alerts

**File:** `app/health.py`

```python
from typing import Dict, Any
import requests

async def check_health() -> Dict[str, Any]:
    """
    Comprehensive health check.
    Returns status of all critical components.
    """
    health = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }
    
    # 1. Check OpenAI API
    try:
        response = requests.post(
            'https://api.openai.com/v1/embeddings',
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
            json={'model': 'text-embedding-3-small', 'input': 'test'}
        )
        health['components']['openai_api'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except Exception as e:
        health['components']['openai_api'] = f'error: {str(e)}'
        health['status'] = 'degraded'
    
    # 2. Check PostgreSQL
    try:
        from app.db import SessionLocal
        session = SessionLocal()
        session.execute("SELECT 1")
        health['components']['postgresql'] = 'healthy'
    except Exception as e:
        health['components']['postgresql'] = f'error: {str(e)}'
        health['status'] = 'degraded'
    
    # 3. Check ChromaDB
    try:
        from app.rag import chroma_client
        collection = chroma_client.get_or_create_collection("documents")
        count = collection.count()
        health['components']['chromadb'] = {
            'status': 'healthy',
            'documents': count
        }
    except Exception as e:
        health['components']['chromadb'] = f'error: {str(e)}'
        health['status'] = 'degraded'
    
    return health

@app.get("/health")
async def health_endpoint():
    return await check_health()
```

**Add to Render monitoring:**

```bash
# In Render dashboard → Health Checks
Endpoint: /health
Port: 8000
Path: /health
Check interval: 30 seconds
```

---

## 5. ACCESS CONTROL & CREDENTIALS

### 5.1 Current State

```
⚠️ SECURITY ISSUE: OpenAI API key in environment variables
✓ GOOD: PostgreSQL managed by Render (encrypted)
⚠️ ISSUE: ChromaDB unprotected (no auth)
⚠️ ISSUE: Frontend has no auth (anyone can access)
```

### 5.2 Recommended Changes

**Option A: Quick Fix (1 hour)**
```bash
# Render dashboard → Settings → Environment
# Remove: OPENAI_API_KEY (from git)
# Add:    OPENAI_API_KEY (Render secret)
# Result: Key not in code, managed by Render
```

**Option B: Better Security (2 hours)**
```bash
# Deploy HashiCorp Vault on Render
# Move all secrets there
# Rotate keys automatically (90-day policy)
```

**Option C: Enterprise (4 hours)**
```bash
# Migrate to AWS Secrets Manager
# Add IAM roles for API access
# Implement audit logging
```

---

### 5.3 Add Basic Authentication (If Needed)

```python
from fastapi import FastAPI, Header, HTTPException
from typing import Optional

app = FastAPI()

VALID_API_KEYS = {
    "demo-key-123": "Demo User",
    "prod-key-456": "Production User",
}

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key on protected endpoints"""
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/query")
async def query(q: str, api_key: str = Depends(verify_api_key)):
    """Query endpoint (requires API key)"""
    # Now only valid keys can query
    # ...
```

---

## 6. RECOVERY & DISASTER RECOVERY

### 6.1 Current State

```
⚠️ NO BACKUPS
⚠️ NO RECOVERY PROCEDURE
⚠️ NO ROLLBACK CAPABILITY
```

**What happens if:**
- ChromaDB corrupts? → **Data permanently lost**
- PostgreSQL fails? → **Complete system outage**
- OpenAI API is down? → **All embeddings fail**
- Code bug deployed? → **Manual rollback only**

---

### 6.2 Backup Strategy

**ChromaDB Backup (add cron job):**

```bash
#!/bin/bash
# scripts/backup_chromadb.sh
# Run every 6 hours

BACKUP_DIR="/tmp/chromadb_backups"
mkdir -p $BACKUP_DIR

# Copy entire ChromaDB directory
cp -r /path/to/chromadb $BACKUP_DIR/chromadb_$(date +%s)

# Keep only last 7 days
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;

# Upload to S3 (or Render's object storage)
aws s3 sync $BACKUP_DIR s3://rag-system-backups/chromadb/
```

**PostgreSQL Backup (Render handles automatically!):**

```
Render ✓ Provides:
  - Automatic daily backups
  - Point-in-time restore
  - 30-day retention
  - One-click restore

You need to:
  - Verify backup is working
  - Test restore procedure
  - Document restore steps
```

**Test restore:**

```bash
# Monthly: Restore backup to test environment
# 1. Render dashboard → Database → Backups
# 2. Create restore
# 3. Verify data intact
# 4. Delete test instance
# 5. Document in runbook
```

---

### 6.3 Disaster Recovery Runbook

**File:** `runbooks/DISASTER_RECOVERY.md`

```markdown
# Disaster Recovery Runbook

## Scenario 1: Embeddings API Rate Limited (OpenAI Down)

**Detection:**
- `/query` endpoint returns 429 Too Many Requests
- Prometheus metric: `openai_embedding_cost_usd_total` stopped incrementing

**Immediate Action (0-5 min):**
1. Check OpenAI status: https://status.openai.com
2. If down: Return cached results to users
3. If rate-limited: Implement exponential backoff

**Recovery (5-30 min):**
```python
# Implement fallback: use cached embeddings
@app.post("/query")
async def query(q: str):
    try:
        results = new_embedding_query(q)  # Fresh embedding
    except OpenAIRateLimitError:
        results = cached_embedding_query(q)  # Fallback to cache
    return results
```

## Scenario 2: PostgreSQL Database Corrupted

**Detection:**
- `/health` endpoint shows PostgreSQL: unhealthy
- Database connection errors in logs

**Immediate Action (0-10 min):**
1. Stop API (prevent further corruption):
   ```bash
   curl -X PATCH https://api.render.com/v1/services/YOUR-SERVICE-ID \
     -H "Authorization: Bearer $RENDER_API_TOKEN" \
     -d '{"suspended": true}'
   ```

2. Assess damage:
   ```sql
   SELECT COUNT(*) FROM pg_tables;
   ```

**Recovery (10-60 min):**
1. Render Dashboard → Database → Backups
2. Click "Restore" → Choose backup from last 24 hours
3. Wait for restore to complete
4. Test: `SELECT COUNT(*) FROM documents;`
5. Resume API:
   ```bash
   curl -X PATCH https://api.render.com/v1/services/YOUR-SERVICE-ID \
     -H "Authorization: Bearer $RENDER_API_TOKEN" \
     -d '{"suspended": false}'
   ```

## Scenario 3: Deployment Breaks Everything

**Detection:**
- Health checks failing
- Error rate >50%
- Users reporting failures

**Immediate Action (0-5 min):**
```bash
# Render dashboard → Deploy → Rollback
# OR from CLI:
git log --oneline -5  # Find last good commit
git revert HEAD
git push  # Auto-deploys on Render
```

**Root Cause Analysis (30 min):**
1. Check deploy logs:
   ```bash
   # Render dashboard → Logs → Deploy logs
   ```
2. Check runtime logs:
   ```bash
   # Render dashboard → Logs → Runtime logs
   ```
3. Fix in code, redeploy

## Scenario 4: ChromaDB Data Lost

**Detection:**
- ChromaDB returns "collection not found"
- Document count drops to 0
- Queries return empty results

**Recovery (Immediate):**
1. Check backup timestamp:
   ```bash
   ls -lh /tmp/chromadb_backups/
   ```

2. Restore latest backup:
   ```bash
   rm -rf /path/to/chromadb
   cp -r /tmp/chromadb_backups/chromadb_LATEST /path/to/chromadb
   ```

3. Restart FastAPI service (auto on Render)

4. Verify:
   ```bash
   curl https://rag-system-api/health
   ```

**Prevent Future Loss:**
- Add daily backup verification
- Store backups in S3 (off-system)
- Test restore monthly
```

---

## 7. GOVERNANCE & COMPLIANCE

### 7.1 Data Retention Policy

**Create:** `COMPLIANCE.md`

```markdown
# Data Retention & Privacy Policy

## What Data We Collect
- User queries (text)
- Uploaded documents (full content)
- Embeddings (vector representations)
- API logs (queries, timestamps)

## Where It's Stored
- PostgreSQL (Render, US East)
- ChromaDB (Render, embedded)
- Render logs (30-day retention)

## Retention Period
- Documents: Keep indefinitely (unless user deletes)
- Query logs: 90 days (then purge)
- Embeddings: Delete with document

## User Rights
- User can request document deletion
- User can request query history deletion
- User can request data export (GDPR/CCPA)

## Compliance
- GDPR: Right to be forgotten (delete endpoint needed)
- CCPA: Privacy notice (add to frontend)
- SOC 2: Audit trails (add logging)

## Implementation
- Add DELETE /documents/{id} endpoint
- Add GET /user/data endpoint (export)
- Add audit log for all deletions
```

---

### 7.2 Audit Logging

**File:** `app/audit/audit_log.py`

```python
from sqlalchemy import Column, String, DateTime, JSON
from app.db import Base
from datetime import datetime

class AuditLog(Base):
    """Record all user actions for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_ip = Column(String)
    action = Column(String)  # query, upload, delete
    resource = Column(String)  # document ID, query ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)

@app.post("/query")
async def query(q: str, request: Request):
    # Log query
    audit_log = AuditLog(
        user_ip=request.client.host,
        action='query',
        resource='search',
        details={'query_length': len(q)}
    )
    db.add(audit_log)
    db.commit()
    
    # Process query...
```

---

## 8. 30-DAY HARDENING ROADMAP

### Week 1: Monitoring & Observability
- [ ] Day 1: Setup logging (JSON structured logs)
- [ ] Day 2: Add Prometheus metrics
- [ ] Day 3: Configure Render health checks
- [ ] Day 4: Setup alerts (Slack/email)
- [ ] Day 5: Create monitoring dashboard
- [ ] Day 6-7: Baseline metrics (know normal behavior)

**Deliverables:**
- Render logs showing structured JSON output
- `/metrics` endpoint returning Prometheus metrics
- Health check pinging every 30 sec
- Alert sent to Slack on /health failure

---

### Week 2: Input Validation & Rate Limiting
- [ ] Day 8: Implement input validators
- [ ] Day 9: Add rate limiting middleware
- [ ] Day 10: Add max request size limits
- [ ] Day 11: Test injection attacks
- [ ] Day 12: Add authentication (API keys)
- [ ] Day 13-14: Load test with rate limiting

**Deliverables:**
- `/query` rejects queries >5000 chars
- Rate limiter returns 429 after 10 req/min
- Large uploads rejected with 413
- All tests passing

---

### Week 3: Disaster Recovery & Backups
- [ ] Day 15: Setup ChromaDB backup cron
- [ ] Day 16: Verify PostgreSQL backups (Render)
- [ ] Day 17: Write disaster recovery runbook
- [ ] Day 18: Test ChromaDB restore
- [ ] Day 19: Test PostgreSQL restore
- [ ] Day 20: Setup S3 offsite backups
- [ ] Day 21: Monthly disaster recovery drill

**Deliverables:**
- Cronjob backing up ChromaDB every 6 hours
- DR runbook with step-by-step procedures
- Successful restore test documented
- S3 backups 7 days old, clean

---

### Week 4: Security Hardening & Compliance
- [ ] Day 22: Implement credential sanitization in logs
- [ ] Day 23: Add audit logging
- [ ] Day 24: Move OpenAI key to Render secrets (not git)
- [ ] Day 25: Add data retention policy
- [ ] Day 26: Implement DELETE document endpoint
- [ ] Day 27-28: Security audit (pen test?)
- [ ] Day 29-30: Get sign-offs from stakeholders

**Deliverables:**
- Logs never contain API keys
- Audit logs for all user actions
- OpenAI key not in Git history
- COMPLIANCE.md document
- Team sign-off on readiness

---

## 9. IMPLEMENTATION PRIORITY MATRIX

```
PRIORITY = IMPACT × URGENCY

HIGH PRIORITY (Do First)
  ✓ Logging (observe what's happening)
  ✓ Rate limiting (prevent DoS)
  ✓ Input validation (prevent injection)
  ✓ Credential management (security)

MEDIUM PRIORITY (Do Next)
  ✓ Health checks (uptime visibility)
  ✓ Backups (disaster recovery)
  ✓ Authentication (access control)

LOWER PRIORITY (Do Later)
  ✓ Audit logging (compliance)
  ✓ Load testing (scalability)
  ✓ Penetration testing (security)
```

---

## 10. SUCCESS CRITERIA (30-Day Target)

### ✅ Monitoring
- [ ] Logs are structured (JSON format)
- [ ] Metrics exposed at `/metrics` endpoint
- [ ] Health check responsive (<5 sec)
- [ ] Alerts configured (Slack integration working)
- [ ] Dashboard shows live metrics

### ✅ Security
- [ ] Input validation prevents injection attacks
- [ ] Rate limiter enforced (10 req/min)
- [ ] Credentials never in logs (verified)
- [ ] API key in Render secrets (not git)
- [ ] Security tests passing (100%)

### ✅ Reliability
- [ ] ChromaDB backups running (every 6 hours)
- [ ] PostgreSQL backups verified (Render automatic)
- [ ] Disaster recovery runbook complete
- [ ] Restore procedure tested monthly
- [ ] Rollback procedure works (<5 min)

### ✅ Compliance
- [ ] Audit logs recording all user actions
- [ ] Data retention policy documented
- [ ] User can delete their documents
- [ ] User can export their data
- [ ] Team trained on incident response

---

## 11. SIGN-OFF CHECKLIST

**To certify system is production-hardened:**

- [ ] **Engineering Lead**: Code quality reviewed
  - Signature: _________________ Date: _____
  
- [ ] **Security Lead**: Security audit passed
  - Signature: _________________ Date: _____
  
- [ ] **DevOps Lead**: Monitoring & backups verified
  - Signature: _________________ Date: _____
  
- [ ] **Product Lead**: Feature-complete, user-ready
  - Signature: _________________ Date: _____

**System Status:** ☐ Ready for Continued Production Use

---

## 12. ONGOING MAINTENANCE (Monthly)

**Every Month:**
- [ ] Review logs for errors
- [ ] Check backup integrity
- [ ] Test disaster recovery procedure
- [ ] Update monitoring thresholds
- [ ] Review security alerts

**Quarterly:**
- [ ] Penetration test (if budget)
- [ ] Load test (simulate peak usage)
- [ ] Database optimization
- [ ] Dependency updates

**Annually:**
- [ ] SOC 2 audit (if required)
- [ ] Full security review
- [ ] Capacity planning
- [ ] Technology refresh decision

---

**Document Owner:** qualigenai (Ram)  
**Last Updated:** May 15, 2026  
**Next Review:** May 30, 2026  
**Status:** DRAFT → Awaiting Sign-Offs
