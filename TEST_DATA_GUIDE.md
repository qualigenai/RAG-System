# RAG System v1.5 - Test Data Management Guide

Complete guide for professional test data management

---

## 🎯 Overview

```
Test Data Architecture:

test_data.py (Centralized Data)
    ↓
conftest.py (Pytest Fixtures)
    ↓
test_with_data.py (Tests Using Data)
    ↓
seed_database.py (Database Seeding)
    ↓
automated_tests.py (Automation)
```

---

## 📦 What's Included

### **1. test_data.py**
```
Centralized test data containing:
✓ 4 test users (admin, editor, viewer, new_user)
✓ 5 invalid user scenarios (for negative testing)
✓ 4 test documents (PDF, TXT with real content)
✓ 4 invalid documents (for security testing)
✓ 6 search queries (various scenarios)
✓ 6 security test cases (SQL injection, XSS, etc.)
✓ 4 load test scenarios
✓ 7 API endpoint configurations

Total: 40+ test data scenarios!
```

### **2. conftest.py**
```
Pytest fixtures that use test data:
✓ User fixtures (admin, editor, viewer)
✓ Authentication fixtures (tokens, headers)
✓ Document fixtures (upload, multiple)
✓ Query fixtures (all test queries)
✓ Security fixtures (payloads, cases)
✓ Load test fixtures
✓ Combined fixtures (ready-to-use)

Auto-used by pytest - no manual setup needed!
```

### **3. test_with_data.py**
```
Professional test cases using data:
✓ Authentication tests (register, login)
✓ Document upload tests
✓ Search/query tests
✓ Security tests
✓ Role-based access tests
✓ Data integrity tests
✓ Parametrized tests (all scenarios)

100+ test cases automated!
```

### **4. seed_database.py**
```
Database population script:
✓ Creates test users
✓ Uploads test documents
✓ Verifies data integrity
✓ Exports results
✓ Supports cleanup

Prepare database before test run!
```

---

## 🚀 Quick Start

### **Step 1: Copy Files to Project**

```
C:\Users\Rambhupal\rag-system\
├── test_data.py           ← NEW
├── conftest.py            ← NEW (copy to root or tests/)
├── tests/
│   ├── test_with_data.py  ← NEW
│   └── test_rag_system.py ← (existing)
├── seed_database.py       ← NEW
└── ... (other files)
```

### **Step 2: Install Dependencies**

```bash
pip install -r requirements-test.txt
```

### **Step 3: Seed Database**

```bash
python seed_database.py
```

Output:
```
✅ Backend is running
📝 Seeding Test Users...
✅ ADMIN: admin@rag-test.com
✅ EDITOR: editor@rag-test.com
✅ VIEWER: viewer@rag-test.com
📄 Seeding Test Documents...
✅ microsoft_document: Microsoft.pdf
✅ tech_article: Technology_Trends_2026.txt
✅ company_report: Annual_Report_2025.txt
✓ Verification complete
```

### **Step 4: Run Tests**

```bash
# Run all tests with data
pytest test_with_data.py -v

# Run specific test class
pytest test_with_data.py::TestAuthenticationWithData -v

# Run with test data coverage
pytest test_with_data.py --cov=test_data --cov-report=html
```

---

## 📋 Test Data Structure

### **User Test Data**

```python
# From test_data.py

TEST_USERS = {
    "admin": {
        "email": "admin@rag-test.com",
        "username": "admin_test",
        "password": "AdminPassword123!",
        "full_name": "Admin Test User",
        "role": "admin",
        "organization": "Test Organization"
    },
    "editor": { ... },
    "viewer": { ... },
    "new_user": { ... }
}

# Usage in tests
admin = TestData.get_test_user("admin")
all_users = TestData.get_all_test_users()
```

### **Document Test Data**

```python
TEST_DOCUMENTS = {
    "microsoft_document": {
        "filename": "Microsoft.pdf",
        "content": b"...",  # Real document content
        "type": "pdf",
        "size_kb": 100,
        "expected_chunks": 5,
        "key_terms": ["Microsoft", "Bill Gates", ...]
    },
    "tech_article": { ... },
    "company_report": { ... },
    "large_document": { ... }
}

# Usage in tests
doc = TestData.get_test_document("microsoft_document")
```

### **Query Test Data**

```python
TEST_QUERIES = {
    "simple_query": {
        "query": "What is Microsoft?",
        "document_needed": "microsoft_document",
        "expected_keywords": ["Microsoft", "corporation", ...],
        "should_find_results": True,
        "min_relevance": 0.8
    },
    "specific_query": { ... },
    "broad_query": { ... }
}

# Usage in tests
query = TestData.get_test_query("simple_query")
all_queries = TestData.get_all_test_queries()
```

### **Security Test Data**

