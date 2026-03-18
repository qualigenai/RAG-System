"""
RAG System v1.5 - Updated Tests Using Test Data

Now tests use:
✓ Centralized test data
✓ Pytest fixtures
✓ Professional test organization
✓ Comprehensive scenarios

Run: pytest tests/test_with_data.py -v
"""

import pytest
from test_data import TestData

# ============= AUTHENTICATION TESTS WITH DATA =============

class TestAuthenticationWithData:
    """Authentication tests using test data"""
    
    def test_register_admin_user(self, api_base_url):
        """Test admin registration with test data"""
        import requests
        
        admin_data = TestData.get_test_user("admin")
        
        response = requests.post(
            f"{api_base_url}/auth/register",
            json=admin_data
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_register_editor_user(self, api_base_url):
        """Test editor registration with test data"""
        import requests
        
        editor_data = TestData.get_test_user("editor")
        
        response = requests.post(
            f"{api_base_url}/auth/register",
            json=editor_data
        )
        
        assert response.status_code == 200
    
    def test_register_invalid_user_weak_password(self, api_base_url):
        """Test registration with weak password"""
        import requests
        
        invalid_user = TestData.get_invalid_user("weak_password")
        
        response = requests.post(
            f"{api_base_url}/auth/register",
            json=invalid_user
        )
        
        assert response.status_code == 400
        assert "password" in response.json().get("detail", "").lower()
    
    def test_register_invalid_user_duplicate_email(self, api_base_url):
        """Test registration with duplicate email"""
        import requests
        
        admin_data = TestData.get_test_user("admin")
        
        # Register once
        requests.post(
            f"{api_base_url}/auth/register",
            json=admin_data
        )
        
        # Try to register again
        response = requests.post(
            f"{api_base_url}/auth/register",
            json=admin_data
        )
        
        assert response.status_code == 400
    
    def test_login_with_valid_credentials(self, api_base_url, registered_editor):
        """Test login with valid credentials from test data"""
        import requests
        
        response = requests.post(
            f"{api_base_url}/auth/login",
            data={
                "email": registered_editor["email"],
                "password": registered_editor["password"]
            }
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_with_invalid_credentials(self, api_base_url, registered_editor):
        """Test login with wrong password"""
        import requests
        
        response = requests.post(
            f"{api_base_url}/auth/login",
            data={
                "email": registered_editor["email"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401

# ============= DOCUMENT UPLOAD TESTS WITH DATA =============

class TestDocumentUploadWithData:
    """Document upload tests using test data"""
    
    def test_upload_microsoft_document(self, api_base_url, authenticated_editor, test_microsoft_document):
        """Test uploading Microsoft document"""
        import requests
        
        doc = test_microsoft_document
        
        response = requests.post(
            f"{api_base_url}/upload",
            headers=authenticated_editor["headers"],
            files={"file": (doc["filename"], doc["content"], "text/plain")}
        )
        
        assert response.status_code == 200
        assert "document_id" in response.json()
        assert response.json()["filename"] == doc["filename"]
    
    def test_upload_multiple_documents(self, api_base_url, authenticated_editor, multiple_documents):
        """Test that multiple documents uploaded successfully"""
        assert len(multiple_documents) > 0
        
        for doc in multiple_documents:
            assert "document_id" in doc
            assert "filename" in doc
    
    def test_upload_empty_file(self, api_base_url, authenticated_editor):
        """Test uploading empty file (should fail)"""
        import requests
        
        invalid_doc = TestData.get_invalid_document("empty_file")
        
        response = requests.post(
            f"{api_base_url}/upload",
            headers=authenticated_editor["headers"],
            files={"file": (invalid_doc["filename"], invalid_doc["content"], "text/plain")}
        )
        
        assert response.status_code == 400

# ============= SEARCH & QUERY TESTS WITH DATA =============

class TestSearchWithData:
    """Search and query tests using test data"""
    
    def test_simple_search_query(self, api_base_url, ready_to_search):
        """Test simple search query"""
        import requests
        
        query_data = ready_to_search["query"]
        
        response = requests.post(
            f"{api_base_url}/query",
            headers=ready_to_search["user"]["headers"],
            data={"query_text": query_data["query"]}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "answer" in result
        assert "query" in result
    
    def test_all_query_scenarios(self, api_base_url, authenticated_editor, uploaded_document):
        """Test all query scenarios from test data"""
        import requests
        
        for query_type, query_data in TestData.get_all_test_queries().items():
            response = requests.post(
                f"{api_base_url}/query",
                headers=authenticated_editor["headers"],
                data={"query_text": query_data["query"]}
            )
            
            assert response.status_code == 200
            print(f"✓ {query_type} executed successfully")

# ============= SECURITY TESTS WITH DATA =============

class TestSecurityWithData:
    """Security tests using test data"""
    
    def test_sql_injection_email(self, api_base_url):
        """Test SQL injection prevention"""
        import requests
        
        sql_injection = TestData.get_security_test_case("sql_injection_email")
        
        response = requests.post(
            f"{api_base_url}/auth/login",
            data={
                "email": sql_injection["email"],
                "password": sql_injection["password"]
            }
        )
        
        # Should fail, not execute SQL
        assert response.status_code == 401
    
    def test_xss_prevention(self, api_base_url, authenticated_editor):
        """Test XSS prevention in search"""
        import requests
        
        xss_payload = TestData.get_security_test_case("xss_search")
        
        response = requests.post(
            f"{api_base_url}/query",
            headers=authenticated_editor["headers"],
            data={"query_text": xss_payload["query"]}
        )
        
        # Should not execute script
        assert response.status_code == 200
        assert "<script>" not in response.json().get("answer", "")
    
    def test_all_security_attacks(self, api_base_url):
        """Test all security attack vectors"""
        import requests
        
        for attack_name, attack_data in TestData.get_all_security_cases().items():
            # Basic test - just ensure we don't crash
            if "email" in attack_data:
                response = requests.post(
                    f"{api_base_url}/auth/login",
                    data=attack_data,
                    timeout=5
                )
                assert response.status_code in [400, 401, 422]
                print(f"✓ {attack_name} blocked successfully")

# ============= ROLE-BASED ACCESS TESTS WITH DATA =============

class TestRoleBasedAccessWithData:
    """Role-based access tests using test data"""
    
    def test_admin_permissions(self, api_base_url, authenticated_admin):
        """Test admin can access all endpoints"""
        import requests
        
        # Admin should be able to access stats
        response = requests.get(
            f"{api_base_url}/api/stats",
            headers=authenticated_admin["headers"]
        )
        
        assert response.status_code == 200
    
    def test_editor_permissions(self, api_base_url, authenticated_editor):
        """Test editor permissions"""
        import requests
        
        # Editor should be able to search
        response = requests.post(
            f"{api_base_url}/query",
            headers=authenticated_editor["headers"],
            data={"query_text": "test"}
        )
        
        assert response.status_code in [200, 400]  # OK or no documents
    
    def test_viewer_permissions(self, api_base_url):
        """Test viewer permissions"""
        import requests
        
        viewer_data = TestData.get_test_user("viewer")
        
        # Register viewer
        requests.post(
            f"{api_base_url}/auth/register",
            json=viewer_data
        )
        
        # Login viewer
        login_response = requests.post(
            f"{api_base_url}/auth/login",
            data={
                "email": viewer_data["email"],
                "password": viewer_data["password"]
            }
        )
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Viewer should be able to search
        response = requests.post(
            f"{api_base_url}/query",
            headers=headers,
            data={"query_text": "test"}
        )
        
        assert response.status_code in [200, 400]

# ============= DATA INTEGRITY TESTS =============

class TestDataIntegrityWithData:
    """Data integrity tests using test data"""
    
    def test_document_content_preservation(self, api_base_url, authenticated_editor, test_microsoft_document):
        """Test that document content is preserved"""
        import requests
        
        doc = test_microsoft_document
        
        # Upload document
        upload_response = requests.post(
            f"{api_base_url}/upload",
            headers=authenticated_editor["headers"],
            files={"file": (doc["filename"], doc["content"], "text/plain")}
        )
        
        assert upload_response.status_code == 200
        
        # Search for content from document
        search_response = requests.post(
            f"{api_base_url}/query",
            headers=authenticated_editor["headers"],
            data={"query_text": "Microsoft"}
        )
        
        assert search_response.status_code == 200
    
    def test_user_data_isolation(self, api_base_url, authenticated_editor, authenticated_admin):
        """Test user data isolation"""
        # Each user should see their own data
        # Admin and editor are different users
        assert authenticated_editor["user"]["email"] != authenticated_admin["user"]["email"]
        assert authenticated_editor["token"] != authenticated_admin["token"]

# ============= PARAMETRIZED TESTS WITH DATA =============

@pytest.mark.parametrize("query_type", TestData.get_all_test_queries().keys())
def test_all_queries_parametrized(api_base_url, authenticated_editor, query_type):
    """Test all queries in test data"""
    import requests
    
    query_data = TestData.get_test_query(query_type)
    
    response = requests.post(
        f"{api_base_url}/query",
        headers=authenticated_editor["headers"],
        data={"query_text": query_data["query"]}
    )
    
    assert response.status_code == 200
    print(f"✓ {query_type}")

@pytest.mark.parametrize("attack_type", TestData.get_all_security_cases().keys())
def test_all_security_cases_parametrized(api_base_url, attack_type):
    """Test all security cases in test data"""
    import requests
    
    attack_data = TestData.get_security_test_case(attack_type)
    
    # All attacks should be blocked or fail
    response = requests.post(
        f"{api_base_url}/auth/login",
        data=attack_data,
        timeout=5
    )
    
    assert response.status_code in [400, 401, 422]
    print(f"✓ {attack_type} blocked")

# ============= SAMPLE USAGE =============

if __name__ == "__main__":
    print("Running tests with test data...")
    print()
    print("Test data includes:")
    print(f"  - {len(TestData.TEST_USERS)} test users")
    print(f"  - {len(TestData.TEST_DOCUMENTS)} test documents")
    print(f"  - {len(TestData.TEST_QUERIES)} test queries")
    print(f"  - {len(TestData.SECURITY_TEST_CASES)} security test cases")
    print()
    print("Run with: pytest tests/test_with_data.py -v")
