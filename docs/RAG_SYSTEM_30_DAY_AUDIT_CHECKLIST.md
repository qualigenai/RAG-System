# 30-Day Post-Deployment Audit Checklist
## Enterprise RAG System v1.5

**Deployment Date:** May 2026  
**Audit Start Date:** May 15, 2026  
**Target Completion:** June 14, 2026  
**Owner:** qualigenai (Ram)  

---

## 📋 OVERVIEW

Your RAG System is deployed but operates blind. This checklist guides you through adding **observability, security, and reliability** without downtime.

All changes can be **deployed incrementally** (no big-bang rewrite).

---

## 🔍 WEEK 1: AUDIT & MONITORING SETUP (May 15-21)

### Day 1: Current State Assessment (2 hours)

**Morning (30 min):**
- [ ] Check endpoint availability:
  ```bash
  curl -v https://rag-system-api-s09i.onrender.com/health
  curl -v https://rag-system-frontend-53uy.onrender.com/
  ```

- [ ] Check Render logs:
  ```bash
  # Render dashboard → Services → rag-system-api → Logs
  # Screenshot last 100 lines
  # Save to: logs/baseline_May15_2026.txt
  ```

- [ ] Document response times:
  ```bash
  for i in {1..10}; do
    time curl -X POST \
      https://rag-system-api-s09i.onrender.com/query \
      -H "Content-Type: application/json" \
      -d '{"query": "test query"}'
  done
  # Average time: _____ sec
  ```

**Afternoon (1.5 hours):**
- [ ] Check database connectivity:
  ```bash
  # From Render dashboard → PostgreSQL → Connections
  # Current connections: ___
  # Max connections: ___
  ```

- [ ] Verify ChromaDB status:
  ```python
  # SSH to Render
  # python -c "
  # from app.rag import chroma_client
  # collection = chroma_client.get_or_create_collection('documents')
  # print(f'Documents in ChromaDB: {collection.count()}')
  # "
  ```

- [ ] Create risk register:
  ```bash
  cp risk_register_template.xlsx risk_register_rag_system.xlsx
  # Fill in findings from above
  ```

**Deliverable:** `CURRENT_STATE_REPORT.md` (document all findings)

---

### Day 2: Structured Logging Setup (3 hours)

**Goal:** All logs as JSON for easy parsing

**Task 1: Update logging config (1 hour)**
- [ ] Create `app/logging/config.py`:
  ```bash
  # See PRODUCTION_CODE_SNIPPETS.md for full code
  # Copy → app/logging/config.py
  ```

- [ ] Update `main.py` to call setup:
  ```python
  from app.logging.config import setup_logging
  
  if __name__ == "__main__":
      setup_logging()
      uvicorn.run(app, host="0.0.0.0", port=8000)
  ```

- [ ] Test locally:
  ```bash
  python -m app.main 2>&1 | head -20
  # Should see JSON logs, not plain text
  ```

**Task 2: Sanitize credentials from logs (1 hour)**
- [ ] Create `app/logging/sanitizer.py` (from code snippets)

- [ ] Add filter to logger config:
  ```python
  logger.addFilter(CredentialSanitizer())
  ```

- [ ] Test sanitization:
  ```bash
  python -c "
  from app.logging.sanitizer import CredentialSanitizer
  msg = 'Error: API key sk-1234567890 failed'
  clean = CredentialSanitizer.sanitize(msg)
  print(f'Original: {msg}')
  print(f'Sanitized: {clean}')
  assert 'sk-1234567890' not in clean
  print('✓ Sanitization works')
  "
  ```

**Task 3: Deploy to staging (1 hour)**
- [ ] Commit changes:
  ```bash
  git add app/logging/
  git commit -m "feat: add structured JSON logging with credential sanitization"
  ```

- [ ] Deploy to staging (if available):
  ```bash
  # Create staging branch
  git checkout -b feature/structured-logging
  # Push to trigger Render deploy
  git push -u origin feature/structured-logging
  ```

- [ ] Verify in Render logs:
  ```bash
  # Render dashboard → Logs
  # Should see JSON output (not plain text)
  ```

**Deliverable:** JSON logs flowing through Render

---

### Day 3: Prometheus Metrics (3 hours)

**Goal:** Export metrics for monitoring

**Task 1: Add metrics to FastAPI (1.5 hours)**
- [ ] Create `app/monitoring/metrics.py` (from code snippets)

- [ ] Add to `main.py`:
  ```python
  from app.monitoring.metrics import (
      query_count, query_latency, embedding_cost
  )
  
  @app.post("/query")
  async def query(q: str):
      import time
      start = time.time()
      
      try:
          results = perform_query(q)
          query_count.labels(status='success').inc()
          elapsed = time.time() - start
          query_latency.observe(elapsed)
          return results
      except Exception as e:
          query_count.labels(status='error').inc()
          raise
  ```