```python
SECURITY_TEST_CASES = {
    "sql_injection_email": {
        "email": "admin' OR '1'='1",
        "password": "anything",
        "attack_type": "SQL Injection",
        "should_block": True
    },
    "xss_search": {
        "query": "<script>alert('xss')</script>",
        "attack_type": "XSS",
        "should_block": True
    },
    ...
}

# Usage in tests
attack = TestData.get_security_test_case("sql_injection_email")
```

---

## 🔧 Using Test Data in Tests

### **Example 1: Using Test User**

```python
def test_login(self, api_base_url):
    """Test login with test user"""
    import requests
    
    # Get test user data
    user = TestData.get_test_user("editor")
    
    # Login
    response = requests.post(
        f"{api_base_url}/auth/login",
        data={
            "email": user["email"],
            "password": user["password"]
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### **Example 2: Using Fixtures**

```python
def test_search(self, authenticated_editor, uploaded_document, simple_query):
    """Test search using fixtures"""
    import requests
    
    # All data prepared by fixtures!
    response = requests.post(
        f"{authenticated_editor['headers']}",
        data={"query_text": simple_query["query"]}
    )
    
    assert response.status_code == 200
```

### **Example 3: Parametrized Test with Data**

```python
@pytest.mark.parametrize("query_type", TestData.get_all_test_queries().keys())
def test_all_queries(api_base_url, authenticated_editor, query_type):
    """Test all queries from test data"""
    import requests
    
    query = TestData.get_test_query(query_type)
    
    response = requests.post(
        f"{api_base_url}/query",
        headers=authenticated_editor["headers"],
        data={"query_text": query["query"]}
    )
    
    assert response.status_code == 200
```

---

## 🌱 Database Seeding

### **Automatic Seeding**

```bash
# Seed with all data
python seed_database.py

# Seed without documents (faster)
python seed_database.py --no-documents

# Seed and export results
python seed_database.py --export

# Clean and reseed
python seed_database.py --clean
```

### **Manual Seeding in Python**

```python
from seed_database import DatabaseSeeder

# Create seeder
seeder = DatabaseSeeder(base_url="http://localhost:8000")

# Run seeding
success = seeder.run(
    seed_documents=True,
    verify=True,
    export_results=True
)

# Print results
if success:
    print("✅ Database seeded successfully!")
else:
    print("❌ Some errors occurred")
```

### **Seeding Output**

```
🌱 DATABASE SEEDING STARTED
==================================================
✅ Backend is running
📝 Seeding Test Users...
--------------------------------------------------
✅ ADMIN: admin@rag-test.com
✅ EDITOR: editor@rag-test.com
✅ VIEWER: viewer@rag-test.com
✅ NEW_USER: newuser_1710720123.321@rag-test.com
✓ Users seeded: 4

📄 Seeding Test Documents...
--------------------------------------------------
✅ microsoft_document: Microsoft.pdf
✅ tech_article: Technology_Trends_2026.txt
✅ company_report: Annual_Report_2025.txt
✅ large_document: Large_Document.txt
✓ Documents uploaded: 4

✔️ Verifying Seeded Data...
--------------------------------------------------
✅ Documents in system: 4
✅ Team members: 4
✓ Verification complete

==================================================
DATABASE SEEDING SUMMARY
==================================================
✅ Users created: 4
✅ Documents uploaded: 4
✅ No errors
==================================================
```

---

## 📊 Test Data Statistics

```
Users:
  - Admin (full access)
  - Editor (upload, delete own)
  - Viewer (search only)
  - New User (to test onboarding)
  Total: 4 users

Documents:
  - Microsoft PDF (real company info)
  - Technology Article (TXT format)
  - Company Report (annual report)
  - Large Document (testing limits)
  Total: 4 documents

Queries:
  - Simple question
  - Specific question
  - Broad search
  - Financial query
  - No results query
  - Special characters query
  Total: 6 queries

Security Tests:
  - SQL Injection (email)
  - SQL Injection (password)
  - XSS (search)
  - XSS (image tag)
  - Path Traversal
  - Command Injection
  Total: 6 attacks

Load Scenarios:
  - Light (5 users)
  - Medium (10 users)
  - Heavy (50 users)
  - Stress (100 users)
  Total: 4 scenarios
```

---

## 🔍 Viewing Test Data

### **Python Script**

```python
from test_data import TestData

# Export all test data
filename = TestData.export_test_data("my_test_data.json")
print(f"Test data exported to: {filename}")
```

### **Command Line**

```bash
# List all test users
python -c "from test_data import TestData; import json; print(json.dumps(TestData.TEST_USERS, indent=2))"

# List all test documents
python -c "from test_data import TestData; import json; print(json.dumps({k: {**v, 'content': '...'} for k,v in TestData.TEST_DOCUMENTS.items()}, indent=2))"

# List all test queries
python -c "from test_data import TestData; import json; print(json.dumps(TestData.TEST_QUERIES, indent=2))"
```

---

## 🎯 Test Coverage with Test Data

```
Authentication:
  ✅ Valid registration (4 users)
  ✅ Invalid registration (5 scenarios)
  ✅ Valid login
  ✅ Invalid login
  ✅ Token management

