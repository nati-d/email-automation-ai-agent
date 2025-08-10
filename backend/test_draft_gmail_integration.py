#!/usr/bin/env python3
"""
Test script to verify draft Gmail integration works with the working API
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

class DraftGmailTester:
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
    
    def test_create_draft_with_gmail_sync(self):
        """Test creating a draft with Gmail sync using working API"""
        try:
            draft_data = {
                "recipients": ["recipient@example.com"],
                "subject": f"Test Gmail Draft {datetime.now().strftime('%H:%M:%S')}",
                "body": "This is a test draft created with Gmail sync using the working API.",
                "sync_with_gmail": True  # Enable Gmail sync
            }
            
            response = self.session.post(f"{BASE_URL}/drafts", json=draft_data)
            print(f"🔍 Create draft with Gmail sync: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                draft_id = data.get("id")
                gmail_synced = data.get("metadata", {}).get("synced_with_gmail", False)
                print(f"   ✅ Draft created: {draft_id}")
                print(f"   📧 Gmail synced: {gmail_synced}")
                print(f"   Subject: {data.get('subject')}")
                return draft_id
            else:
                print(f"   ❌ Failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Create draft error: {str(e)}")
            return None
    
    def test_send_draft_with_gmail(self, draft_id):
        """Test sending a draft using working Gmail API"""
        try:
            response = self.session.post(f"{BASE_URL}/drafts/{draft_id}/send")
            print(f"🔍 Send draft via Gmail: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Draft sent successfully via Gmail!")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Send draft error: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all draft Gmail integration tests"""
        print("🚀 Starting Draft Gmail Integration Tests")
        print("=" * 50)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return
        
        # Test 1: Create draft with Gmail sync
        print("\n📝 Test 1: Create Draft with Gmail Sync")
        draft_id = self.test_create_draft_with_gmail_sync()
        
        if draft_id:
            # Test 2: Send draft via Gmail
            print("\n📤 Test 2: Send Draft via Gmail")
            self.test_send_draft_with_gmail(draft_id)
        
        print("\n" + "=" * 50)
        print("✅ Draft Gmail Integration Tests Complete")

if __name__ == "__main__":
    tester = DraftGmailTester()
    tester.run_tests()