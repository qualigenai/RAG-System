# RAG System v1.5 - Automated Testing Guide

Complete automation testing framework for enterprise RAG system.

---

## 📋 Quick Start

### **Windows Users:**
```powershell
# Simple one-click testing
.\run_tests.bat
```

### **macOS/Linux Users:**
```bash
# Simple one-click testing
bash run_tests.sh
```

### **Manual Python Execution:**
```bash
python automated_tests.py
```

---

## 🎯 What Gets Tested Automatically

```
✅ Unit Tests (Pytest)
   - Authentication
   - Authorization
   - Document Upload
   - Search & Query
   - Team Management
   - API Keys
   - Audit Logs

✅ API Tests (Manual)
   - Health Check
   - User Registration
   - User Login
   - Token Validation
   - Protected Endpoints

✅ Load Tests (Locust)
   - Concurrent User Simulation
   - Search Performance
   - Upload Performance
   - Stability Under Load

✅ Security Tests
   - SQL Injection Prevention
   - XSS Prevention
   - Authentication Enforcement
   - HTTPS Validation
```

---

## 📊 Output

The automation creates:

```
test_reports/
├── test_report_20260317_143022.html    ← Open in browser!
├── test_results_20260317_143022.json   ← Machine readable
├── pytest_20260317_143022.json         ← Unit test details
├── load_test_20260317_143022_data.csv  ← Load test metrics
└── newman_20260317_143022.json         ← API test results
```

---

## 🚀 Setup & Installation

### **Step 1: Install Test Dependencies**

```bash
pip install -r requirements-test.txt
```

Or individually:

```bash
pip install pytest requests locust python-dotenv
```

### **Step 2: Ensure Backend is Running**

```bash
python -m uvicorn src.api.main:app --reload
```

Should see:
```
🚀 RAG System v1.5 started successfully!
INFO:     Application startup complete.
```

### **Step 3: Run Tests**

#### **Option A: One-Click (Easiest)**

Windows:
```powershell
.\run_tests.bat
```

macOS/Linux:
```bash
bash run_tests.sh
```

#### **Option B: Manual Python**

```bash
python automated_tests.py
```

#### **Option C: Step-by-Step**

```bash
# Unit tests only
pytest tests/test_rag_system.py -v

# Load tests only
locust -f locustfile.py --host=http://localhost:8000 -u 10 -r 2 -t 1m --headless

# API tests only
python -c "
from automated_tests import TestRunner
runner = TestRunner()
runner.check_backend_running()
runner.run_api_tests_manual()
"
```

---

## 📈 Test Phases Explained

### **Phase 1: Unit Tests (5 min)**
```
Tests individual components:
✓ Can users register? 
✓ Can users login?
✓ Can upload documents?
✓ Can search documents?
✓ Can create API keys?
✓ Are permissions enforced?

Speed: ~2-3 minutes
Pass Rate: 95%+ expected
```

### **Phase 2: API Tests (2 min)**
```
Tests REST API endpoints:
✓ /health (status check)
✓ /auth/register (registration)
✓ /auth/login (authentication)
✓ /upload (document upload)
✓ /query (search)
✓ /api/stats (dashboard)

Speed: ~1-2 minutes
Pass Rate: 100% expected
```

### **Phase 3: Load Tests (1 min)**
```
Tests under concurrent load:
✓ Can handle 10 simultaneous users?
✓ Response times acceptable?
✓ No memory leaks?
✓ Stable performance?

Speed: ~1 minute (configurable)
Expected: <1 sec avg response time
```

### **Phase 4: Security Tests (2 min)**
```
Tests security controls:
✓ SQL injection blocked?
✓ XSS attacks prevented?
✓ Authentication enforced?
✓ HTTPS enabled?
✓ Sensitive data protected?

Speed: ~2 minutes
Pass Rate: 100% expected
```

---

## 📊 Understanding Results

### **HTML Report**
Open `test_reports/test_report_*.html` in browser:

```
✅ PASSED (Green)
   All tests passed, system ready for production

❌ FAILED (Red)
   Fix issues before deployment

⚠️ WARNING (Yellow)
   Review warnings, may need attention

⏭️ SKIPPED (Gray)
   Test dependencies not met (normal)
```

### **JSON Report**
Machine-readable format:

```json
{
  "timestamp": "2026-03-17T14:30:22",
  "summary": {
    "total_tests": 4,
    "passed": 4,
    "failed": 0,
    "pass_rate": "100%"
  },
  "tests": {
    "unit_tests": { "status": "passed" },
    "api_tests": { "status": "passed" },
    "load_tests": { "status": "passed" },
    "security_tests": { "status": "passed" }
  }
}
```

---

## 🔧 Configuration

Edit `automated_tests.py` to customize:

```python
# Backend URL
BASE_URL = "http://localhost:8000"

# Load test parameters
LOAD_TEST_USERS = 10          # Number of simulated users
LOAD_TEST_DURATION = "1m"     # Test duration

# Timeouts
TEST_TIMEOUT = 300            # 5 minutes
```

