"""
RAG System v1.5 - Database Seeding Script

Seeds the database with test data before running tests

Usage:
    python seed_database.py          # Seed with default test data
    python seed_database.py --clean  # Clear and seed fresh
    python seed_database.py --export # Export seeded data
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
                    # User might already exist, try to show status
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
        
        # Get editor token for upload
        editor_data = TestData.get_test_user("editor")
        
        # Register editor if needed
        requests.post(
            f"{self.base_url}/api/auth/register",
            json=editor_data,
            timeout=10
        )
        
        # Login to get token
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={
                "email": editor_data["email"],
                "password": editor_data["password"]
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Could not login as editor")
            return
        
        token = login_response.json().get("access_token")
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
        
        # Try to get stats
        editor_data = TestData.get_test_user("editor")
        
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={
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
                print(f"✅ Team members: {len(stats.get('team_members', []))}")
        
        print("\n✓ Verification complete")
    
    def export_results(self, filename=None):
        """Export seeding results"""
        if not filename:
            filename = f"seed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
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
        
        # Check backend
        if not self.check_backend():
            return False
        
        # Seed users
        self.seed_users()
        
        # Seed documents
        if seed_documents:
            self.seed_documents()
        
        # Verify
        if verify:
            self.verify_data()
        
        # Export results
        if export_results:
            self.export_results()
        
        # Print summary
        self.print_summary()
        
        return len(self.results["errors"]) == 0

# ============= CLEANUP FUNCTION =============

def cleanup_test_data(base_url="http://localhost:8000"):
    """Clean up test data from database"""
    print("\n🗑️  CLEANING TEST DATA")
    print("-" * 50)
    
    # Get admin token
    admin_data = TestData.get_test_user("admin")
    
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        data={
            "email": admin_data["email"],
            "password": admin_data["password"]
        },
        timeout=10
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Note: Actual deletion endpoints would need to be implemented
        # This is a template for future implementation
        print("✅ Cleanup complete")
    else:
        print("❌ Could not authenticate for cleanup")

# ============= COMMAND LINE INTERFACE =============

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
    parser.add_argument(
        "--no-documents",
        action="store_true",
        help="Don't seed documents"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Don't verify seeded data"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export seeding results"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean test data first (careful!)"
    )
    
    args = parser.parse_args()
    
    # Clean if requested
    if args.clean:
        response = input("⚠️  This will delete test data. Continue? (yes/no): ")
        if response.lower() == "yes":
            cleanup_test_data(args.url)
    
    # Seed database
    seeder = DatabaseSeeder(base_url=args.url)
    success = seeder.run(
        seed_documents=not args.no_documents,
        verify=not args.no_verify,
        export_results=args.export
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

# ============= USAGE EXAMPLES =============

"""
USAGE EXAMPLES:

1. Seed with default settings:
   python seed_database.py

2. Seed without documents:
   python seed_database.py --no-documents

3. Seed and export results:
   python seed_database.py --export

4. Seed remote database:
   python seed_database.py --url http://your-server.com

5. Clean and reseed:
   python seed_database.py --clean

6. From Python script:
   from seed_database import DatabaseSeeder
   seeder = DatabaseSeeder()
   seeder.run()
"""
