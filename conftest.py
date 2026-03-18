"""
RAG System v1.5 - Test Fixtures with Centralized Test Data

Pytest fixtures that provide:
- Test users (auto-registered)
- Test documents (auto-uploaded)
- Test tokens (JWT auth)
- Database cleanup

Usage in tests:
    def test_search(authenticated_user, test_document):
        # User already registered and authenticated
        # Document already uploaded
        # Just run your test!
"""

import pytest
from test_data import TestData
import requests
import json
from typing import Dict, Tuple

# ============= API FIXTURES =============

@pytest.fixture(scope="session")
def api_base_url():
    """Base API URL"""
    return "http://localhost:8000"

@pytest.fixture(scope="function")
def admin_user():
    """Get admin test user"""
    return TestData.get_test_user("admin")

@pytest.fixture(scope="function")
def editor_user():
    """Get editor test user"""
    return TestData.get_test_user("editor")

@pytest.fixture(scope="function")
def viewer_user():
    """Get viewer test user"""
    return TestData.get_test_user("viewer")

# ============= AUTHENTICATION FIXTURES =============

@pytest.fixture(scope="function")
def registered_admin(api_base_url, admin_user):
    """Register admin user and return credentials"""
    requests.post(
        f"{api_base_url}/auth/register",
        json=admin_user
    )
    return admin_user

@pytest.fixture(scope="function")
def registered_editor(api_base_url, editor_user):
    """Register editor user and return credentials"""
    requests.post(
        f"{api_base_url}/auth/register",
        json=editor_user
    )
    return editor_user