- [ ] Add metrics endpoint:
  ```python
  from prometheus_client import generate_latest
  
  @app.get("/metrics")
  def metrics():
      return generate_latest()
  ```

**Task 2: Test metrics endpoint (1 hour)**
- [ ] Deploy to staging
- [ ] Make some queries:
  ```bash
  # Make 5 requests
  for i in {1..5}; do
    curl -X POST https://rag-system-api-staging/query \
      -H "Content-Type: application/json" \
      -d '{"query": "test"}'
  done
  ```

- [ ] Check metrics:
  ```bash
  curl https://rag-system-api-staging/metrics | grep rag_queries_total
  # Should show: rag_queries_total{status="success"} 5.0
  ```

**Task 3: Setup Prometheus (0.5 hours)**
- [ ] Create `monitoring/prometheus.yml`:
  ```yaml
  global:
    scrape_interval: 30s
  
  scrape_configs:
    - job_name: 'rag-system'
      static_configs:
        - targets: ['rag-system-api-s09i.onrender.com']
      metrics_path: '/metrics'
  ```

- [ ] Run Prometheus locally (for testing):
  ```bash
  docker run -d -p 9090:9090 \
    -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus
  
  # Open http://localhost:9090
  # Search for: rag_queries_total
  ```

**Deliverable:** `/metrics` endpoint active, metrics flowing

---

### Day 4: Health Checks & Alerting (3 hours)

**Goal:** Detect outages before users notice

**Task 1: Implement comprehensive health check (1.5 hours)**
- [ ] Create `app/health.py` (from audit plan)

- [ ] Add to `main.py`:
  ```python
  from app.health import check_health
  
  @app.get("/health")
  async def health():
      return await check_health()
  ```

- [ ] Test endpoint:
  ```bash
  curl https://rag-system-api-s09i.onrender.com/health | jq .
  # Should show all components: openai_api, postgresql, chromadb
  ```

**Task 2: Configure Render health checks (1 hour)**
- [ ] Render dashboard → Settings → Health Check
  - Endpoint: `/health`
  - Port: 8000
  - Path: `/health`
  - Check interval: 30 seconds
  - Timeout: 5 seconds

- [ ] Save and verify:
  ```bash
  # Wait 2 minutes for first check
  # Render dashboard should show "Healthy" status
  ```

**Task 3: Setup Slack alerts (0.5 hours)**
- [ ] Create Slack webhook:
  ```bash
  # Slack workspace → Integrations → Incoming Webhooks
  # Create webhook URL: https://hooks.slack.com/services/T.../B.../X...
  # Save to: config/.env.local (never commit)
  ```

- [ ] Add alert function:
  ```python
  import requests
  
  def alert_slack(message: str):
      webhook_url = os.getenv("SLACK_WEBHOOK_URL")
      requests.post(webhook_url, json={"text": message})
  
  # Use in health check:
  if health['status'] == 'degraded':
      alert_slack(f"⚠️ RAG System degraded: {health}")
  ```

**Deliverable:** Health check returns component status, Slack alerts work

---

### Day 5: Create Monitoring Dashboard (2 hours)

**Goal:** Single pane of glass for observability

**Task 1: Setup Grafana locally (0.5 hours)**
- [ ] Run Grafana:
  ```bash
  docker run -d -p 3000:3000 grafana/grafana:latest
  # Login: admin/admin (change password!)
  ```

- [ ] Add Prometheus datasource:
  - Data source → Prometheus
  - URL: http://localhost:9090
  - Save & test

**Task 2: Create dashboard (1 hour)**
- [ ] Create dashboard: "RAG System Production"

- [ ] Add panels:
  - **Query Success Rate** (line chart)
    - Query: `rate(rag_queries_total{status="success"}[5m])`
  
  - **Query Latency (p95)** (line chart)
    - Query: `histogram_quantile(0.95, rag_query_latency_seconds)`
  
  - **OpenAI API Cost** (gauge)
    - Query: `rate(openai_embedding_cost_usd_total[1h])`
  
  - **ChromaDB Documents** (gauge)
    - Query: `chromadb_documents_total`
  
  - **Health Status** (stat)
    - Manual JSON query to `/health` endpoint

**Task 3: Export and version (0.5 hours)**
- [ ] Export dashboard JSON:
  ```bash
  # Grafana → Dashboard → Share → Export JSON
  # Save to: monitoring/dashboard_rag_production.json
  git add monitoring/dashboard_rag_production.json
  git commit -m "docs: add RAG system production dashboard"
  ```

**Deliverable:** Grafana dashboard showing live metrics

---

### Day 6: Baseline Metrics & Alerting Rules (2 hours)

**Goal:** Know what "normal" looks like

