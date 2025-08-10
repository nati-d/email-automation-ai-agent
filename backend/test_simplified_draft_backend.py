#!/usr/bin/env python3
"""
Test script to verify the simplified draft backend works correctly
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

class SimplifiedDraftTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
    
    def login(self):
        """Login to get access token"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            print(f"🔍 Login: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                print(f"   ✅ Logged in successfully")
                return True
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_create_local_draft(self):
        """Test creating a local draft (no Gmail sync)"""
        try:
            draft_data = {
                "recipients": ["recipient@example.com"],
                "subject": f"Test Local Draft {datetime.now().strftime('%H:%M:%S')}",
                "body": "This is a test draft stored locally only.",
                "sync_with_gmail": False  # Local only
            }
            
            response = self.session.post(f"{BASE_URL}/drafts", json=draft_data)
            print(f"🔍 Create local draft: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                draft_id = data.get("id")
                print(f"   ✅ Local draft created: {draft_id}")
                print(f"   Subject: {data.get('subject')}")
                print(f"   Recipients: {data.get('recipients')}")
                print(f"   Local draft: {data.get('metadata', {}).get('local_draft', False)}")
                return draft_id
            else:
                print(f"   ❌ Failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Create draft error: {str(e)}")
            return None
    
    def test_list_drafts(self):
        """Test listing local drafts"""
        try:
            response = self.session.get(f"{BASE_URL}/drafts")
            print(f"🔍 List drafts: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                drafts = data.get("drafts", [])
                print(f"   ✅ Found {len(drafts)} local drafts")
                return len(drafts) > 0
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ List drafts error: {str(e)}")
            return False
    
    def test_update_draft(self, draft_id):
        """Test updating a local draft"""
        try:
            update_data = {
                "subject": f"Updated Local Draft {datetime.now().strftime('%H:%M:%S')}",
                "body": "This draft has been updated locally.",
                "sync_with_gmail": False
            }
            
            response = self.session.put(f"{BASE_URL}/drafts/{draft_id}", json=update_data)
            print(f"🔍 Update draft: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Draft updated: {data.get('id')}")
                print(f"   New subject: {data.get('subject')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Update draft error: {str(e)}")
            return False
    
    def test_delete_draft(self, draft_id):
        """Test deleting a local draft"""
        try:
            response = self.session.delete(f"{BASE_URL}/drafts/{draft_id}")
            print(f"🔍 Delete draft: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Draft deleted: {data.get('draft_id')}")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Delete draft error: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all simplified draft tests"""
        print("🚀 Starting Simplified Draft Backend Tests")
        print("=" * 50)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return
        
        # Test 1: Create local draft
        print("\n📝 Test 1: Create Local Draft")
        draft_id = self.test_create_local_draft()
        
        if draft_id:
            # Test 2: List drafts
            print("\n📋 Test 2: List Drafts")
            self.test_list_drafts()
            
            # Test 3: Update draft
            print("\n✏️ Test 3: Update Draft")
            self.test_update_draft(draft_id)
            
            # Test 4: Delete draft
            print("\n🗑️ Test 4: Delete Draft")
            self.test_delete_draft(draft_id)
        
        print("\n" + "=" * 50)
        print("✅ Simplified Draft Backend Tests Complete")
        print("📝 Note: Drafts are now stored locally only")
        print("📤 Use the existing sendEmail API to send draft content")

if __name__ == "__main__":
    tester = SimplifiedDraftTester()
    tester.run_tests()