@pytest.fixture(scope="function")
def admin_token(api_base_url, registered_admin) -> str:
    """Login as admin and get JWT token"""
    response = requests.post(
        f"{api_base_url}/auth/login",
        data={
            "email": registered_admin["email"],
            "password": registered_admin["password"]
        }
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    raise Exception("Failed to get admin token")

@pytest.fixture(scope="function")
def editor_token(api_base_url, registered_editor) -> str:
    """Login as editor and get JWT token"""
    response = requests.post(
        f"{api_base_url}/auth/login",
        data={
            "email": registered_editor["email"],
            "password": registered_editor["password"]
        }
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    raise Exception("Failed to get editor token")

@pytest.fixture(scope="function")
def authenticated_admin(api_base_url, admin_token, registered_admin) -> Dict:
    """Admin user with auth token and headers"""
    return {
        "user": registered_admin,
        "token": admin_token,
        "headers": {"Authorization": f"Bearer {admin_token}"}
    }

@pytest.fixture(scope="function")
def authenticated_editor(api_base_url, editor_token, registered_editor) -> Dict:
    """Editor user with auth token and headers"""
    return {
        "user": registered_editor,
        "token": editor_token,
        "headers": {"Authorization": f"Bearer {editor_token}"}
    }

# ============= DOCUMENT FIXTURES =============

@pytest.fixture(scope="function")
def test_microsoft_document():
    """Get Microsoft test document"""
    return TestData.get_test_document("microsoft_document")

@pytest.fixture(scope="function")
def test_tech_article():
    """Get technology article"""
    return TestData.get_test_document("tech_article")

@pytest.fixture(scope="function")
def test_company_report():
    """Get company report"""
    return TestData.get_test_document("company_report")

@pytest.fixture(scope="function")
def uploaded_document(api_base_url, authenticated_editor, test_microsoft_document):
    """Upload document and return document ID"""
    doc = test_microsoft_document
    
    response = requests.post(
        f"{api_base_url}/upload",
        headers=authenticated_editor["headers"],
        files={"file": (doc["filename"], doc["content"], "application/pdf")}
    )
    
    if response.status_code == 200:
        return {
            "document_id": response.json().get("document_id"),
            "filename": doc["filename"],
            "content": doc["content"]
        }
    raise Exception(f"Failed to upload document: {response.text}")

@pytest.fixture(scope="function")
def multiple_documents(api_base_url, authenticated_editor):
    """Upload multiple test documents"""
    documents = []
    
    for doc_name, doc in TestData.get_all_test_documents().items():
        response = requests.post(
            f"{api_base_url}/upload",
            headers=authenticated_editor["headers"],
            files={"file": (doc["filename"], doc["content"], "text/plain")}
        )
        
        if response.status_code == 200:
            documents.append({
                "name": doc_name,
                "document_id": response.json().get("document_id"),
                "filename": doc["filename"]
            })
    
    return documents

# ============= QUERY FIXTURES =============

@pytest.fixture(scope="function")
def simple_query():
    """Get simple test query"""
    return TestData.get_test_query("simple_query")

@pytest.fixture(scope="function")
def specific_query():
    """Get specific test query"""
    return TestData.get_test_query("specific_query")

@pytest.fixture(scope="function")
def broad_query():
    """Get broad test query"""
    return TestData.get_test_query("broad_query")

@pytest.fixture(scope="function")
def all_test_queries():
    """Get all test queries"""
    return TestData.get_all_test_queries()

# ============= SECURITY TEST FIXTURES =============

@pytest.fixture(scope="function")
def sql_injection_payload():
    """Get SQL injection test case"""
    return TestData.get_security_test_case("sql_injection_email")

@pytest.fixture(scope="function")
def xss_payload():
    """Get XSS test case"""
    return TestData.get_security_test_case("xss_search")

@pytest.fixture(scope="function")
def all_security_payloads():
    """Get all security test cases"""
    return TestData.get_all_security_cases()

# ============= LOAD TEST FIXTURES =============

@pytest.fixture(scope="function")
def light_load_scenario():
    """Get light load test scenario"""
    return TestData.get_load_scenario("light_load")

@pytest.fixture(scope="function")
def medium_load_scenario():
    """Get medium load test scenario"""
    return TestData.get_load_scenario("medium_load")

@pytest.fixture(scope="function")
def heavy_load_scenario():
    """Get heavy load test scenario"""
    return TestData.get_load_scenario("heavy_load")

# ============= API ENDPOINT FIXTURES =============

@pytest.fixture(scope="function")
def health_endpoint():
    """Get health endpoint test data"""
    return TestData.get_api_endpoint("health")

@pytest.fixture(scope="function")
def register_endpoint():
    """Get register endpoint test data"""
    return TestData.get_api_endpoint("register")

@pytest.fixture(scope="function")
def login_endpoint():
    """Get login endpoint test data"""
    return TestData.get_api_endpoint("login")

@pytest.fixture(scope="function")
def upload_endpoint():
    """Get upload endpoint test data"""
    return TestData.get_api_endpoint("upload")

@pytest.fixture(scope="function")
def query_endpoint():
    """Get query endpoint test data"""
    return TestData.get_api_endpoint("query")

# ============= DATABASE FIXTURES =============

@pytest.fixture(scope="function", autouse=True)
def cleanup_after_test(api_base_url):
    """Cleanup after each test"""
    yield
    # Add cleanup logic here if needed
    # Examples:
    # - Delete test users
    # - Delete test documents
    # - Clear cache
    # - Reset database state

# ============= COMBINED FIXTURES =============

@pytest.fixture(scope="function")
def ready_to_search(api_base_url, authenticated_editor, uploaded_document, simple_query):
    """Everything ready for a search test"""
    return {
        "user": authenticated_editor,
        "document": uploaded_document,
        "query": simple_query
    }

@pytest.fixture(scope="function")
def full_test_environment(api_base_url, authenticated_admin, authenticated_editor, multiple_documents):
    """Complete test environment with users and documents"""
    return {
        "admin": authenticated_admin,
        "editor": authenticated_editor,
        "documents": multiple_documents,
        "base_url": api_base_url
    }

# ============= SAMPLE USAGE =============

if __name__ == "__main__":
    print("Test Fixtures Available:")
    print()
    print("Authentication Fixtures:")
    print("  - admin_token: JWT token for admin")
    print("  - editor_token: JWT token for editor")
    print("  - authenticated_admin: Admin user + token + headers")
    print("  - authenticated_editor: Editor user + token + headers")
    print()
    print("Document Fixtures:")
    print("  - test_microsoft_document: Microsoft document data")
    print("  - test_tech_article: Tech article data")
    print("  - uploaded_document: Already uploaded document")
    print("  - multiple_documents: Multiple uploaded documents")
    print()
    print("Query Fixtures:")
    print("  - simple_query: Simple search query")
    print("  - all_test_queries: All test queries")
    print()
    print("Security Fixtures:")
    print("  - sql_injection_payload: SQL injection test case")
    print("  - xss_payload: XSS test case")
    print("  - all_security_payloads: All security cases")
    print()
    print("Ready-to-use Fixtures:")
    print("  - ready_to_search: User + document + query")
    print("  - full_test_environment: Admin + editor + documents")