**Task 1: Run baseline test (1 hour)**
- [ ] Run 100 queries over 2 hours:
  ```bash
  for i in {1..100}; do
    curl -X POST https://rag-system-api-s09i.onrender.com/query \
      -H "Content-Type: application/json" \
      -d '{"query": "test query '$i'"}'
    sleep 72  # 100 queries over 2 hours = one every 72 sec
  done
  ```

- [ ] Record metrics in spreadsheet:
  ```
  Metric | Min | Max | Mean | P95
  Query Latency | __ms | __ms | __ms | __ms
  Success Rate | __% | __% | __% | __%
  Error Count | __ | __ | __ | __
  ```

**Task 2: Create alert rules (1 hour)**
- [ ] Create `monitoring/alert_rules.yml`:
  ```yaml
  groups:
    - name: rag_system
      interval: 30s
      rules:
        # Alert if >5% errors
        - alert: HighErrorRate
          expr: |
            rate(rag_queries_total{status="error"}[5m]) /
            rate(rag_queries_total[5m]) > 0.05
          for: 5m
          annotations:
            summary: "High error rate detected"
            description: "Error rate > 5% for 5 minutes"
        
        # Alert if latency > 5 seconds (p95)
        - alert: SlowQueries
          expr: histogram_quantile(0.95, rag_query_latency_seconds) > 5
          for: 5m
          annotations:
            summary: "High query latency"
            description: "p95 latency > 5 seconds"
        
        # Alert if health check fails
        - alert: HealthCheckFailed
          expr: up{job="rag-system"} == 0
          for: 1m
          annotations:
            summary: "RAG system health check failing"
  ```

- [ ] Configure AlertManager to send to Slack (or PagerDuty)

**Deliverable:** Baseline metrics documented, alert rules configured

---

### Day 7: Week 1 Sign-Off (1 hour)

**Checklist:**
- [ ] JSON structured logs flowing
- [ ] `/metrics` endpoint active
- [ ] `/health` endpoint operational
- [ ] Prometheus scraping metrics every 30 sec
- [ ] Grafana dashboard displaying live data
- [ ] Slack alerts configured (test alert sent)
- [ ] Baseline metrics recorded

**Commit & push:**
```bash
git add app/logging app/monitoring app/health monitoring/
git commit -m "feat(monitoring): add structured logging, metrics, health checks"
git push origin main  # Triggers Render deploy
```

**Deliverable:** Production visibility achieved

---

## 🔒 WEEK 2: SECURITY HARDENING (May 22-28)

### Day 8: Input Validation (3 hours)

**Goal:** Prevent injection attacks

**Task 1: Create validators (1.5 hours)**
- [ ] Create `app/validators/rag_validator.py` (from code snippets)

- [ ] Add to FastAPI routes:
  ```python
  from app.validators import RAGInputValidator
  
  @app.post("/query")
  async def query(q: str):
      # Validate input
      RAGInputValidator.validate_query(q)
      
      # Safe to process
      results = perform_query(q)
      return results
  
  @app.post("/upload")
  async def upload(file: UploadFile):
      content = await file.read()
      
      # Validate
      RAGInputValidator.validate_document(content, file.filename)
      
      # Safe to store
      store_document(content, file.filename)
      return {"status": "uploaded"}
  ```

**Task 2: Write validation tests (1 hour)**
- [ ] Create `tests/test_validation.py`:
  ```python
  import pytest
  from app.validators import RAGInputValidator
  
  def test_query_too_long_rejected():
      long_query = "a" * 10000
      with pytest.raises(ValueError, match="too long"):
          RAGInputValidator.validate_query(long_query)
  
  def test_invalid_chars_rejected():
      bad = "query with <script> tag"
      with pytest.raises(ValueError, match="invalid"):
          RAGInputValidator.validate_query(bad)
  
  def test_valid_query_accepted():
      assert RAGInputValidator.validate_query("What is AI?")
  
  def test_file_type_validation():
      with pytest.raises(ValueError):
          RAGInputValidator.validate_document(b"content", "malware.exe")
  ```

- [ ] Run tests:
  ```bash
  pytest tests/test_validation.py -v
  # Expected: All tests pass
  ```

**Task 3: Integration test injection attacks (0.5 hours)**
- [ ] Test with curl:
  ```bash
  # Test 1: Long query
  curl -X POST https://rag-system-api/query \
    -d "{\"query\": \"$(python -c 'print("a"*10000)')\"}"
  # Expected: 400 Bad Request
  
  # Test 2: Invalid chars
  curl -X POST https://rag-system-api/query \
    -d '{"query": "test <script>alert(1)</script>"}'
  # Expected: 400 Bad Request
  
  # Test 3: Normal query
  curl -X POST https://rag-system-api/query \
    -d '{"query": "What is machine learning?"}'
  # Expected: 200 OK with results
  ```

**Deliverable:** Input validation implemented, tests passing

---

### Day 9: Rate Limiting (2 hours)

**Goal:** Prevent DoS attacks and cost overruns

