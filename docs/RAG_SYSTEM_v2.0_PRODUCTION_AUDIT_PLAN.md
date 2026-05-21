# Production Audit & Hardening Plan
## Enterprise RAG System v2.0 (Post-Deployment)

**System Status:** LIVE IN PRODUCTION (May 2026)  
**Deployment Platform:** Render (Free Tier)  
**Backend Endpoint:** https://rag-system-api-v2.onrender.com  
**Version:** 2.0 (separate branch from v1.5)  
**Tech Stack:** FastAPI + ChromaDB + PostgreSQL + OpenAI embeddings  
**Owner:** qualigenai (Ram)  

---

## Executive Summary

Your RAG System v2.0 is live and **operating blind** - just like v1.5 was. 

This is a **parallel production instance** to v1.5, so it also needs the same **7 control pillars hardening**:

```
✓ Deployed
✓ Accessible at: https://rag-system-api-v2.onrender.com
✗ Monitored
✗ Secured
✗ Recoverable
✗ Scalable
✗ Compliant
```

**This plan provides a 30-day hardening roadmap for v2.0.**

---

## 🔍 CURRENT STATE ASSESSMENT

### v2.0 is identical to v1.5 in terms of:
- ✅ Tech stack (FastAPI + ChromaDB)
- ✅ Database (PostgreSQL on Render)
- ✅ Embeddings (OpenAI text-embedding-3-small)
- ✅ Architecture (same as v1.5)

