"""
RAG System v1.5 - Load Testing with Locust

Install: pip install locust

Run: locust -f locustfile.py -u 10 -r 2 -t 1m

Parameters:
  -u: Number of users
  -r: Ramp-up rate (users per second)
  -t: Test duration

This tests:
- Authentication performance
- Concurrent user load
- Document upload/search under load
- System stability
"""

from locust import HttpUser, task, between
import random
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERS = []
TEST_TOKENS = {}

---

# ============= UTILITY FUNCTIONS =============

def setup_test_users():
    """Create test users before load test"""
    global TEST_USERS, TEST_TOKENS
    
    print("Setting up test users...")
    
    for i in range(10):
        email = f"loadtest{i}@test.com"
        password = "LoadTest123!"
        
        # Register
        client = HttpUser()
        client.client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "username": f"loadtest{i}",
                "password": password,
                "full_name": f"Load Test User {i}"
            }
        )
        
        # Login
        response = client.client.post(
            f"{BASE_URL}/auth/login",
            data={
                "email": email,
                "password": password
            }
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            TEST_USERS.append(email)
            TEST_TOKENS[email] = token
            print(f"✓ Created user {i+1}/10")
    
    print(f"Test setup complete: {len(TEST_USERS)} users created")

---

# ============= LOAD TEST SCENARIOS =============

class RAGSystemLoadTest(HttpUser):
    """
    Simulates real user behavior under load
    
    Weights:
    - Auth: 10% (users logging in)
    - Search: 60% (most common action)
    - Upload: 20% (document uploads)
    - Dashboard: 10% (admin tasks)
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user session"""
        # Pick random user
        if TEST_USERS:
            self.email = random.choice(TEST_USERS)
            self.token = TEST_TOKENS[self.email]
        else:
            # Create user on the fly
            self.email = f"user_{int(time.time() * 1000)}@test.com"
            self.token = None
            self.login()
    
    # ============= AUTH TASKS (10%) =============
    
    @task(1)
    def login(self):
        """Simulate user login"""
        response = self.client.post(
            "/auth/login",
            data={
                "email": self.email,
                "password": "LoadTest123!"
            },
            catch_response=True
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    @task(1)
    def get_current_user(self):
        """Simulate getting user info"""
        if not self.token:
            return
        
        response = self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        )
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Get user failed: {response.status_code}")
    
    # ============= SEARCH TASKS (60%) =============
    
    @task(6)
    def search_documents(self):
        """Simulate document search - MOST COMMON"""
        if not self.token:
            return
        
        queries = [
            "What is Microsoft?",
            "Tell me about technology",
            "Company information",
            "Founder details",
            "Financial performance",
            "Product overview"
        ]
        
        query = random.choice(queries)
        
        response = self.client.post(
            "/query",
            headers={"Authorization": f"Bearer {self.token}"},
            data={"query_text": query},
            catch_response=True
        )
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Search failed: {response.status_code}")
    
    # ============= UPLOAD TASKS (20%) =============
    
    @task(2)
    def upload_document(self):
        """Simulate document upload"""
        if not self.token:
            return
        
        # Create test file content
        content = b"Test document about Microsoft. Microsoft is a technology company founded in 1975."
        
        response = self.client.post(
            "/upload",
            headers={"Authorization": f"Bearer {self.token}"},
            files={"file": ("test.txt", content, "text/plain")},
            catch_response=True
        )
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Upload failed: {response.status_code}")
    
    # ============= DASHBOARD TASKS (10%) =============
    
    @task(1)
    def get_statistics(self):
        """Simulate viewing dashboard stats"""
        if not self.token:
            return
        
        response = self.client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        )
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Stats failed: {response.status_code}")
    
    @task(1)
    def get_audit_logs(self):
        """Simulate viewing audit logs"""
        if not self.token:
            return
        
        response = self.client.get(
            "/api/audit-logs?limit=50",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        )
        
        # May fail if not admin, but that's expected
        if response.status_code in [200, 403]:
            response.success()
        else:
            response.failure(f"Audit logs failed: {response.status_code}")
    
    @task(1)
    def list_team_members(self):
        """Simulate viewing team members"""
        if not self.token:
            return
        
        response = self.client.get(
            "/api/team/members",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        )
        
        # May fail if not admin, but that's expected
        if response.status_code in [200, 403]:
            response.success()
        else:
            response.failure(f"Team members failed: {response.status_code}")

---

# ============= STRESS TEST USER =============

class StressTestUser(HttpUser):
    """
    Aggressive stress testing user
    Performs operations as fast as possible
    """
    
    wait_time = between(0.1, 0.5)  # Fast requests
    
    def on_start(self):
        """Initialize for stress test"""
        self.email = "stress@test.com"
        self.token = None
        
        # Try to login
        response = self.client.post(
            "/auth/login",
            data={
                "email": self.email,
                "password": "StressTest123!"
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
    
    @task(10)
    def rapid_searches(self):
        """Perform rapid searches"""
        if not self.token:
            return
        
        queries = [f"query {random.randint(1, 100)}" for _ in range(5)]
        
        for query in queries:
            self.client.post(
                "/query",
                headers={"Authorization": f"Bearer {self.token}"},
                data={"query_text": query}
            )

---

# ============= CUSTOM STATS COLLECTION =============

from locust import events
import statistics

stats_history = []

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Run before test starts"""
    print("\n" + "="*60)
    print("RAG System Load Test Started")
    print("="*60)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Run after test completes"""
    print("\n" + "="*60)
    print("Load Test Complete")
    print("="*60)
    
    # Print summary
    print("\n📊 TEST SUMMARY:")
    print(f"Total Requests: {environment.stats.total.num_requests}")
    print(f"Failed Requests: {environment.stats.total.num_failures}")
    print(f"Success Rate: {100 * (1 - environment.stats.total.failure_rate):.2f}%")
    print(f"Avg Response Time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {environment.stats.total.min_response_time:.2f}ms")
    print(f"Max Response Time: {environment.stats.total.max_response_time:.2f}ms")
    print(f"95th Percentile: {environment.stats.total.percentile_95:.2f}ms")

---

# ============= USAGE INSTRUCTIONS =============

"""
USAGE INSTRUCTIONS:

1. START BACKEND:
   python -m uvicorn src.api.main:app --reload

2. RUN LOAD TEST (Interactive UI):
   locust -f locustfile.py --host=http://localhost:8000

   Then:
   - Open http://localhost:8089
   - Set number of users (e.g., 10)
   - Set ramp-up rate (e.g., 2 users/sec)
   - Click "Start swarming"

3. RUN LOAD TEST (CLI):
   locust -f locustfile.py \
     --host=http://localhost:8000 \
     -u 10 \
     -r 2 \
     -t 5m \
     --headless

   Parameters:
   -u: Number of users
   -r: Ramp-up rate (users per second)
   -t: Test duration

4. ANALYZE RESULTS:
   - Response times
   - Success rate
   - Error patterns
   - System stability

EXPECTED PERFORMANCE:
- Avg response time: < 1 second
- Success rate: > 95%
- P95 latency: < 2 seconds
- No memory leaks
- Stable throughput

TEST SCENARIOS:
- Normal load: 10 users, 2 ramp-up
- High load: 50 users, 5 ramp-up
- Stress test: 100+ users, max ramp-up
- Spike test: Instant 100 users
- Soak test: 50 users for 1+ hours
"""