**Task 1: Add rate limiter middleware (1 hour)**
- [ ] Create `app/middleware/rate_limiter.py`:
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  
  RATE_LIMITS = {
      "/query": "10/minute",
      "/upload": "5/minute",
      "/health": "1000/minute",
  }
  ```

- [ ] Add to FastAPI:
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  from app.middleware.rate_limiter import RATE_LIMITS
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  
  @app.post("/query")
  @limiter.limit("10/minute")
  async def query(request: Request, q: str):
      # Process query
  ```

**Task 2: Test rate limiting (1 hour)**
- [ ] Deploy to staging
  
- [ ] Hammer endpoint:
  ```bash
  for i in {1..20}; do
    RESP=$(curl -s -w "\n%{http_code}" -X POST \
      https://rag-system-api-staging/query \
      -d '{"query": "test"}')
    CODE=$(echo "$RESP" | tail -1)
    echo "Request $i: $CODE"
    sleep 3
  done
  
  # Expected: First 10 return 200, rest return 429
  ```

- [ ] Verify headers:
  ```bash
  curl -i -X POST https://rag-system-api-staging/query -d '{"query": "test"}'
  # Should see: X-RateLimit-Limit: 10
  # Should see: X-RateLimit-Remaining: 9
  ```

**Deliverable:** Rate limiter active, requests throttled after limit

---

### Day 10: Credential Management (2 hours)

**Goal:** Never hardcode secrets

**Task 1: Audit git history (0.5 hours)**
- [ ] Check for exposed secrets:
  ```bash
  git log -p -- | grep -i "api_key\|password\|secret" | head -20
  
  # If found:
  # - Record the commit
  # - Plan remediation (git filter-repo to remove)
  ```

- [ ] Check current environment variables:
  ```bash
  # Render dashboard → Settings → Environment
  # Verify OPENAI_API_KEY is in "Secrets", not visible in code
  ```

**Task 2: Move secrets to Render (1 hour)**
- [ ] Render dashboard → Settings → Environment:
  - Remove any hardcoded secrets from git
  - Add secrets:
    ```
    OPENAI_API_KEY = sk-...
    POSTGRES_URL = postgresql://...
    ```

- [ ] Verify in code:
  ```python
  from fastapi import FastAPI
  import os
  
  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
      raise RuntimeError("OPENAI_API_KEY not set")
  ```

- [ ] Test:
  ```bash
  # Deploy to Render
  # Verify app starts with secrets in environment
  curl https://rag-system-api-s09i.onrender.com/health
  # Should return 200 OK (means OpenAI key loaded)
  ```

**Task 3: Implement credential sanitization in logs (0.5 hours)**
- [ ] Add to `app/logging/sanitizer.py`:
  ```python
  PATTERNS = [
      (r'api_key["\']?\s*[:=]\s*["\']?([^"\';\s]+)', 'api_key=REDACTED'),
      (r'sk[-_][a-zA-Z0-9]+', 'sk-REDACTED'),
      (r'postgresql://[^@]+@', 'postgresql://USER:PASS@'),
  ]
  ```

- [ ] Test:
  ```bash
  python -c "
  from app.logging.sanitizer import CredentialSanitizer
  msg = 'Connected to postgresql://user:pass@localhost'
  clean = CredentialSanitizer.sanitize(msg)
  assert 'pass' not in clean
  print('✓ Credentials redacted')
  "
  ```

**Deliverable:** Secrets managed by Render, never in code

---

### Day 11: Audit Logging (2 hours)

**Goal:** Compliance & forensics

**Task 1: Create audit log table (1 hour)**
- [ ] Create `app/models/audit.py`:
  ```python
  from sqlalchemy import Column, Integer, String, DateTime, JSON
  from app.db import Base
  
  class AuditLog(Base):
      __tablename__ = "audit_logs"
      
      id = Column(Integer, primary_key=True)
      timestamp = Column(DateTime, default=datetime.utcnow)
      action = Column(String)  # query, upload, delete
      user_ip = Column(String)
      resource = Column(String)  # doc ID
      details = Column(JSON)
  ```

- [ ] Run migration:
  ```bash
  # Alembic migration or raw SQL:
  # CREATE TABLE audit_logs (
  #   id SERIAL PRIMARY KEY,
  #   timestamp TIMESTAMP DEFAULT NOW(),
  #   action VARCHAR,
  #   user_ip VARCHAR,
  #   resource VARCHAR,
  #   details JSONB
  # );
  ```

**Task 2: Log user actions (0.5 hours)**
- [ ] Add logging to endpoints:
  ```python
  from app.models import AuditLog
  from app.db import SessionLocal
  
  @app.post("/query")
  async def query(q: str, request: Request):
      # Log the action
      log = AuditLog(
          action='query',
          user_ip=request.client.host,
          resource='search',
          details={'query_length': len(q)}
      )
      db = SessionLocal()
      db.add(log)
      db.commit()
      
      # Process query...
  ```

