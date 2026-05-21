# Production Audit & Hardening Plan
## Enterprise RAG System v2.0 (Post-Deployment)

**System Status:** LIVE IN PRODUCTION (May 2026)  
**Deployment Platform:** Render (Free Tier)  
**Backend v2.0:** https://rag-system-api-v2.onrender.com  
**Frontend:** https://rag-system-frontend-v2.onrender.com (if separate)  
**Repository Branch:** v2.0  
**Owner:** qualigenai (Ram)  

---

## Executive Summary

Your RAG System **v2.0 is live but operating blind**. Like v1.5, the deployment works, but critical controls are missing:

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

## 🔍 CURRENT STATE ASSESSMENT - v2.0

### What's Working
- FastAPI backend responds (health check: `GET /health`)
- ChromaDB hybrid retrieval operational (70% vector + 30% BM25)
- OpenAI embeddings (text-embedding-3-small) functional
- PostgreSQL storage connected (Render-hosted)
- Frontend accessible

### Critical Gaps (v2.0 Specific)
| Control Pillar | Status | Gap | Risk |
|---|---|---|---|
| **Risk Assessment** | ❌ None | No threat model | Unknown vulnerabilities |
| **Risk Treatment** | ⚠️ Partial | No input validation, rate limiting | Injection attacks, DoS |
| **Validation** | ❌ None | No integration tests, security tests | Regressions, silent failures |
| **Monitoring** | ❌ None | No logs, metrics, alerts | Blind to issues (MTTD: ∞) |
| **Access Control** | ⚠️ Partial | OpenAI key in env vars, no RBAC | Credential compromise risk |
| **Recovery** | ❌ None | No backups, no rollback procedure | Data loss, prolonged outages |
| **Governance** | ❌ None | No runbooks, no audit trail | Uncontrolled operations |

---

## 1. RISK ASSESSMENT (v2.0)

### 1.1 Threat Model - RAG System v2.0

**Same as v1.5** (identical stack), but deployed at different endpoint:

```
https://rag-system-api-v2.onrender.com (v2.0 endpoint)
vs
https://rag-system-api-s09i.onrender.com (v1.5 endpoint)

Both vulnerable to same threats:
- Input injection (SQL, prompt)
- Missing rate limiting (DoS)
- Unvalidated file uploads
- Credential exposure in logs
- Missing backups
- No disaster recovery
```

---

### 1.2 Risk Register (v2.0)

**Create file:** `risk_register_rag_system_v2.0.xlsx`

| Component | Risk | Severity | Likelihood | Impact | Owner | Status | Target Mitigation |
|-----------|------|----------|-----------|--------|-------|--------|------------------|
| Frontend | XSS in doc display | HIGH | Medium | Code injection | Ram | Not Started | Input sanitization |
| Backend | SQL injection | HIGH | Medium | Data theft | Ram | Not Started | Input validation |
| Backend | Prompt injection | MEDIUM | High | LLM manipulation | Ram | Not Started | Prompt sanitization |
| Backend | No rate limiting | MEDIUM | High | API DoS | Ram | Not Started | Rate limiter |
| Backend | Logs leak credentials | CRITICAL | High | Key theft | Ram | Not Started | Log sanitization |
| ChromaDB | No backup | CRITICAL | Medium | Data loss | Ram | Not Started | Backup cron |
| PostgreSQL | No backup verification | HIGH | Medium | Lost recovery | Ram | Not Started | Test restore |
| OpenAI | Key exposed | CRITICAL | Medium | Cost spike | Ram | Not Started | Vault + rotation |

---

## 2. RISK TREATMENT (v2.0)

Use the **same code snippets as v1.5** (stack is identical):

### 2.1 Input Validation
- Copy from: `RAG_SYSTEM_PRODUCTION_CODE_SNIPPETS.md` → Section 4
- File: `app/validators/rag_validator.py`
- Implementation: Identical to v1.5

### 2.2 Rate Limiting
- Copy from: `RAG_SYSTEM_PRODUCTION_CODE_SNIPPETS.md` → Section 5
- File: `app/middleware/rate_limiter.py`
- Configuration: 10 req/min (same as v1.5)

### 2.3 Credential Management
- Move OpenAI API key to Render secrets (same as v1.5)
- Do NOT hardcode in git

### 2.4 Log Sanitization
- Copy from: `RAG_SYSTEM_PRODUCTION_CODE_SNIPPETS.md` → Section 1
- File: `app/logging/sanitizer.py`
- Prevents credential leaks in logs

---

## 3. VALIDATION (v2.0)

### 3.1 Pre-Production Testing

**Test v2.0 endpoint:**
```bash
# Test 1: API responds
curl https://rag-system-api-v2.onrender.com/health
# Expected: {"status": "healthy"}

# Test 2: Embeddings work
curl -X POST https://rag-system-api-v2.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
# Expected: 200 with results

# Test 3: Large payload rejected (after validation added)
curl -X POST https://rag-system-api-v2.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "'"$(python -c 'print("a" * 100000)')"'"}'
# Expected: 413 (after we add validation)

# Test 4: Rate limiting works (after implementation)
for i in {1..20}; do
  curl https://rag-system-api-v2.onrender.com/query
done
# Expected: After 10 requests → 429 Too Many Requests
```

