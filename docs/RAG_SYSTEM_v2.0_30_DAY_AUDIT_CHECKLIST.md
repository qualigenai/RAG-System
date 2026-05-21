# 30-Day Post-Deployment Audit Checklist
## Enterprise RAG System v2.0

**Deployment Date:** May 2026 (v2.0 branch)  
**Audit Start Date:** May 15, 2026  
**Target Completion:** June 14, 2026  
**Endpoint:** https://rag-system-api-v2.onrender.com  
**Owner:** qualigenai (Ram)  

---

## OVERVIEW

This is the **v2.0-specific audit checklist**. Same process as v1.5, but for the separate v2.0 instance.

All tasks reference the v2.0 endpoint and git branch.

---

## 🔍 WEEK 1: AUDIT & MONITORING SETUP (May 15-21)

### Day 1: Current State Assessment (2 hours)

**Morning (30 min):**
- [ ] Check v2.0 endpoint availability:
  ```bash
  curl -v https://rag-system-api-v2.onrender.com/health
  ```

- [ ] Check Render logs for v2.0:
  ```bash
  # Render dashboard → Services → rag-system-api-v2 → Logs
  # Screenshot last 100 lines
  # Save to: logs/v2.0_baseline_May15_2026.txt
  ```

- [ ] Document response times for v2.0:
  ```bash
  for i in {1..10}; do
    time curl -X POST \
      https://rag-system-api-v2.onrender.com/query \
      -H "Content-Type: application/json" \
      -d '{"query": "test query"}'
  done
  # Average time: _____ sec
  ```

**Afternoon (1.5 hours):**
- [ ] Check v2.0 PostgreSQL:
  ```bash
  # Render dashboard → PostgreSQL (v2.0 instance) → Connections
  # Current connections: ___
  # Max connections: ___
  ```

- [ ] Verify v2.0 ChromaDB:
  ```python
  # SSH to Render v2.0 service
  # python -c "
  # from app.rag import chroma_client
  # collection = chroma_client.get_or_create_collection('documents')
  # print(f'Documents in ChromaDB v2.0: {collection.count()}')
  # "
  ```

- [ ] Create risk register for v2.0:
  ```bash
  cp risk_register_template.xlsx risk_register_rag_system_v2.0.xlsx
  # Fill in findings from above
  ```

**Deliverable:** `v2.0_CURRENT_STATE_REPORT.md` (document all findings)

---

### Day 2: Structured Logging Setup (3 hours)

**Task 1: Update logging config (1 hour)**
- [ ] In v2.0 git branch:
  ```bash
  git checkout v2.0  # Switch to v2.0 branch
  ```

- [ ] Create `app/logging/config.py`:
  ```bash
  # See RAG_SYSTEM_v2.0_PRODUCTION_CODE_SNIPPETS.md for full code
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
- [ ] Add sanitizer filter
- [ ] Test sanitization works
- [ ] Verify no secrets in logs

**Task 3: Deploy to v2.0 (1 hour)**
- [ ] Commit changes:
  ```bash
  git add app/logging/
  git commit -m "feat: add structured JSON logging with credential sanitization (v2.0)"
  git push origin v2.0  # Push to v2.0 branch
  ```

- [ ] Verify in Render logs:
  ```bash
  # Render dashboard → rag-system-api-v2 → Logs
  # Should see JSON output
  ```

**Deliverable:** JSON logs flowing through Render for v2.0

---

### Days 3-7: Complete Week 1 Tasks

Follow the same structure as Days 2-7:
- Day 3: Prometheus Metrics
- Day 4: Health Checks & Alerting
- Day 5: Create Monitoring Dashboard
- Day 6: Baseline Metrics & Alert Rules
- Day 7: Week 1 Sign-Off

**All using v2.0 endpoint:** `https://rag-system-api-v2.onrender.com`

---

## 🔒 WEEK 2: SECURITY HARDENING (May 22-28)

### Day 8: Input Validation (3 hours)
- [ ] Create `app/validators/rag_validator.py` (v2.0 branch)
- [ ] Add to FastAPI routes
- [ ] Write validation tests
- [ ] Integration test injection attacks

### Day 9: Rate Limiting (2 hours)
- [ ] Add rate limiter middleware
- [ ] Test rate limiting (should throttle after 10 req/min)
- [ ] Verify headers returned

### Day 10: Credential Management (2 hours)
- [ ] Audit git history for secrets
- [ ] Move to Render environment (v2.0 settings)
- [ ] Verify secrets are not in code

### Day 11: Audit Logging (2 hours)
- [ ] Create audit log table
- [ ] Log user actions
- [ ] Setup cleanup cron job

### Day 12: Authentication (API Keys) (2 hours)
- [ ] Create API key table
- [ ] Generate keys
- [ ] Add auth middleware

### Day 13: Security Testing (2 hours)
- [ ] Injection attack tests
- [ ] Manual penetration tests
- [ ] Verify all pass