**Task 3: Setup audit log cleanup (0.5 hours)**
- [ ] Create cleanup cron job:
  ```python
  # Run daily at 3 AM UTC
  from apscheduler.schedulers.background import BackgroundScheduler
  from datetime import datetime, timedelta
  
  def cleanup_old_audit_logs():
      """Delete audit logs older than 90 days"""
      cutoff = datetime.utcnow() - timedelta(days=90)
      db = SessionLocal()
      db.query(AuditLog).filter(AuditLog.timestamp < cutoff).delete()
      db.commit()
  
  scheduler = BackgroundScheduler()
  scheduler.add_job(cleanup_old_audit_logs, 'cron', hour=3)
  scheduler.start()
  ```

**Deliverable:** Audit logs recording all user actions

---

### Day 12: Authentication (API Keys) (2 hours)

**Goal:** Control who can access the API

**Task 1: Create API key table (1 hour)**
- [ ] Create `app/models/api_key.py`:
  ```python
  from sqlalchemy import Column, String, DateTime, Boolean
  from app.db import Base
  
  class APIKey(Base):
      __tablename__ = "api_keys"
      
      key = Column(String, primary_key=True)
      name = Column(String)  # "Demo", "Production", etc.
      created_at = Column(DateTime, default=datetime.utcnow)
      last_used_at = Column(DateTime, nullable=True)
      is_active = Column(Boolean, default=True)
  ```

- [ ] Generate keys:
  ```python
  import secrets
  
  def generate_api_key(name: str) -> str:
      """Generate new API key"""
      key = secrets.token_urlsafe(32)
      db = SessionLocal()
      db.add(APIKey(key=key, name=name))
      db.commit()
      return key
  
  # Usage:
  demo_key = generate_api_key("Demo")
  print(f"Demo API Key: {demo_key}")
  ```

**Task 2: Add auth middleware (0.5 hours)**
- [ ] Create `app/middleware/auth.py`:
  ```python
  from fastapi import Header, HTTPException
  from app.db import SessionLocal
  from app.models import APIKey
  
  async def verify_api_key(x_api_key: str = Header(...)):
      """Verify API key on protected endpoints"""
      db = SessionLocal()
      key = db.query(APIKey).filter(APIKey.key == x_api_key).first()
      
      if not key or not key.is_active:
          raise HTTPException(status_code=401, detail="Invalid API key")
      
      # Update last_used_at
      key.last_used_at = datetime.utcnow()
      db.commit()
      
      return key
  
  @app.post("/query")
  async def query(q: str, api_key: APIKey = Depends(verify_api_key)):
      # Only valid keys can query
  ```

**Task 3: Test authentication (0.5 hours)**
- [ ] Deploy and test:
  ```bash
  # Without key
  curl -X POST https://rag-system-api/query -d '{"query": "test"}'
  # Expected: 403 Forbidden
  
  # With valid key
  curl -X POST https://rag-system-api/query \
    -H "X-API-Key: $DEMO_KEY" \
    -d '{"query": "test"}'
  # Expected: 200 OK with results
  ```

**Deliverable:** API key authentication required for all endpoints

---

### Day 13: Security Testing (2 hours)

**Goal:** Verify defenses work

**Task 1: Injection attack tests (1 hour)**
- [ ] Create `tests/test_security.py`:
  ```python
  def test_sql_injection_blocked():
      payload = 'test"; DROP TABLE embeddings; --'
      with pytest.raises(ValueError):
          RAGInputValidator.validate_query(payload)
  
  def test_xss_blocked():
      payload = 'test<script>alert(1)</script>'
      with pytest.raises(ValueError):
          RAGInputValidator.validate_query(payload)
  
  def test_api_key_not_in_logs():
      # Verify credential redaction
      logger.info("Error: API key sk-12345")
      # Check logs don't contain "sk-12345"
  ```

- [ ] Run tests:
  ```bash
  pytest tests/test_security.py -v
  # Expected: All pass
  ```

**Task 2: Manual penetration tests (1 hour)**
- [ ] Test large payload DoS:
  ```bash
  curl -X POST https://rag-system-api/query \
    -d "{\"query\": \"$(python -c 'print("a"*100000)')\"}"
  # Expected: 400 (rejected by validator)
  ```

- [ ] Test rate limiting:
  ```bash
  for i in {1..20}; do
    curl -X POST https://rag-system-api/query -d '{"query": "test"}'
  done | grep -c "429"
  # Expected: ~10 returns 429
  ```

- [ ] Test missing auth:
  ```bash
  curl -X POST https://rag-system-api/query -d '{"query": "test"}'
  # Expected: 401 (missing API key)
  ```

**Deliverable:** All security tests passing

---

### Day 14: Week 2 Sign-Off (1 hour)