### Differences:
- Different Render endpoint: `https://rag-system-api-v2.onrender.com` (not v1.5's endpoint)
- Separate git branch
- Separate ChromaDB and PostgreSQL instances

### What's Missing (Same as v1.5):
| Control Pillar | Status | Gap | Risk |
|---|---|---|---|
| **Risk Assessment** | ❌ None | No threat model | Unknown vulnerabilities |
| **Risk Treatment** | ⚠️ Partial | No input validation, rate limiting | Injection attacks, DoS |
| **Validation** | ❌ None | No integration tests, security tests | Regressions, silent failures |
| **Monitoring** | ❌ None | No logs, metrics, alerts | Blind to issues |
| **Access Control** | ⚠️ Partial | OpenAI key in env vars, no RBAC | Credential compromise |
| **Recovery** | ❌ None | No backups, no rollback | Data loss, prolonged outages |
| **Governance** | ❌ None | No runbooks, no audit trail | Uncontrolled operations |

---

## 1. RISK ASSESSMENT (v2.0 Specific)

### 1.1 Threat Model - RAG System v2.0

```
┌─────────────────────────────────────────────────────────┐
│  Internet Users / Clients                              │
│  (Documents uploaded, queries submitted)                │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS
                   ▼
        ┌──────────────────────┐
        │  Frontend (React)    │
        │  v2.0 instance       │
        │  (Render)            │
        └──────────┬───────────┘
                   │ API calls
                   ▼
        ┌──────────────────────────┐
        │  FastAPI Backend v2.0    │
        │  rag-system-api-v2       │
        │  (Render)                │
        │  - Input validation ⚠️   │
        │  - Rate limiting ❌      │
        │  - Error handling ⚠️     │
        └──────┬──────────────┬────┘
               │              │
               ▼              ▼
        ┌──────────────┐  ┌──────────────┐
        │ ChromaDB v2  │  │ PostgreSQL   │
        │ (Vector DB)  │  │ (v2.0 db)    │
        │ - No auth ❌ │  │ - Encrypted? │
        │ - No backup? │  │ - Backed up? │
        └──────────────┘  └──────────────┘
               │
               ▼
        ┌──────────────────────┐
        │ OpenAI API           │
        │ (embeddings)         │
        │ - Key in env ⚠️      │
        └──────────────────────┘
```

**Same risks as v1.5, but affecting v2.0 instance separately.**

---

## 2. RISK TREATMENT

See **RAG_SYSTEM_v2.0_PRODUCTION_CODE_SNIPPETS.md** for implementation.

All code snippets are identical to v1.5 version - copy them into your v2.0 codebase.

---

## 3. VALIDATION STRATEGY

Same validation approach as v1.5:
- Unit tests (85%+ coverage)
- Integration tests (end-to-end workflows)
- Security tests (injection prevention)

---

## 4. MONITORING

Same monitoring requirements as v1.5:
- Structured logging (JSON format)
- Prometheus metrics
- Health checks
- Grafana dashboards
- Alert routing

---

## 5. ACCESS CONTROL

Same access boundary requirements as v1.5:
- API token scoping
- Credential management
- K8s RBAC (if applicable)
- Network policies

---

## 6. RECOVERY & DISASTER RECOVERY

Same recovery approach as v1.5:
- Backups (PostgreSQL + ChromaDB)
- Restore procedures
- Rollback automation
- Runbooks

---

## 7. GOVERNANCE & COMPLIANCE

Same compliance requirements as v1.5:
- Data retention policy
- Audit logging
- Documentation
- Sign-offs

---

## 📋 30-DAY HARDENING ROADMAP FOR v2.0

Identical to v1.5 30-day plan:

```
WEEK 1 (May 15-21): MONITORING & OBSERVABILITY
├─ Day 1: Current state assessment
├─ Day 2: Structured logging setup
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
├─ Day 18: Disaster recovery runbook
├─ Day 19: Rollback procedure
└─ Days 20-21: Week 3 sign-off

WEEK 4 (Jun 5-14): COMPLIANCE & SIGN-OFFS
├─ Day 22: Data retention policy
├─ Days 23-28: Implementation verification
└─ Days 29-30: Final sign-offs
```

---

## ✅ KEY DIFFERENCES: v2.0 vs v1.5

| Aspect | v1.5 | v2.0 |
|--------|------|------|
| Endpoint | rag-system-api-s09i.onrender.com | rag-system-api-v2.onrender.com |
| Git Branch | main (or legacy) | v2.0 branch |
| PostgreSQL | Shared/separate? | Separate instance (v2.0 db) |
| ChromaDB | v1.5 instance | v2.0 instance |
| Code Base | v1.5 codebase | v2.0 codebase |
| Audit Plan | Separate (started May 15) | This plan (starting today) |

---

## 🚀 START v2.0 AUDIT TODAY

1. **Follow:** RAG_SYSTEM_v2.0_30_DAY_AUDIT_CHECKLIST.md (day-by-day)
2. **Copy code:** RAG_SYSTEM_v2.0_PRODUCTION_CODE_SNIPPETS.md (as you implement)
3. **Test against:** https://rag-system-api-v2.onrender.com

---

## 📁 FILE ORGANIZATION FOR v2.0

```
rag-system-v2.0/
├── docs/
│   ├── README.md
│   ├── PRODUCTION_AUDIT_PLAN.md          ← This file
│   ├── 30_DAY_AUDIT_CHECKLIST.md         ← Start here
│   └── PRODUCTION_CODE_SNIPPETS.md       ← Copy from here
├── app/
│   ├── logging/
│   ├── monitoring/
│   ├── validators/
│   └── [rest of code]
└── runbooks/
    ├── DISASTER_RECOVERY.md
    └── ROLLBACK.md
```

---

## ⏱️ TIMELINE FOR v2.0 AUDIT

**Start Date:** May 15, 2026 (TODAY)  
**Target Completion:** June 14, 2026  
**Duration:** 30 days (same as v1.5)

If you complete v1.5 audit on June 14, you can:
- Continue with v2.0 immediately, OR
- Run v1.5 and v2.0 audits in parallel

---

## 📞 NEXT STEPS

1. **Download:** RAG_SYSTEM_v2.0_30_DAY_AUDIT_CHECKLIST.md
2. **Open checklist:** Follow Day 1 tasks
3. **Test v2.0 endpoint:**
   ```bash
   curl https://rag-system-api-v2.onrender.com/health
   ```
4. **Create v2.0 docs folder** (similar to v1.5)
5. **Start Day 1 assessment** (today)

---

**Document Owner:** qualigenai (Ram)  
**Last Updated:** May 15, 2026  
**Status:** READY TO START v2.0 AUDIT