### Day 14: Week 2 Sign-Off (1 hour)
- [ ] All security items checked
- [ ] Get week 2 stakeholder sign-off

---

## 📦 WEEK 3: DISASTER RECOVERY (May 29 - June 4)

### Day 15: Backup Strategy (2 hours)
- [ ] PostgreSQL backups (Render managed)
- [ ] ChromaDB backup script
- [ ] Cleanup old backups

### Day 16: PostgreSQL Restore Testing (1 hour)
- [ ] Test restore procedure
- [ ] Verify data integrity
- [ ] Document procedure

### Day 17: ChromaDB Restore Testing (1 hour)
- [ ] Test restore from backup
- [ ] Verify document count matches
- [ ] Document procedure

### Day 18: Disaster Recovery Runbook (2 hours)
- [ ] Write comprehensive runbook
- [ ] Cover 5+ failure scenarios
- [ ] Add emergency contacts

### Day 19: Rollback Procedure (1 hour)
- [ ] Document rollback steps
- [ ] Test git revert works
- [ ] Verify quick recovery

### Days 20-21: Week 3 Sign-Off (1 hour)
- [ ] All recovery items verified
- [ ] Get week 3 stakeholder sign-off

---

## 📋 WEEK 4: COMPLIANCE & SIGN-OFFS (June 5-14)

### Day 22: Data Retention Policy (1 hour)
- [ ] Create COMPLIANCE.md
- [ ] Document retention periods
- [ ] Include user rights

### Days 23-28: Implementation Verification (Ongoing)
- [ ] Verify all items complete
- [ ] Run full test suite
- [ ] Check all metrics active

### Days 29-30: Final Sign-Offs (2 hours)
- [ ] Collect stakeholder approvals:
  - [ ] QA Lead: ________________ Date: _____ Sign: _____
  - [ ] Security Lead: ________________ Date: _____ Sign: _____
  - [ ] DevOps Lead: ________________ Date: _____ Sign: _____
  - [ ] Product Lead: ________________ Date: _____ Sign: _____

**FINAL STATUS:** ☐ APPROVED FOR PRODUCTION (v2.0)

---

## 🎯 SUCCESS CRITERIA (End of 30 Days - v2.0)

### Observability ✅
- [ ] Structured JSON logs flowing
- [ ] Metrics exported to Prometheus
- [ ] Health checks responding (<1 sec)
- [ ] Grafana dashboard showing live data
- [ ] Mean time to detect (MTTD): <1 minute

### Security ✅
- [ ] Input validation preventing injection (100% pass rate)
- [ ] Rate limiting enforced (tested)
- [ ] Zero credentials in logs (verified)
- [ ] API authentication required (tested)
- [ ] Audit logs in database

### Reliability ✅
- [ ] PostgreSQL backups daily (7-day retention)
- [ ] ChromaDB backups every 6 hours
- [ ] Restore procedures tested (both successful)
- [ ] Disaster recovery runbook (12+ scenarios)
- [ ] Rollback procedure working (<5 min recovery)
- [ ] Mean time to recovery (MTTR): <15 minutes

### Compliance ✅
- [ ] Data retention policy documented
- [ ] Audit logs in place
- [ ] User privacy controls
- [ ] Compliance checklist completed
- [ ] Team trained on procedures

---

## 📁 FOLDER STRUCTURE FOR v2.0

```
rag-system/ (v2.0 branch)
├── docs/
│   ├── README.md                                    (link to docs)
│   ├── PRODUCTION_AUDIT_PLAN.md                    (this is v2.0 version)
│   ├── 30_DAY_AUDIT_CHECKLIST.md                   (follow daily)
│   ├── PRODUCTION_CODE_SNIPPETS.md                 (copy code from here)
│   ├── v2.0_CURRENT_STATE_REPORT.md                (Day 1 output)
│   └── COMPLIANCE.md                                (Week 4 output)
│
├── runbooks/
│   ├── DISASTER_RECOVERY.md                        (Week 3 output)
│   ├── ROLLBACK.md                                 (Week 3 output)
│   └── TROUBLESHOOTING.md                          (Week 4 output)
│
└── [rest of v2.0 code...]
```

---

## 📞 NEXT STEP

1. **Download:** This checklist (✓ done)
2. **Create v2.0 docs folder:**
   ```powershell
   mkdir -p docs runbooks
   cp RAG_SYSTEM_v2.0_PRODUCTION_AUDIT_PLAN.md docs/
   cp RAG_SYSTEM_v2.0_30_DAY_AUDIT_CHECKLIST.md docs/
   cp RAG_SYSTEM_v2.0_PRODUCTION_CODE_SNIPPETS.md docs/
   ```

3. **Start Day 1 TODAY:**
   - Test v2.0 endpoint
   - Document current state
   - Create CURRENT_STATE_REPORT.md

---

**Owner:** qualigenai (Ram)  
**Period:** May 15 - June 14, 2026  
**Endpoint:** https://rag-system-api-v2.onrender.com  
**Status:** ✅ Ready to start audit