**Checklist:**
- [ ] Input validation prevents injection attacks
- [ ] Rate limiting enforces 10 req/min per IP
- [ ] Credentials never appear in logs
- [ ] Secrets managed by Render environment
- [ ] Audit logs recording user actions
- [ ] API key authentication required
- [ ] All security tests passing (100%)

**Commit:**
```bash
git add app/validators app/middleware app/models tests/
git commit -m "feat(security): add input validation, rate limiting, auth, audit logging"
git push origin main  # Deploy to production
```

**Deliverable:** Security hardened system deployed

---

## 📦 WEEK 3: DISASTER RECOVERY (May 29 - June 4)

### Day 15: Backup Strategy (2 hours)

**Goal:** Recover from data loss

**Task 1: PostgreSQL backups (0.5 hours)**
- [ ] Verify Render manages backups:
  ```bash
  # Render dashboard → PostgreSQL → Backups
  # Check:
  # - Automatic daily backups: YES
  # - Retention: 7 days (default)
  # - Last backup: [date]
  ```

- [ ] Document in runbook:
  ```markdown
  # PostgreSQL Backups
  - Render automatically backs up daily
  - Retention: 7 days rolling window
  - To restore: Render dashboard → Database → Backups → Restore
  - Recovery time: ~15 minutes
  ```

**Task 2: ChromaDB backups (1 hour)**
- [ ] Create backup script:
  ```bash
  #!/bin/bash
  # scripts/backup_chromadb.sh
  
  BACKUP_DIR="/tmp/chromadb_backups"
  mkdir -p $BACKUP_DIR
  
  # Copy ChromaDB data
  TIMESTAMP=$(date +%s)
  cp -r /path/to/chromadb $BACKUP_DIR/chromadb_$TIMESTAMP
  
  # Keep only last 7 days
  find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
  
  echo "ChromaDB backup complete: chromadb_$TIMESTAMP"
  ```

- [ ] Schedule as cron job:
  ```bash
  # Add to crontab
  0 */6 * * * /app/scripts/backup_chromadb.sh
  # (Run every 6 hours: 12am, 6am, 12pm, 6pm)
  ```

- [ ] Test backup:
  ```bash
  bash scripts/backup_chromadb.sh
  ls -lh /tmp/chromadb_backups/
  # Should see: chromadb_1715800000/
  ```

**Task 3: S3 offsite backups (0.5 hours)**
- [ ] Create `scripts/backup_to_s3.sh`:
  ```bash
  #!/bin/bash
  
  AWS_BUCKET="rag-system-backups"
  
  # Sync local backups to S3
  aws s3 sync /tmp/chromadb_backups \
    s3://$AWS_BUCKET/chromadb/ \
    --delete  # Remove old backups
  
  # Sync PostgreSQL backups (from Render)
  # (Render has its own S3 export feature)
  ```

- [ ] Schedule:
  ```bash
  # Add to crontab (after local backup)
  10 */6 * * * /app/scripts/backup_to_s3.sh
  ```

**Deliverable:** Daily backups running, offsite copy verified

---

### Day 16: PostgreSQL Restore Testing (1 hour)

**Goal:** Verify recovery procedure works

**Task 1: Test restore procedure (1 hour)**
- [ ] Create test database:
  ```bash
  # Render dashboard → PostgreSQL → Backups
  # Click "Restore" → Select backup from 24 hours ago
  # Wait for restore to complete (~15 min)
  ```

- [ ] Verify restore:
  ```bash
  # Connect to restored DB
  psql $RESTORED_DATABASE_URL -c "SELECT COUNT(*) FROM documents;"
  # Should match original count
  ```

- [ ] Delete test database:
  ```bash
  # Render dashboard → Databases → [test-db] → Delete
  ```

- [ ] Document:
  ```markdown
  # PostgreSQL Restore Test - May 16, 2026
  - Backup age: 24 hours
  - Restore time: 14 minutes
  - Data integrity: VERIFIED (count matches)
  - Document count: 12345
  - Restore procedure: WORKS
  
  Tested by: Ram
  Date: May 16, 2026
  ```

**Deliverable:** Restore procedure tested and documented

---

### Day 17: ChromaDB Restore Testing (1 hour)

**Goal:** Practice recovery

**Task 1: Test ChromaDB restore (1 hour)**
- [ ] Create backup:
  ```bash
  bash scripts/backup_chromadb.sh
  BACKUP_DIR=$(ls -td /tmp/chromadb_backups/*/ | head -1)
  echo "Latest backup: $BACKUP_DIR"
  ```

- [ ] Simulate data loss:
  ```bash
  # Delete all ChromaDB data (in test env only!)
  rm -rf /path/to/chromadb/*
  ```

- [ ] Restore from backup:
  ```bash
  # Copy backup back
  cp -r $BACKUP_DIR/* /path/to/chromadb/
  ```

