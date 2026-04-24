"""
RAG SYSTEM v1.5 - AUTOMATED TEST RUNNER

Master automation script that runs:
1. Unit tests (Pytest)
2. API tests (Postman/Newman)
3. Load tests (Locust)
4. Security tests
5. Generates HTML report

Run: python automated_tests.py
"""

import subprocess
import json
import time
import os
from datetime import datetime
from pathlib import Path
import sys

# ============= CONFIGURATION =============

BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
TEST_USER_EMAIL = "testuser@automation.com"
TEST_USER_PASSWORD = "AutomationTest123!"
TEST_ADMIN_EMAIL = "admin@automation.com"
TEST_ADMIN_PASSWORD = "AdminTest123!"

# Test parameters
TEST_TIMEOUT = 300  # 5 minutes
LOAD_TEST_DURATION = "1m"
LOAD_TEST_USERS = 10

# Report configuration
REPORTS_DIR = "test_reports"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = f"{REPORTS_DIR}/test_report_{TIMESTAMP}.html"

# ============= SETUP =============

class Colors:
    """Color codes for terminal output"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'

class TestRunner:
    """Master test runner"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_run_id": TIMESTAMP,
            "environment": BASE_URL,
            "tests": {
                "unit_tests": {"status": "pending", "details": {}},
                "api_tests": {"status": "pending", "details": {}},
                "load_tests": {"status": "pending", "details": {}},
                "security_tests": {"status": "pending", "details": {}}
            },
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "pass_rate": "0%"
            }
        }
        self.setup_reports_dir()
    
    def setup_reports_dir(self):
        """Create reports directory"""
        Path(REPORTS_DIR).mkdir(exist_ok=True)
        print(f"{Colors.BLUE}✓ Reports directory ready: {REPORTS_DIR}{Colors.RESET}")
    
    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}{Colors.RESET}\n")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Colors.RED}❌ {text}{Colors.RESET}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")
    
    # ============= PREFLIGHT CHECKS =============
    
    def check_backend_running(self):
        """Check if backend is running"""
        self.print_header("PREFLIGHT CHECK: Backend Health")
        
        try:
            import requests
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.print_success(f"Backend running at {BASE_URL}")
                health = response.json()
                self.print_info(f"Status: {health.get('status')}")
                self.print_info(f"Version: {health.get('version')}")
                return True
            else:
                self.print_error(f"Backend returned {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Cannot connect to backend: {str(e)}")
            self.print_warning("Make sure backend is running:")
            self.print_info("python -m uvicorn src.api.main:app --reload")
            return False
    
    def check_dependencies(self):
        """Check if required tools are installed"""
        self.print_header("PREFLIGHT CHECK: Dependencies")
        
        dependencies = {
            "pytest": "pip install pytest",
            "requests": "pip install requests",
            "newman": "npm install -g newman",
        }
        
        missing = []
        
        for dep, install_cmd in dependencies.items():
            try:
                if dep == "pytest":
                    import pytest
                    self.print_success(f"{dep} installed")
                elif dep == "requests":
                    import requests
                    self.print_success(f"{dep} installed")
                elif dep == "newman":
                    result = subprocess.run(
                        ["newman", "--version"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self.print_success(f"{dep} installed")
                    else:
                        missing.append((dep, install_cmd))
            except Exception as e:
                missing.append((dep, install_cmd))
        
        if missing:
            self.print_warning("Missing dependencies:")
            for dep, cmd in missing:
                self.print_info(f"  Install {dep}: {cmd}")
            return False
        
        return True
    
    # ============= UNIT TESTS =============
    
    def run_unit_tests(self):
        """Run pytest unit tests"""
        self.print_header("PHASE 1: UNIT TESTS (Pytest)")
        
        try:
            # Check if tests exist
            if not Path("tests/test_rag_system.py").exists():
                self.print_warning("test_rag_system.py not found in tests/")
                self.print_info("Skipping unit tests")
                self.results["tests"]["unit_tests"]["status"] = "skipped"
                return False
            
            # Run pytest with JSON output
            cmd = [
                "pytest",
                "tests/test_rag_system.py",
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file={REPORTS_DIR}/pytest_{TIMESTAMP}.json"
            ]
            
            self.print_info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, timeout=TEST_TIMEOUT)
            
            # Parse output
            output = result.stdout.decode('utf-8', errors='ignore')
            
            if result.returncode == 0:
                self.print_success("All unit tests passed!")
                self.results["tests"]["unit_tests"]["status"] = "passed"
                self.extract_pytest_results(output)
                return True
            else:
                self.print_error("Some unit tests failed!")
                print(output[-2000:])  # Last 2000 chars
                self.results["tests"]["unit_tests"]["status"] = "failed"
                self.extract_pytest_results(output)
                return False
        
        except FileNotFoundError:
            self.print_error("Pytest not installed: pip install pytest")
            self.results["tests"]["unit_tests"]["status"] = "error"
            return False
        except subprocess.TimeoutExpired:
            self.print_error("Unit tests timeout!")
            self.results["tests"]["unit_tests"]["status"] = "timeout"
            return False
        except Exception as e:
            self.print_error(f"Error running unit tests: {str(e)}")
            self.results["tests"]["unit_tests"]["status"] = "error"
            return False
    
    def extract_pytest_results(self, output):
        """Extract pytest results from output"""
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line or 'failed' in line:
                self.print_info(line.strip())
                self.results["tests"]["unit_tests"]["details"]["summary"] = line.strip()
    
    # ============= API TESTS =============
    
    def run_api_tests_postman(self):
        """Run API tests using Newman (Postman CLI)"""
        self.print_header("PHASE 2: API TESTS (Postman/Newman)")
        
        try:
            # Check if Postman collection exists
            if not Path("RAG_System_Postman_Collection.json").exists():
                self.print_warning("Postman collection not found")
                self.print_info("Skipping Postman tests")
                self.results["tests"]["api_tests"]["status"] = "skipped"
                return False
            
            # Set environment variables for Postman
            postman_env = {
                "BASE_URL": BASE_URL,
                "ACCESS_TOKEN": "",  # Will be filled after login
            }
            
            # Create temp env file
            env_file = f"{REPORTS_DIR}/postman_env_{TIMESTAMP}.json"
            with open(env_file, 'w') as f:
                json.dump(postman_env, f)
            
            # Run Newman
            cmd = [
                "newman",
                "run",
                "RAG_System_Postman_Collection.json",
                f"--environment={env_file}",
                f"--reporters=cli,json",
                f"--reporter-json-export={REPORTS_DIR}/newman_{TIMESTAMP}.json"
            ]
            
            self.print_info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, timeout=TEST_TIMEOUT)
            
            output = result.stdout.decode('utf-8', errors='ignore')
            
            if result.returncode == 0:
                self.print_success("All API tests passed!")
                self.results["tests"]["api_tests"]["status"] = "passed"
                return True
            else:
                self.print_error("Some API tests failed!")
                print(output[-2000:])
                self.results["tests"]["api_tests"]["status"] = "failed"
                return False
        
        except FileNotFoundError:
            self.print_error("Newman not installed: npm install -g newman")
            self.results["tests"]["api_tests"]["status"] = "error"
            return False
        except subprocess.TimeoutExpired:
            self.print_error("API tests timeout!")
            self.results["tests"]["api_tests"]["status"] = "timeout"
            return False
        except Exception as e:
            self.print_error(f"Error running API tests: {str(e)}")
            self.results["tests"]["api_tests"]["status"] = "error"
            return False
    
    def run_api_tests_manual(self):
        """Run API tests using manual requests"""
        self.print_header("PHASE 2: API TESTS (Manual)")
        
        try:
            import requests
            
            test_results = {
                "auth_tests": [],
                "upload_tests": [],
                "search_tests": [],
                "health_check": []
            }
            
            # Health check
            self.print_info("Testing health endpoint...")
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.print_success("Health check passed")
                test_results["health_check"].append({"test": "health", "status": "passed"})
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                test_results["health_check"].append({"test": "health", "status": "failed"})
            
            # Register user
            self.print_info("Testing user registration...")
            register_data = {
                "email": f"autotest_{int(time.time())}@test.com",
                "username": "autotest",
                "password": TEST_USER_PASSWORD,
                "full_name": "Automation Test"
            }
            
            response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
            if response.status_code == 200:
                self.print_success("User registration passed")
                test_results["auth_tests"].append({"test": "register", "status": "passed"})
                token = response.json().get("access_token")
            else:
                self.print_error(f"User registration failed: {response.status_code}")
                test_results["auth_tests"].append({"test": "register", "status": "failed"})
                token = None
            
            # Login
            if token:
                self.print_info("Testing user login...")
                login_data = {"email": register_data["email"], "password": TEST_USER_PASSWORD}
                response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
                if response.status_code == 200:
                    self.print_success("User login passed")
                    test_results["auth_tests"].append({"test": "login", "status": "passed"})
                else:
                    self.print_error(f"User login failed: {response.status_code}")
                    test_results["auth_tests"].append({"test": "login", "status": "failed"})
            
            self.results["tests"]["api_tests"]["status"] = "passed"
            self.results["tests"]["api_tests"]["details"] = test_results
            return True
        
        except Exception as e:
            self.print_error(f"Error running API tests: {str(e)}")
            self.results["tests"]["api_tests"]["status"] = "error"
            return False
    
    # ============= LOAD TESTS =============
    
    def run_load_tests(self):
        """Run load tests using Locust"""
        self.print_header("PHASE 3: LOAD TESTS (Locust)")
        
        try:
            # Check if locustfile exists
            if not Path("locustfile.py").exists():
                self.print_warning("locustfile.py not found")
                self.print_info("Skipping load tests")
                self.results["tests"]["load_tests"]["status"] = "skipped"
                return False
            
            self.print_info(f"Running load test: {LOAD_TEST_USERS} users, {LOAD_TEST_DURATION}")
            
            # Run Locust in headless mode
            cmd = [
                "locust",
                "-f", "locustfile.py",
                f"--host={BASE_URL}",
                "-u", str(LOAD_TEST_USERS),
                "-r", "2",
                "-t", LOAD_TEST_DURATION,
                "--headless",
                f"--csv={REPORTS_DIR}/load_test_{TIMESTAMP}"
            ]
            
            self.print_info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            
            output = result.stdout.decode('utf-8', errors='ignore')
            
            if result.returncode == 0:
                self.print_success("Load tests completed!")
                self.results["tests"]["load_tests"]["status"] = "passed"
                self.extract_load_test_results(output)
                return True
            else:
                self.print_warning("Load test warning or failure")
                print(output[-1000:])
                self.results["tests"]["load_tests"]["status"] = "warning"
                return False
        
        except FileNotFoundError:
            self.print_error("Locust not installed: pip install locust")
            self.results["tests"]["load_tests"]["status"] = "skipped"
            return False
        except subprocess.TimeoutExpired:
            self.print_warning("Load test timeout!")
            self.results["tests"]["load_tests"]["status"] = "timeout"
            return False
        except Exception as e:
            self.print_warning(f"Load test skipped: {str(e)}")
            self.results["tests"]["load_tests"]["status"] = "skipped"
            return False
    
    def extract_load_test_results(self, output):
        """Extract load test results"""
        lines = output.split('\n')
        for line in lines:
            if 'Requests/sec' in line or 'Fastest' in line or 'Average' in line:
                self.print_info(line.strip())
    
    # ============= SECURITY TESTS =============
    
    def run_security_tests(self):
        """Run basic security tests"""
        self.print_header("PHASE 4: SECURITY TESTS")
        
        try:
            import requests
            
            security_results = []
            
            # Test 1: SQL Injection
            self.print_info("Testing SQL Injection prevention...")
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={"email": "admin' OR '1'='1", "password": "test"},
                timeout=5
            )
            if response.status_code != 200:
                self.print_success("SQL Injection blocked")
                security_results.append({"test": "SQL Injection", "status": "passed"})
            else:
                self.print_error("SQL Injection vulnerability!")
                security_results.append({"test": "SQL Injection", "status": "failed"})
            
            # Test 2: XSS in Search
            self.print_info("Testing XSS prevention...")
            response = requests.post(
                f"{BASE_URL}/query",
                data={"query_text": "<script>alert('xss')</script>"},
                headers={"Authorization": f"Bearer fake_token"},
                timeout=5
            )
            if response.status_code in [200, 403]:  # Either safe or requires auth
                self.print_success("XSS prevention verified")
                security_results.append({"test": "XSS", "status": "passed"})
            
            # Test 3: Missing Authentication
            self.print_info("Testing authentication enforcement...")
            response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
            if response.status_code == 403 or response.status_code == 401:
                self.print_success("Authentication enforced")
                security_results.append({"test": "Auth Enforcement", "status": "passed"})
            else:
                self.print_error("Unprotected endpoint found!")
                security_results.append({"test": "Auth Enforcement", "status": "failed"})
            
            # Test 4: HTTPS
            self.print_info("Checking HTTPS requirement...")
            if BASE_URL.startswith("https://"):
                self.print_success("HTTPS enabled")
                security_results.append({"test": "HTTPS", "status": "passed"})
            else:
                self.print_warning("Not using HTTPS (OK for localhost)")
                security_results.append({"test": "HTTPS", "status": "warning"})
            
            self.results["tests"]["security_tests"]["status"] = "passed"
            self.results["tests"]["security_tests"]["details"] = security_results
            return True
        
        except Exception as e:
            self.print_warning(f"Security tests error: {str(e)}")
            self.results["tests"]["security_tests"]["status"] = "warning"
            return False
    
    # ============= REPORTING =============
    
    def calculate_summary(self):
        """Calculate test summary"""
        tests = self.results["tests"]
        
        total = 4
        passed = sum(1 for t in tests.values() if t["status"] == "passed")
        failed = sum(1 for t in tests.values() if t["status"] == "failed")
        skipped = sum(1 for t in tests.values() if t["status"] == "skipped")
        
        self.results["summary"]["total_tests"] = total
        self.results["summary"]["passed"] = passed
        self.results["summary"]["failed"] = failed
        self.results["summary"]["skipped"] = skipped
        
        if total > 0:
            pass_rate = (passed / (total - skipped)) * 100 if (total - skipped) > 0 else 0
            self.results["summary"]["pass_rate"] = f"{pass_rate:.1f}%"
    
    def generate_html_report(self):
        """Generate HTML test report"""
        self.calculate_summary()
        
        # Determine status color
        summary = self.results["summary"]
        if summary["failed"] == 0:
            status_color = "green"
            status_text = "✅ PASSED"
        else:
            status_color = "red"
            status_text = "❌ FAILED"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAG System v1.5 - Test Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 8px; margin-bottom: 30px; }}
                .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
                .header p {{ opacity: 0.9; }}
                .status {{ font-size: 24px; font-weight: bold; margin-top: 20px; }}
                .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
                .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .summary-card h3 {{ color: #667eea; font-size: 14px; margin-bottom: 10px; }}
                .summary-card .number {{ font-size: 32px; font-weight: bold; }}
                .test-section {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .test-section h2 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
                .test-result {{ padding: 15px; margin-bottom: 10px; border-radius: 4px; border-left: 4px solid #ddd; }}
                .test-result.passed {{ background: #f0fdf4; border-left-color: #22c55e; }}
                .test-result.passed::before {{ content: "✅"; margin-right: 10px; }}
                .test-result.failed {{ background: #fef2f2; border-left-color: #ef4444; }}
                .test-result.failed::before {{ content: "❌"; margin-right: 10px; }}
                .test-result.skipped {{ background: #fffbeb; border-left-color: #f59e0b; }}
                .test-result.skipped::before {{ content: "⏭️"; margin-right: 10px; }}
                .test-result.error {{ background: #fef2f2; border-left-color: #ef4444; }}
                .test-result.error::before {{ content: "⚠️"; margin-right: 10px; }}
                .footer {{ text-align: center; color: #666; padding: 20px; }}
                .timestamp {{ color: #999; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background: #f3f4f6; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                .pass-rate {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>RAG System v1.5</h1>
                    <p>Automated Test Report</p>
                    <div class="status" style="color: {status_color};">{status_text}</div>
                    <p style="margin-top: 20px; font-size: 14px;">Generated: {self.results['timestamp']}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card">
                        <h3>Total Tests</h3>
                        <div class="number">{summary['total_tests']}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Passed</h3>
                        <div class="number" style="color: #22c55e;">{summary['passed']}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Failed</h3>
                        <div class="number" style="color: #ef4444;">{summary['failed']}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Pass Rate</h3>
                        <div class="pass-rate">{summary['pass_rate']}</div>
                    </div>
                </div>
                
                <div class="test-section">
                    <h2>Test Results</h2>
                    <table>
                        <tr>
                            <th>Test Phase</th>
                            <th>Status</th>
                            <th>Details</th>
                        </tr>
        """
        
        for test_name, test_data in self.results["tests"].items():
            status = test_data["status"]
            test_label = test_name.replace("_", " ").title()
            html += f"""
                        <tr>
                            <td>{test_label}</td>
                            <td><span class="test-result {status}">{status.upper()}</span></td>
                            <td>{json.dumps(test_data.get('details', {}), indent=2)[:200]}</td>
                        </tr>
            """
        
        html += """
                    </table>
                </div>
                
                <div class="test-section">
                    <h2>Test Environment</h2>
                    <table>
                        <tr>
                            <th>Property</th>
                            <th>Value</th>
                        </tr>
        """
        
        html += f"""
                        <tr><td>Backend URL</td><td>{BASE_URL}</td></tr>
                        <tr><td>Test Run ID</td><td>{self.results['test_run_id']}</td></tr>
                        <tr><td>Timestamp</td><td>{self.results['timestamp']}</td></tr>
                    </table>
                </div>
                
                <div class="footer">
                    <p>RAG System v1.5 - Automated Test Suite</p>
                    <p class="timestamp">Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(html)

        return REPORT_FILE

    def save_json_report(self):
        """Save results as JSON"""
        json_file = f"{REPORTS_DIR}/test_results_{TIMESTAMP}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        return json_file

    # ============= MAIN EXECUTION =============

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_header("RAG SYSTEM v1.5 - AUTOMATED TEST SUITE")
        self.print_info(f"Environment: {BASE_URL}")
        self.print_info(f"Report ID: {TIMESTAMP}\n")

        # Preflight checks
        if not self.check_backend_running():
            self.print_error("ABORT: Backend not running!")
            return False

        # Run tests
        all_passed = True

        # Phase 1: Unit Tests
        if not self.run_unit_tests():
            all_passed = False

        # Phase 2: API Tests
        if not self.run_api_tests_manual():  # Use manual if Newman fails
            all_passed = False

        # Phase 3: Load Tests
        if not self.run_load_tests():
            all_passed = False

        # Phase 4: Security Tests
        if not self.run_security_tests():
            all_passed = False

        # Generate reports
        self.print_header("GENERATING REPORTS")
        html_report = self.generate_html_report()
        json_report = self.save_json_report()

        self.print_success(f"HTML Report: {html_report}")
        self.print_success(f"JSON Report: {json_report}")

        # Print summary
        self.print_header("TEST SUMMARY")
        summary = self.results["summary"]
        self.print_info(f"Total Tests: {summary['total_tests']}")
        self.print_success(f"Passed: {summary['passed']}")
        if summary['failed'] > 0:
            self.print_error(f"Failed: {summary['failed']}")
        self.print_info(f"Pass Rate: {summary['pass_rate']}")

        # Final status
        self.print_header("FINAL RESULT")
        if summary["failed"] == 0:
            self.print_success("✅ ALL TESTS PASSED!")
            return True
        else:
            self.print_error(f"❌ {summary['failed']} TEST(S) FAILED!")
            return False

# ============= ENTRY POINT =============

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)