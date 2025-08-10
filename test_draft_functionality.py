#!/usr/bin/env python3
"""
Test script to verify draft functionality works end-to-end
"""

import asyncio
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

class DraftTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def login(self):
        """Login and get auth token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_health_check(self):
        """Test draft health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/drafts/health")
            print(f"🔍 Health check: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status')}")
                print(f"   Message: {data.get('message')}")
                return True
            return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_create_draft(self):
        """Test creating a draft"""
        try:
            draft_data = {
                "recipients": ["recipient@example.com"],
                "subject": f"Test Draft {datetime.now().strftime('%H:%M:%S')}",
                "body": "This is a test draft created by the test script.",
                "sync_with_gmail": False  # Don't sync for testing
            }
            
            response = self.session.post(f"{BASE_URL}/drafts", json=draft_data)
            print(f"🔍 Create draft: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                draft_id = data.get("id")
                print(f"   ✅ Draft created: {draft_id}")
                print(f"   Subject: {data.get('subject')}")
                print(f"   Recipients: {data.get('recipients')}")
                return draft_id
            else:
                print(f"   ❌ Failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Create draft error: {str(e)}")
            return None
    
    def test_get_draft(self, draft_id):
        """Test getting a specific draft"""
        try:
            response = self.session.get(f"{BASE_URL}/drafts/{draft_id}")
            print(f"🔍 Get draft: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Draft retrieved: {data.get('id')}")
                print(f"   Subject: {data.get('subject')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get draft error: {str(e)}")
            return False
    
    def test_list_drafts(self):
        """Test listing drafts"""
        try:
            response = self.session.get(f"{BASE_URL}/drafts")
            print(f"🔍 List drafts: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                drafts = data.get("drafts", [])
                print(f"   ✅ Found {len(drafts)} drafts")
                return len(drafts) > 0
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ List drafts error: {str(e)}")
            return False
    
    def test_update_draft(self, draft_id):
        """Test updating a draft"""
        try:
            update_data = {
                "subject": f"Updated Test Draft {datetime.now().strftime('%H:%M:%S')}",
                "body": "This draft has been updated by the test script.",
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
        """Test deleting a draft"""
        try:
            response = self.session.delete(f"{BASE_URL}/drafts/{draft_id}?sync_with_gmail=false")
            print(f"🔍 Delete draft: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Draft deleted: {data.get('message')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Delete draft error: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all draft tests"""
        print("🚀 Starting Draft Functionality Tests")
        print("=" * 50)
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return
        
        # Test 2: Login
        if not self.login():
            print("❌ Login failed - stopping tests")
            return
        
        # Test 3: List drafts (initial)
        print("\n📋 Testing initial draft list...")
        self.test_list_drafts()
        
        # Test 4: Create draft
        print("\n📝 Testing draft creation...")
        draft_id = self.test_create_draft()
        if not draft_id:
            print("❌ Draft creation failed - stopping tests")
            return
        
        # Test 5: Get specific draft
        print("\n🔍 Testing draft retrieval...")
        if not self.test_get_draft(draft_id):
            print("❌ Draft retrieval failed")
        
        # Test 6: Update draft
        print("\n✏️ Testing draft update...")
        if not self.test_update_draft(draft_id):
            print("❌ Draft update failed")
        
        # Test 7: List drafts (after creation)
        print("\n📋 Testing draft list after creation...")
        self.test_list_drafts()
        
        # Test 8: Delete draft
        print("\n🗑️ Testing draft deletion...")
        if not self.test_delete_draft(draft_id):
            print("❌ Draft deletion failed")
        
        print("\n" + "=" * 50)
        print("✅ Draft functionality tests completed!")

if __name__ == "__main__":
    tester = DraftTester()
    tester.run_tests()