- [ ] Verify:
  ```bash
  # Query restored data
  python -c "
  from app.rag import chroma_client
  collection = chroma_client.get_or_create_collection('documents')
  print(f'Documents restored: {collection.count()}')
  "
  # Should match original count
  ```

- [ ] Document:
  ```markdown
  # ChromaDB Restore Test - May 17, 2026
  - Backup age: 6 hours
  - Restore time: 2 minutes
  - Data integrity: VERIFIED
  - Document count before: 12345
  - Document count after: 12345
  - Recovery procedure: WORKS
  
  Tested by: Ram
  ```

**Deliverable:** Restore procedure proven to work

---

### Day 18: Disaster Recovery Runbook (2 hours)

**Goal:** Document recovery procedures

**Task 1: Write comprehensive runbook (2 hours)**
- [ ] Create `runbooks/DISASTER_RECOVERY.md` (use audit plan as template)

- [ ] Include scenarios:
  - PostgreSQL corruption → Restore from backup
  - ChromaDB loss → Restore from S3 backup
  - OpenAI API unavailable → Fallback to cached embeddings
  - Deployment broken → Rollback via git revert
  - Rate limiter overwhelmed → Circuit breaker protection

- [ ] For each scenario:
  - Detection (how to know it happened)
  - Immediate action (0-5 min)
  - Root cause analysis (5-60 min)
  - Recovery (steps to fix)
  - Prevention (how to avoid next time)

- [ ] Add contact info:
  ```markdown
  ## Emergency Contacts
  - On-call engineer: [name] ([phone])
  - DevOps lead: [name] ([phone])
  - Render support: support@render.com
  - Slack: #rag-system-incidents
  ```

**Deliverable:** Comprehensive disaster recovery runbook

---

### Day 19: Rollback Procedure (1 hour)

**Goal:** Quick recovery from bad deployments

**Task 1: Document rollback (1 hour)**
- [ ] Create `ROLLBACK.md`:
  ```markdown
  # Rollback Procedure
  
  ## Fast Rollback (0-5 minutes)
  ```bash
  # Find last good commit
  git log --oneline -5
  
  # Revert bad commit
  git revert HEAD  # or specify commit hash
  
  # Push (auto-deploys on Render)
  git push origin main
  
  # Wait for deploy (watch logs)
  # Render dashboard → Logs → Deploy logs
  
  # Verify
  curl https://rag-system-api/health
  ```
  
  ## If git revert fails:
  ```bash
  # Hard reset to specific commit
  git reset --hard <commit-hash>
  git push -f origin main  # Force push (dangerous, use carefully)
  ```
  
  ## Render manual rollback:
  ```bash
  # Render dashboard → Deployments
  # Find working deployment
  # Click "Redeploy"
  ```
  ```

- [ ] Test rollback:
  ```bash
  # Create test branch
  git checkout -b test/rollback
  
  # Make a deliberate bad change
  echo "# BROKEN" >> app/main.py
  
  # Push (triggers deploy)
  git push -u origin test/rollback
  
  # Watch it fail in Render
  # Then revert:
  git revert HEAD
  git push origin test/rollback
  
  # Verify it works again
  ```

- [ ] Clean up:
  ```bash
  git checkout main
  git branch -D test/rollback
  ```

**Deliverable:** Rollback procedure tested and working

---

### Day 20-21: Week 3 Sign-Off (1 hour)

**Checklist:**
- [ ] PostgreSQL backups verified (daily, 7-day retention)
- [ ] ChromaDB backups running (every 6 hours)
- [ ] S3 offsite backups synced
- [ ] PostgreSQL restore tested (works)
- [ ] ChromaDB restore tested (works)
- [ ] Disaster recovery runbook written
- [ ] Rollback procedure documented and tested

**Commit:**
```bash
git add runbooks/ scripts/
git commit -m "docs: add disaster recovery runbooks and backup procedures"
git push origin main
```

**Deliverable:** Full disaster recovery capability

---

## 📋 WEEK 4: COMPLIANCE & SIGN-OFFS (June 5-14)

### Day 22: Data Retention Policy (1 hour)

**Task 1: Write policy (1 hour)**
- [ ] Create `COMPLIANCE.md`:
  ```markdown
  # Data Retention & Privacy Policy
  
  ## What We Collect
  - User queries (text)
  - Uploaded documents (content)
  - Embeddings (vectors)
  - API logs (timestamps, IPs)
  
  ## How Long We Keep It
  - Queries: 90 days (then auto-delete)
  - Documents: Until user deletes
  - Embeddings: Delete with document
  - Logs: 30 days (Render default)
  
  ## User Rights
  - Right to delete their documents
  - Right to export their data (GDPR Art. 20)
  - Right to be forgotten (GDPR Art. 17)
  
  ## Compliance
  - GDPR: EU user data protection
  - CCPA: California privacy rights
  - SOC 2: Audit trails (we have!)
  ```

