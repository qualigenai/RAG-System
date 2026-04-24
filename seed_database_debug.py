"""
RAG System v1.5 - Database Seeding Script (DEBUG VERSION)

Seeds the database with test data before running tests
Added debug output to show exact errors

Usage:
    python seed_database.py          # Seed with default test data
"""

import sys
import requests
import json
from datetime import datetime
from test_data import TestData

class DatabaseSeeder:
    """Seed database with test data"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "users_created": 0,
            "documents_uploaded": 0,
            "errors": []
        }

    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is running")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to backend: {str(e)}")
            print(f"   Make sure backend is running: python -m uvicorn src.api.main:app --reload")
            return False

    def seed_users(self):
        """Seed test users"""
        print("\n📝 Seeding Test Users...")
        print("-" * 50)

        for role, user_data in TestData.get_all_test_users().items():
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/register",
                    json=user_data,
                    timeout=10
                )

                if response.status_code == 200:
                    print(f"✅ {role.upper()}: {user_data['email']}")
                    self.results["users_created"] += 1
                elif response.status_code == 400:
                    print(f"⚠️  {role.upper()}: Already exists or invalid")
                else:
                    error = f"{role}: HTTP {response.status_code}"
                    print(f"❌ {error}")
                    self.results["errors"].append(error)

            except Exception as e:
                error = f"{role}: {str(e)}"
                print(f"❌ {error}")
                self.results["errors"].append(error)

        print(f"\n✓ Users seeded: {self.results['users_created']}")

    def seed_documents(self):
        """Seed test documents"""
        print("\n📄 Seeding Test Documents...")
        print("-" * 50)

        editor_data = TestData.get_test_user("editor")

        print(f"   Registering editor: {editor_data['email']}")
        reg_response = requests.post(
            f"{self.base_url}/api/auth/register",
            json=editor_data,
            timeout=10
        )
        print(f"   Register status: {reg_response.status_code}")

        print(f"   Logging in editor: {editor_data['email']}")
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={
                "email": editor_data["email"],
                "password": editor_data["password"]
            },
            timeout=10
        )

        print(f"   Login status: {login_response.status_code}")

        if login_response.status_code != 200:
            print(f"❌ Could not login as editor")
            print(f"   Response: {login_response.text}")
            return

        try:
            token = login_response.json().get("access_token")
            print(f"   Token received: {token[:20]}..." if token else "   ERROR: No token in response")
        except Exception as e:
            print(f"   ERROR parsing token: {str(e)}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # Upload documents
        for doc_name, doc_data in TestData.get_all_test_documents().items():
            try:
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    headers=headers,
                    files={"file": (doc_data["filename"], doc_data["content"], "text/plain")},
                    timeout=30
                )

                if response.status_code == 200:
                    print(f"✅ {doc_name}: {doc_data['filename']}")
                    self.results["documents_uploaded"] += 1
                else:
                    error = f"{doc_name}: HTTP {response.status_code}"
                    print(f"❌ {error}")
                    self.results["errors"].append(error)

            except Exception as e:
                error = f"{doc_name}: {str(e)}"
                print(f"❌ {error}")
                self.results["errors"].append(error)

        print(f"\n✓ Documents uploaded: {self.results['documents_uploaded']}")

    def verify_data(self):
        """Verify seeded data"""
        print("\n✔️  Verifying Seeded Data...")
        print("-" * 50)

        editor_data = TestData.get_test_user("editor")

        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={
                "email": editor_data["email"],
                "password": editor_data["password"]
            },
            timeout=10
        )

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            stats_response = requests.get(
                f"{self.base_url}/api/stats",
                headers=headers,
                timeout=10
            )

            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Documents in system: {stats.get('total_documents', 0)}")
                team_members = stats.get('team_members', 0)
                if isinstance(team_members, list):
                    team_count = len(team_members)
                else:
                    team_count = team_members
                print(f"✅ Team members: {team_count}")

        print("\n✓ Verification complete")

    def export_results(self, filename=None):
        """Export seeding results"""
        if not filename:
            filename = f"seed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Results exported to: {filename}")
        return filename

    def print_summary(self):
        """Print seeding summary"""
        print("\n" + "=" * 50)
        print("DATABASE SEEDING SUMMARY")
        print("=" * 50)
        print(f"✅ Users created: {self.results['users_created']}")
        print(f"✅ Documents uploaded: {self.results['documents_uploaded']}")

        if self.results["errors"]:
            print(f"❌ Errors: {len(self.results['errors'])}")
            for error in self.results["errors"]:
                print(f"   - {error}")
        else:
            print("✅ No errors")

        print("=" * 50)

    def run(self, seed_documents=True, verify=True, export_results=False):
        """Run complete seeding process"""
        print("\n🌱 DATABASE SEEDING STARTED")
        print("=" * 50)

        if not self.check_backend():
            return False

        self.seed_users()

        if seed_documents:
            self.seed_documents()

        if verify:
            self.verify_data()

        if export_results:
            self.export_results()

        self.print_summary()

        return len(self.results["errors"]) == 0

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed RAG System database with test data"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    seeder = DatabaseSeeder(base_url=args.url)
    success = seeder.run(seed_documents=True, verify=True, export_results=False)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())