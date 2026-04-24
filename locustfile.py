"""
RAG SYSTEM v1.5 - Load Testing with Locust

Install: pip install locust

Run: locust -f locustfile.py -u 10 -r 2 -t 1m

This tests:
- Authentication performance
- Concurrent user load
- Document upload/search under load
- System stability
"""

from locust import HttpUser, task, between
import random
import time

BASE_URL = "http://localhost:8000"
TEST_USERS = []
TEST_TOKENS = {}

# ============= LOAD TEST SCENARIOS =============

class RAGSystemLoadTest(HttpUser):
    """
    Simulates real user behavior under load

    Weights:
    - Auth: 10 percent (users logging in)
    - Search: 60 percent (most common action)
    - Upload: 20 percent (document uploads)
    - Dashboard: 10 percent (admin tasks)
    """

    wait_time = between(1, 3)

    def on_start(self):
        """Initialize user session"""
        self.email = f"loadtest_{int(time.time() * 1000)}@test.com"
        self.password = "LoadTest123!"
        self.token = None
        self.login()

    # ============= AUTH TASKS (10 percent) =============

    @task(1)
    def login(self):
        """Simulate user login"""
        response = self.client.post(
            "/auth/login",
            data={
                "email": self.email,
                "password": self.password
            },
            catch_response=True
        )

        if response.status_code == 200:
            try:
                self.token = response.json().get("access_token")
                response.success()
            except Exception as e:
                response.failure(f"Failed to parse token: {str(e)}")
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

    # ============= SEARCH TASKS (60 percent) =============

    @task(6)
    def search_documents(self):
        """Simulate document search"""
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

    # ============= UPLOAD TASKS (20 percent) =============

    @task(2)
    def upload_document(self):
        """Simulate document upload"""
        if not self.token:
            return

        content = b"Test document about Microsoft. Microsoft is a technology company."

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

    # ============= DASHBOARD TASKS (10 percent) =============

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

        if response.status_code in [200, 403]:
            response.success()
        else:
            response.failure(f"Team members failed: {response.status_code}")


# ============= STRESS TEST USER =============

class StressTestUser(HttpUser):
    """
    Aggressive stress testing user
    Performs operations as fast as possible
    """

    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Initialize for stress test"""
        self.email = "stress@test.com"
        self.token = None

        response = self.client.post(
            "/auth/login",
            data={
                "email": self.email,
                "password": "StressTest123!"
            }
        )

        if response.status_code == 200:
            try:
                self.token = response.json().get("access_token")
            except Exception:
                pass

    @task(10)
    def rapid_searches(self):
        """Perform rapid searches"""
        if not self.token:
            return

        queries = [
            "query 1",
            "query 2",
            "query 3",
            "query 4",
            "query 5"
        ]

        for query in queries:
            self.client.post(
                "/query",
                headers={"Authorization": f"Bearer {self.token}"},
                data={"query_text": query}
            )


# ============= CUSTOM STATS COLLECTION =============

from locust import events
import time as time_module

test_start_time = None

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Run before test starts"""
    global test_start_time
    test_start_time = time_module.time()
    print("\n" + "=" * 60)
    print("RAG System Load Test Started")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Run after test completes"""
    print("\n" + "=" * 60)
    print("Load Test Complete")
    print("=" * 60)

    if hasattr(environment.stats, 'total'):
        print("\nTEST SUMMARY:")
        print(f"Total Requests: {environment.stats.total.num_requests}")
        print(f"Failed Requests: {environment.stats.total.num_failures}")

        success_rate = 100 * (1 - environment.stats.total.failure_rate)
        print(f"Success Rate: {success_rate:.2f}%")

        print(f"Avg Response Time: {environment.stats.total.avg_response_time:.2f}ms")
        print(f"Min Response Time: {environment.stats.total.min_response_time:.2f}ms")
        print(f"Max Response Time: {environment.stats.total.max_response_time:.2f}ms")


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
- Avg response time: less than 1 second
- Success rate: greater than 95%
- P95 latency: less than 2 seconds
- No memory leaks
- Stable throughput

TEST SCENARIOS:
- Normal load: 10 users, 2 ramp-up
- High load: 50 users, 5 ramp-up
- Stress test: 100 plus users, max ramp-up
- Spike test: Instant 100 users
- Soak test: 50 users for 1 plus hours
"""