Documents:
  ✅ Upload valid files (4 documents)
  ✅ Upload invalid files (5 scenarios)
  ✅ Large file handling
  ✅ Different formats

Search:
  ✅ Simple queries
  ✅ Specific queries
  ✅ Broad searches
  ✅ No results

Security:
  ✅ SQL Injection (2 vectors)
  ✅ XSS (2 vectors)
  ✅ Path Traversal
  ✅ Command Injection

Performance:
  ✅ Light load (5 users)
  ✅ Medium load (10 users)
  ✅ Heavy load (50 users)
  ✅ Stress test (100 users)
```

---

## 📈 Benefits of Centralized Test Data

### **Before (Manual)**

```
❌ Test data scattered in test files
❌ Hard to maintain
❌ Difficult to update
❌ Inconsistent test data
❌ No reusability
❌ Manual test setup
```

### **After (Centralized)**

```
✅ All test data in one place
✅ Easy to maintain
✅ Quick to update
✅ Consistent across tests
✅ Highly reusable
✅ Automated setup with fixtures
```

---

## 💡 Advanced Usage

### **Custom Test Data**

```python
# Add custom test data
class MyTestData:
    """Custom test data"""
    
    CUSTOM_USERS = {
        "power_user": {
            "email": "power@test.com",
            "password": "PowerUser123!",
            ...
        }
    }
    
    @classmethod
    def get_power_user(cls):
        return cls.CUSTOM_USERS["power_user"]

# Use in tests
user = MyTestData.get_power_user()
```

### **Data-Driven Testing**

```python
# Test all scenarios with same test
scenarios = [
    ("simple", "What is X?", True),
    ("complex", "Tell me about X", True),
    ("empty", "Unrelated topic", False)
]

for scenario_name, query, should_find in scenarios:
    # Run same test with different data
    test_search(scenario_name, query, should_find)
```

### **Test Data Validation**

```python
# Validate test data format
def validate_test_data():
    """Ensure test data is properly formatted"""
    
    for user_name, user_data in TestData.TEST_USERS.items():
        assert "email" in user_data
        assert "@" in user_data["email"]
        assert len(user_data["password"]) >= 8
    
    for doc_name, doc_data in TestData.TEST_DOCUMENTS.items():
        assert "filename" in doc_data
        assert "content" in doc_data
        assert isinstance(doc_data["content"], bytes)
```

---

## 🐛 Troubleshooting

### **Issue: Test data not found**

```
Error: AttributeError: TestData has no attribute 'get_test_user'

Solution:
✅ Make sure test_data.py is in Python path
✅ Place test_data.py in project root
✅ Add to PYTHONPATH if needed
```

### **Issue: Fixture not available**

```
Error: fixture 'authenticated_editor' not found

Solution:
✅ Copy conftest.py to tests/ directory
✅ Or place in project root
✅ pytest automatically discovers conftest.py
```

### **Issue: Database seeding fails**

```
Error: Cannot connect to backend

Solution:
✅ Start backend: python -m uvicorn src.api.main:app --reload
✅ Verify URL: http://localhost:8000/health
✅ Check CORS settings in FastAPI
```

---

## 📚 Best Practices

```
✅ Keep test data in one place (test_data.py)
✅ Use fixtures for common setup
✅ Parametrize tests with test data
✅ Seed database before test suite
✅ Clean up after tests (optional)
✅ Export test results for audit
✅ Version control test data changes
✅ Document test data requirements
```

---

## 🎓 Complete Example Workflow

```python
# 1. Get test user
user = TestData.get_test_user("admin")

# 2. Register user (in test fixture)
requests.post(f"{api_url}/auth/register", json=user)

# 3. Login user (in test fixture)
response = requests.post(f"{api_url}/auth/login", data=user)
token = response.json()["access_token"]

# 4. Get test document
doc = TestData.get_test_document("microsoft_document")

# 5. Upload document
requests.post(
    f"{api_url}/upload",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": (doc["filename"], doc["content"])}
)

# 6. Execute test query
query = TestData.get_test_query("simple_query")
response = requests.post(
    f"{api_url}/query",
    headers={"Authorization": f"Bearer {token}"},
    data={"query_text": query["query"]}
)

# 7. Verify results
assert response.status_code == 200
assert "answer" in response.json()
```

---

## 🚀 Next Steps

1. ✅ Copy all test data files to project
2. ✅ Install dependencies: `pip install -r requirements-test.txt`
3. ✅ Seed database: `python seed_database.py`
4. ✅ Run tests: `pytest test_with_data.py -v`
5. ✅ View results: Check pytest output
6. ✅ Extend data: Add custom test scenarios as needed

---

**Professional Test Data Management Complete!** 🎉

All tests now use centralized, reusable, well-organized test data! 💪