---

## 🎯 Common Scenarios

### **Scenario 1: Quick Sanity Check**

```bash
# Just check if backend is working
python -c "
from automated_tests import TestRunner
runner = TestRunner()
runner.check_backend_running()
"
```

### **Scenario 2: Continuous Integration (CI/CD)**

```bash
# Run tests and exit with status code
python automated_tests.py
if [ $? -eq 0 ]; then
    echo "Tests passed - safe to deploy"
    exit 0
else
    echo "Tests failed - do not deploy"
    exit 1
fi
```

### **Scenario 3: Before Production Deployment**

```bash
# Run complete test suite
python automated_tests.py

# Review HTML report
open test_reports/test_report_*.html

# Check for failures
if grep -q '"failed": 0' test_reports/test_results_*.json; then
    echo "✅ Ready for production"
else
    echo "❌ Fix issues first"
    exit 1
fi
```

### **Scenario 4: Daily Regression Testing**

```bash
# Schedule with cron (macOS/Linux)
0 8 * * * cd /path/to/rag-system && python automated_tests.py >> test_reports/daily_log.txt 2>&1
```

Or Windows Task Scheduler:
```
Task: "Daily RAG Tests"
Trigger: 08:00 AM Daily
Action: python C:\path\to\automated_tests.py
```

---

## 🐛 Troubleshooting

### **Issue: Backend not running**

```
❌ Cannot connect to backend: Connection refused

Solution:
python -m uvicorn src.api.main:app --reload
```

### **Issue: Pytest not found**

```
❌ Error running unit tests: Pytest not installed

Solution:
pip install pytest
```

### **Issue: Locust not found**

```
⚠️ Locust not installed: pip install locust

Solution (optional):
pip install locust
# Or skip load tests by commenting out in automated_tests.py
```

### **Issue: Tests timeout**

```
⚠️ Unit tests timeout!

Solution:
1. Increase TEST_TIMEOUT in automated_tests.py
2. Check if backend is slow
3. Run fewer tests: pytest tests/test_rag_system.py::TestAuthentication -v
```

### **Issue: Permission denied (macOS/Linux)**

```
bash: ./run_tests.sh: Permission denied

Solution:
chmod +x run_tests.sh
./run_tests.sh
```

---

## 📈 Performance Benchmarks

Expected performance metrics:

```
Login Response:         < 2 seconds
File Upload (5MB):      < 30 seconds
Search Query:           < 5 seconds
LLM Response:           < 10 seconds
Dashboard Load:         < 3 seconds

Concurrent Users:       10 without issues
Peak Load:              50 users with scaling
Memory Usage:           < 2GB
CPU Usage:              < 80%
```

---

## ✅ Pre-Deployment Checklist

Before deploying to production:

```
□ Run: python automated_tests.py
□ All tests pass (green ✅)
□ No critical failures
□ Load tests pass
□ Security tests pass
□ Response times acceptable
□ Memory usage normal
□ Review HTML report
□ Fix any issues
□ Re-run tests
□ Document results
□ Get approval
□ Deploy! 🚀
```

---

## 📚 Additional Testing Commands

```bash
# Run specific test class
pytest tests/test_rag_system.py::TestAuthentication -v

# Run with coverage report
pytest tests/test_rag_system.py --cov=src --cov-report=html

# Run load test with custom parameters
locust -f locustfile.py \
    --host=http://localhost:8000 \
    -u 50 \           # 50 users
    -r 5 \            # 5 users per second
    -t 5m \           # 5 minutes
    --headless

# Run security tests only
python -c "
from automated_tests import TestRunner
runner = TestRunner()
runner.run_security_tests()
"
```

---

## 📧 Test Report Distribution

### **Email Report**

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

# Read HTML report
with open('test_reports/test_report_*.html', 'r') as f:
    report_html = f.read()

# Send email
# ... (email setup code)
```

### **Slack Notification**

```bash
# Send test results to Slack
curl -X POST YOUR_SLACK_WEBHOOK \
  -H 'Content-type: application/json' \
  -d '{"text":"RAG Tests: All Passed ✅"}'
```

---

## 🎓 Learning Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Locust Documentation**: https://locust.io/
- **API Testing Best Practices**: https://www.postman.com/api-platform/api-testing/
- **Security Testing**: https://owasp.org/www-project-web-security-testing-guide/

---

## 📞 Support

If tests fail:

1. **Check backend is running**: `curl http://localhost:8000/health`
2. **Review test logs**: Check terminal output
3. **View detailed report**: Open HTML report in browser
4. **Check test configuration**: Verify BASE_URL in automated_tests.py
5. **Run tests individually**: Debug one test at a time

---

## 🚀 Next Steps

1. ✅ Run: `python automated_tests.py`
2. ✅ Review: Open HTML report
3. ✅ Fix: Any failing tests
4. ✅ Deploy: When all tests pass
5. ✅ Monitor: Run tests regularly

---

**Happy Testing! 🎉**

