"""
RAG System v1.5 - Test Data Management

Centralized test data for all automation scenarios
- User credentials
- Document samples
- Test queries
- Expected results

Usage:
    from test_data import TestData
    user = TestData.get_test_user()
"""

import json
from typing import Dict, List
from datetime import datetime

class TestData:
    """Centralized test data for automation"""
    
    # ============= USER TEST DATA =============
    
    TEST_USERS = {
        "admin": {
            "email": "admin@rag-test.com",
            "username": "admin_test",
            "password": "AdminPassword123!",
            "full_name": "Admin Test User",
            "role": "admin",
            "organization": "Test Organization"
        },
        "editor": {
            "email": "editor@rag-test.com",
            "username": "editor_test",
            "password": "EditorPassword123!",
            "full_name": "Editor Test User",
            "role": "editor",
            "organization": "Test Organization"
        },
        "viewer": {
            "email": "viewer@rag-test.com",
            "username": "viewer_test",
            "password": "ViewerPassword123!",
            "full_name": "Viewer Test User",
            "role": "viewer",
            "organization": "Test Organization"
        },
        "new_user": {
            "email": f"newuser_{datetime.now().timestamp()}@rag-test.com",
            "username": "new_user_test",
            "password": "NewUserPassword123!",
            "full_name": "New User Test",
            "role": "editor",
            "organization": "Test Organization"
        }
    }
    
    # ============= INVALID USER DATA (Security Testing) =============
    
    INVALID_USERS = {
        "weak_password": {
            "email": "weak@rag-test.com",
            "username": "weak_user",
            "password": "123",  # Too short
            "full_name": "Weak Password User",
            "error": "Password must be at least 8 characters"
        },
        "no_special_char": {
            "email": "nospecial@rag-test.com",
            "username": "nospecial_user",
            "password": "Password123",  # Missing special char
            "full_name": "No Special Char",
            "error": "Password must contain special characters"
        },
        "duplicate_email": {
            "email": "admin@rag-test.com",  # Already exists
            "username": "duplicate",
            "password": "DuplicatePass123!",
            "full_name": "Duplicate Email",
            "error": "Email already registered"
        },
        "sql_injection_email": {
            "email": "admin' OR '1'='1",
            "username": "sqli",
            "password": "SQLInjection123!",
            "full_name": "SQL Injection",
            "error": "Invalid email format"
        },
        "xss_username": {
            "email": "xss@rag-test.com",
            "username": "<script>alert('xss')</script>",
            "password": "XSSTest123!",
            "full_name": "XSS Test",
            "error": "Invalid username format"
        }
    }
    
    # ============= DOCUMENT TEST DATA =============
    
    TEST_DOCUMENTS = {
        "microsoft_document": {
            "filename": "Microsoft.pdf",
            "content": b"""
Microsoft Corporation
Microsoft is an American technology corporation which develops, manufactures, licenses, supports and sells computer software, consumer electronics, personal computers, and services.

Founded: April 4, 1975
Headquarters: Redmond, Washington
CEO: Satya Nadella
Stock Symbol: MSFT (NASDAQ)
Employees: 221,000+

Products:
- Windows Operating System
- Microsoft Office
- Azure Cloud Services
- Xbox Gaming
- Surface Devices

History:
Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975, in Albuquerque, New Mexico.
The company went public in 1986 with an IPO at $21 per share.
""",
            "type": "pdf",
            "size_kb": 100,
            "expected_chunks": 5,
            "key_terms": ["Microsoft", "Bill Gates", "Windows", "Azure", "Nasdaq"]
        },
        "tech_article": {
            "filename": "Technology_Trends_2026.txt",
            "content": b"""
Technology Trends in 2026

1. Artificial Intelligence
   - Large Language Models (LLMs)
   - Generative AI
   - AI-powered automation
   
2. Cloud Computing
   - Multi-cloud strategies
   - Edge computing
   - Serverless architecture
   
3. Cybersecurity
   - Zero-trust security
   - AI-powered threat detection
   - Quantum-resistant encryption
   
4. Data Engineering
   - Real-time analytics
   - Data lakes
   - Data governance
   
5. Developer Tools
   - Low-code platforms
   - DevOps automation
   - API-first architecture
""",
            "type": "txt",
            "size_kb": 5,
            "expected_chunks": 3,
            "key_terms": ["AI", "Cloud", "Security", "Data", "Developer"]
        },
        "company_report": {
            "filename": "Annual_Report_2025.txt",
            "content": b"""
Annual Report 2025

Financial Performance:
Revenue: $500 million
Profit: $150 million
Year-over-Year Growth: 25%

Department Performance:
- Sales: +30%
- Engineering: +20%
- Operations: +15%

Key Achievements:
1. Launched new product line
2. Expanded to 5 new markets
3. Increased customer satisfaction by 40%
4. Reduced operational costs by 20%

Future Plans:
- Global expansion
- AI integration
- Sustainability initiatives
""",
            "type": "txt",
            "size_kb": 3,
            "expected_chunks": 2,
            "key_terms": ["Revenue", "Growth", "Performance", "Product", "Market"]
        },
        "large_document": {
            "filename": "Large_Document.txt",
            "content": b"Sample content for large file testing. " * 5000,  # Large file
            "type": "txt",
            "size_kb": 200,
            "expected_chunks": 20,
            "key_terms": ["Sample", "content", "testing"]
        }
    }
    
    # ============= INVALID DOCUMENTS (Security Testing) =============
    
    INVALID_DOCUMENTS = {
        "empty_file": {
            "filename": "empty.txt",
            "content": b"",
            "error": "File is empty",
            "should_upload": False
        },
        "oversized_file": {
            "filename": "oversized.bin",
            "content": b"X" * (300 * 1024 * 1024),  # 300MB
            "error": "File exceeds 200MB limit",
            "should_upload": False
        },
        "unsupported_format": {
            "filename": "malicious.exe",
            "content": b"MZ\x90\x00",  # PE executable header
            "error": "Unsupported file format",
            "should_upload": False
        },
        "corrupted_pdf": {
            "filename": "corrupted.pdf",
            "content": b"Not a real PDF file but pretending to be",
            "error": "Could not extract PDF text",
            "should_upload": False
        },
        "xss_filename": {
            "filename": "<script>alert('xss')</script>.txt",
            "content": b"Test content",
            "error": "Invalid filename",
            "should_upload": False
        }
    }
    
    # ============= SEARCH TEST DATA =============
    
    TEST_QUERIES = {
        "simple_query": {
            "query": "What is Microsoft?",
            "document_needed": "microsoft_document",
            "expected_keywords": ["Microsoft", "corporation", "technology"],
            "should_find_results": True,
            "min_relevance": 0.8
        },
        "specific_query": {
            "query": "When was Microsoft founded?",
            "document_needed": "microsoft_document",
            "expected_keywords": ["1975", "April", "founded"],
            "should_find_results": True,
            "min_relevance": 0.85
        },
        "broad_query": {
            "query": "Tell me about technology trends",
            "document_needed": "tech_article",
            "expected_keywords": ["AI", "Cloud", "technology"],
            "should_find_results": True,
            "min_relevance": 0.7
        },
        "financial_query": {
            "query": "What was the revenue in 2025?",
            "document_needed": "company_report",
            "expected_keywords": ["revenue", "500", "million"],
            "should_find_results": True,
            "min_relevance": 0.85
        },
        "no_results_query": {
            "query": "Dinosaurs and ancient history",
            "document_needed": "microsoft_document",
            "expected_keywords": [],
            "should_find_results": False,
            "min_relevance": 0.0
        },
        "special_chars_query": {
            "query": "What is C++?",
            "document_needed": None,
            "expected_keywords": [],
            "should_find_results": False,
            "min_relevance": 0.0
        }
    }
    
    # ============= SECURITY TEST DATA =============
    
    SECURITY_TEST_CASES = {
        "sql_injection_email": {
            "email": "admin' OR '1'='1",
            "password": "anything",
            "attack_type": "SQL Injection",
            "should_block": True
        },
        "sql_injection_password": {
            "email": "test@test.com",
            "password": "' OR '1'='1",
            "attack_type": "SQL Injection",
            "should_block": True
        },
        "xss_search": {
            "query": "<script>alert('xss')</script>",
            "attack_type": "XSS",
            "should_block": True
        },
        "xss_img_tag": {
            "query": "<img src=x onerror=alert('xss')>",
            "attack_type": "XSS",
            "should_block": True
        },
        "path_traversal": {
            "path": "../../../etc/passwd",
            "attack_type": "Path Traversal",
            "should_block": True
        },
        "command_injection": {
            "command": "; rm -rf /",
            "attack_type": "Command Injection",
            "should_block": True
        }
    }
    
    # ============= LOAD TEST DATA =============
    
    LOAD_TEST_SCENARIOS = {
        "light_load": {
            "users": 5,
            "ramp_up_rate": 1,
            "duration": "30s",
            "expected_response_time": "< 1s",
            "expected_success_rate": "100%"
        },
        "medium_load": {
            "users": 10,
            "ramp_up_rate": 2,
            "duration": "1m",
            "expected_response_time": "< 2s",
            "expected_success_rate": "99%"
        },
        "heavy_load": {
            "users": 50,
            "ramp_up_rate": 5,
            "duration": "2m",
            "expected_response_time": "< 5s",
            "expected_success_rate": "95%"
        },
        "stress_test": {
            "users": 100,
            "ramp_up_rate": 10,
            "duration": "3m",
            "expected_response_time": "< 10s",
            "expected_success_rate": "90%"
        }
    }
    
    # ============= API TEST DATA =============
    
    API_TEST_ENDPOINTS = {
        "health": {
            "method": "GET",
            "path": "/health",
            "requires_auth": False,
            "expected_status": 200,
            "expected_response": {
                "status": "healthy",
                "version": "1.5"
            }
        },
        "register": {
            "method": "POST",
            "path": "/auth/register",
            "requires_auth": False,
            "expected_status": 200,
            "request_body": {
                "email": "test@test.com",
                "username": "testuser",
                "password": "Password123!",
                "full_name": "Test User"
            }
        },
        "login": {
            "method": "POST",
            "path": "/auth/login",
            "requires_auth": False,
            "expected_status": 200,
            "request_body": {
                "email": "test@test.com",
                "password": "Password123!"
            }
        },
        "upload": {
            "method": "POST",
            "path": "/upload",
            "requires_auth": True,
            "expected_status": 200,
            "expected_response_fields": ["document_id", "filename", "size"]
        },
        "query": {
            "method": "POST",
            "path": "/query",
            "requires_auth": True,
            "expected_status": 200,
            "request_body": {
                "query_text": "Test query"
            },
            "expected_response_fields": ["query", "answer", "sources"]
        },
        "stats": {
            "method": "GET",
            "path": "/api/stats",
            "requires_auth": True,
            "expected_status": 200,
            "expected_response_fields": ["team_members", "total_documents", "queries_today"]
        }
    }
    
    # ============= TEST DATA GETTERS =============
    
    @classmethod
    def get_test_user(cls, role="editor"):
        """Get test user by role"""
        return cls.TEST_USERS.get(role, cls.TEST_USERS["editor"])
    
    @classmethod
    def get_all_test_users(cls):
        """Get all test users"""
        return cls.TEST_USERS
    
    @classmethod
    def get_invalid_user(cls, type_="weak_password"):
        """Get invalid user for negative testing"""
        return cls.INVALID_USERS.get(type_, cls.INVALID_USERS["weak_password"])
    
    @classmethod
    def get_test_document(cls, doc_type="microsoft_document"):
        """Get test document"""
        return cls.TEST_DOCUMENTS.get(doc_type, cls.TEST_DOCUMENTS["microsoft_document"])
    
    @classmethod
    def get_all_test_documents(cls):
        """Get all test documents"""
        return cls.TEST_DOCUMENTS
    
    @classmethod
    def get_invalid_document(cls, doc_type="empty_file"):
        """Get invalid document for negative testing"""
        return cls.INVALID_DOCUMENTS.get(doc_type, cls.INVALID_DOCUMENTS["empty_file"])
    
    @classmethod
    def get_test_query(cls, query_type="simple_query"):
        """Get test query"""
        return cls.TEST_QUERIES.get(query_type, cls.TEST_QUERIES["simple_query"])
    
    @classmethod
    def get_all_test_queries(cls):
        """Get all test queries"""
        return cls.TEST_QUERIES
    
    @classmethod
    def get_security_test_case(cls, attack_type="sql_injection_email"):
        """Get security test case"""
        return cls.SECURITY_TEST_CASES.get(attack_type, cls.SECURITY_TEST_CASES["sql_injection_email"])
    
    @classmethod
    def get_all_security_cases(cls):
        """Get all security test cases"""
        return cls.SECURITY_TEST_CASES
    
    @classmethod
    def get_load_scenario(cls, scenario="medium_load"):
        """Get load test scenario"""
        return cls.LOAD_TEST_SCENARIOS.get(scenario, cls.LOAD_TEST_SCENARIOS["medium_load"])
    
    @classmethod
    def get_api_endpoint(cls, endpoint="health"):
        """Get API endpoint test data"""
        return cls.API_TEST_ENDPOINTS.get(endpoint, cls.API_TEST_ENDPOINTS["health"])
    
    @classmethod
    def export_test_data(cls, filename="test_data_export.json"):
        """Export all test data to JSON file"""
        data = {
            "users": cls.TEST_USERS,
            "invalid_users": cls.INVALID_USERS,
            "documents": {
                k: {**v, "content": "...binary..."}
                for k, v in cls.TEST_DOCUMENTS.items()
            },
            "queries": cls.TEST_QUERIES,
            "security_cases": cls.SECURITY_TEST_CASES,
            "load_scenarios": cls.LOAD_TEST_SCENARIOS,
            "api_endpoints": cls.API_TEST_ENDPOINTS
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename


# ============= SAMPLE USAGE =============

if __name__ == "__main__":
    print("RAG System Test Data Management")
    print("=" * 50)
    print()
    
    # Get users
    print("Test Users Available:")
    for role, user in TestData.get_all_test_users().items():
        print(f"  {role}: {user['email']}")
    print()
    
    # Get documents
    print("Test Documents Available:")
    for doc_type, doc in TestData.get_all_test_documents().items():
        print(f"  {doc_type}: {doc['filename']}")
    print()
    
    # Get queries
    print("Test Queries Available:")
    for query_type, query in TestData.get_all_test_queries().items():
        print(f"  {query_type}: {query['query']}")
    print()
    
    # Get security cases
    print("Security Test Cases:")
    for case_type, case in TestData.get_all_security_cases().items():
        print(f"  {case_type}: {case['attack_type']}")
    print()
    
    # Export test data
    filename = TestData.export_test_data()
    print(f"Test data exported to: {filename}")