---

## 4. MONITORING (v2.0)

### 4.1 Add Observability

**Same as v1.5**, using identical code:
- Structured logging (JSON format)
- Prometheus metrics
- Health checks
- Grafana dashboards
- Alert routing

**Key difference:** Monitor v2.0 endpoint separately from v1.5

---

## 5. ACCESS BOUNDARIES (v2.0)

### 5.1 Credential Management

**v2.0 Specific Setup:**
```bash
# Render dashboard → Settings → Environment
# Add v2.0-specific secrets:
OPENAI_API_KEY_V2=sk-...          # Separate key for v2.0
POSTGRES_URL_V2=postgresql://...  # v2.0 database
CHROMADB_PATH_V2=/tmp/chromadb_v2
```

**Or:** Reuse v1.5 credentials if sharing infrastructure

---

## 6. RECOVERY CONTROLS (v2.0)

### 6.1 Backup Strategy

**Same as v1.5:**
- PostgreSQL: Render manages automatically (7-day retention)
- ChromaDB: Create backup cron job (every 6 hours)
- S3: Sync backups offsite

**v2.0 specific:**
```bash
# Backup v2.0 ChromaDB separately
0 */6 * * * /app/scripts/backup_chromadb_v2.sh
```

---

## 7. GOVERNANCE (v2.0)

### 7.1 Documentation

**Create:**
- `docs/v2.0/CURRENT_STATE_REPORT.md` (Day 1)
- `docs/v2.0/DISASTER_RECOVERY.md` (Week 3)
- `docs/v2.0/COMPLIANCE.md` (Week 4)

---

## 30-DAY HARDENING ROADMAP (v2.0)

```
WEEK 1 (May 15-21): MONITORING & OBSERVABILITY
  ├─ Day 1: Current state assessment (v2.0 endpoint)
  ├─ Day 2: Structured logging
  ├─ Day 3: Prometheus metrics
  ├─ Day 4: Health checks
  ├─ Day 5: Grafana dashboard
  ├─ Day 6: Baseline metrics
  └─ Day 7: Week 1 sign-off

WEEK 2 (May 22-28): SECURITY HARDENING
  ├─ Day 8: Input validation
  ├─ Day 9: Rate limiting
  ├─ Day 10: Credential management
  ├─ Day 11: Audit logging
  ├─ Day 12: Authentication
  ├─ Day 13: Security testing
  └─ Day 14: Week 2 sign-off

WEEK 3 (May 29 - Jun 4): DISASTER RECOVERY
  ├─ Day 15: Backup strategy
  ├─ Day 16: PostgreSQL restore testing
  ├─ Day 17: ChromaDB restore testing
  ├─ Day 18: DR runbook
  ├─ Day 19: Rollback procedure
  └─ Days 20-21: Week 3 sign-off

WEEK 4 (Jun 5-14): COMPLIANCE & SIGN-OFFS
  ├─ Day 22: Data retention policy
  ├─ Days 23-28: Verification
  └─ Days 29-30: Final sign-offs
```

---

## AFTER THIS AUDIT (v2.0)

Once v2.0 is hardened, repeat for **v1.5**:
- Same 30-day audit timeline
- Same 7-pillar framework
- Separate monitoring for v1.5 endpoint

---

## SUCCESS CRITERIA (v2.0)

### Monitoring ✅
- [ ] JSON logs flowing
- [ ] Metrics at `/metrics`
- [ ] Health checks responsive
- [ ] Grafana dashboard live
- [ ] Slack alerts configured

### Security ✅
- [ ] Input validation prevents injection
- [ ] Rate limiter enforced (10 req/min)
- [ ] Zero credentials in logs
- [ ] API keys in Render secrets
- [ ] Audit logs in database

### Reliability ✅
- [ ] PostgreSQL backups automated
- [ ] ChromaDB backups every 6h
- [ ] Restore procedures tested
- [ ] DR runbook complete
- [ ] Rollback works

### Compliance ✅
- [ ] Audit logs in place
- [ ] Data retention policy
- [ ] User privacy controls
- [ ] All sign-offs collected

---

## SIGN-OFF CHECKLIST (v2.0)

- [ ] **Engineering Lead**: _______________ Date: _____ 
- [ ] **Security Lead**: _______________ Date: _____
- [ ] **DevOps Lead**: _______________ Date: _____
- [ ] **Product Lead**: _______________ Date: _____

**System Status:** ☐ Ready for Continued Production Use

---

**Document Owner:** qualigenai (Ram)  
**Endpoint:** https://rag-system-api-v2.onrender.com  
**Branch:** v2.0  
**Created:** May 15, 2026  
**Status:** DRAFT → Awaiting execution start