**Deliverable:** Compliance policy documented

---

### Day 23-28: Implementation Verification (Ongoing)

**Task 1: Create verification checklist**

```
✅ MONITORING
  ☑ JSON structured logs flowing
  ☑ Prometheus metrics at /metrics
  ☑ Health checks every 30 sec
  ☑ Grafana dashboard live
  ☑ Slack alerts configured

✅ SECURITY
  ☑ Input validation prevents injection
  ☑ Rate limiting enforced
  ☑ Credentials never in logs
  ☑ API keys managed by Render
  ☑ Audit logs recording actions
  ☑ API key auth required
  ☑ All security tests passing

✅ DISASTER RECOVERY
  ☑ PostgreSQL backups automated
  ☑ ChromaDB backups every 6h
  ☑ S3 offsite backups synced
  ☑ Restore procedures tested
  ☑ Rollback procedure works
  ☑ Runbooks written

✅ COMPLIANCE
  ☑ Data retention policy
  ☑ Audit logs implemented
  ☑ User delete endpoint
  ☑ Privacy policy created
  ☑ Team trained
```

**Deliverable:** All items verified

---

### Day 29-30: Final Sign-Offs (2 hours)

**Task 1: Get stakeholder approval**

Email to:
- [ ] **Engineering Lead**
  ```
  Subject: RAG System Production Audit - Sign-Off Needed
  
  We've completed a 30-day production hardening audit.
  
  ITEMS COMPLETED:
  ✓ Monitoring (logs, metrics, alerts)
  ✓ Security (validation, rate limiting, auth)
  ✓ Disaster recovery (backups, restore testing)
  ✓ Compliance (data retention, audit logs)
  
  All tests passing. Ready for your sign-off.
  
  Can you review and confirm readiness?
  ```

- [ ] **Security Lead**
  ```
  Subject: RAG System Security Audit Complete
  
  Security hardening completed:
  - Input validation prevents injection attacks
  - Rate limiting prevents DoS
  - Credentials managed securely
  - All logs sanitized
  - Audit trails in place
  
  Sign-off requested.
  ```

- [ ] **DevOps Lead**
  ```
  Subject: RAG System Backup & Recovery Verified
  
  - PostgreSQL backups: Daily (7-day retention)
  - ChromaDB backups: Every 6 hours (S3 synced)
  - Restore procedures: Tested and verified
  - Rollback automation: Works
  
  Sign-off requested.
  ```

**Task 2: Collect sign-offs**

```
Audit Completion Checklist
===========================

Engineering Lead: ________________ Date: _____ Sign: _____

Security Lead: ________________ Date: _____ Sign: _____

DevOps Lead: ________________ Date: _____ Sign: _____

Product Lead: ________________ Date: _____ Sign: _____

FINAL STATUS: ☐ APPROVED FOR CONTINUED PRODUCTION USE
```

**Deliverable:** All stakeholder sign-offs collected

---

## 🎯 SUCCESS METRICS (End of 30 Days)

### Observability
- ✅ Structured JSON logs flowing (zero plain text)
- ✅ Metrics exposed at `/metrics` (20+ metrics tracked)
- ✅ Health checks responsive (<1 sec)
- ✅ Grafana dashboard showing live data
- ✅ Mean time to detect (MTTD): <1 minute

### Security
- ✅ Input validation prevents injection (100% test pass rate)
- ✅ Rate limiter enforced (tested and working)
- ✅ Zero credentials in logs (verified with searches)
- ✅ API authentication required (tested)
- ✅ Audit logs recording all actions

### Reliability
- ✅ PostgreSQL backups daily (7-day retention)
- ✅ ChromaDB backups every 6 hours
- ✅ Restore procedures tested (both successful)
- ✅ Disaster recovery runbook (12+ scenarios)
- ✅ Rollback procedure working (<5 min recovery)
- ✅ Mean time to recovery (MTTR): <15 minutes

### Compliance
- ✅ Data retention policy documented
- ✅ Audit logs in place
- ✅ User privacy controls
- ✅ Compliance checklist completed
- ✅ Team trained on procedures

---

## 📞 ONGOING MAINTENANCE

### Weekly (Every Monday)
- [ ] Review error logs for patterns
- [ ] Check backup logs (no failures)
- [ ] Verify health checks (100% success)
- [ ] Monitor query latency (no degradation)

### Monthly (First Friday)
- [ ] Test disaster recovery procedure
- [ ] Review and rotate API keys
- [ ] Update runbooks if procedures changed
- [ ] Analyze metrics trends

### Quarterly
- [ ] Load test (simulate peak usage)
- [ ] Penetration test (if budget allows)
- [ ] Dependency updates (security patches)
- [ ] Capacity planning review

---

**Owner:** qualigenai (Ram)  
**Start Date:** May 15, 2026  
**Target Completion:** June 14, 2026  
**Status:** IN PROGRESS
