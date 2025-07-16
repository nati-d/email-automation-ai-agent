#!/usr/bin/env python3
"""
Test /me Endpoint with Bearer Token Authentication

This script demonstrates how to use the /me endpoint with Bearer token authentication.
"""

import requests
import json
from typing import Optional


class MeEndpointTest:
    """Test class for the /me endpoint with Bearer token authentication"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def test_me_without_authentication(self):
        """Test /me endpoint without authentication (should fail)"""
        print("🔓 Testing /me endpoint without authentication...")
        
        try:
            response = requests.get(f"{self.base_url}/api/auth/me")
            print(f"❌ Expected 401, got: {response.status_code}")
            if response.status_code != 401:
                print(f"   Unexpected response: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_me_with_invalid_token(self):
        """Test /me endpoint with invalid Bearer token (should fail)"""
        print("\n🔓 Testing /me endpoint with invalid Bearer token...")
        
        try:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers)
            print(f"❌ Expected 401, got: {response.status_code}")
            if response.status_code != 401:
                print(f"   Unexpected response: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_me_with_valid_session(self, session_id: str):
        """Test /me endpoint with valid Bearer token"""
        print(f"\n✅ Testing /me endpoint with valid Bearer token: {session_id[:10]}...")
        
        try:
            headers = {"Authorization": f"Bearer {session_id}"}
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                session_info = data.get('session_info', {})
                
                print(f"✅ /me endpoint successful!")
                print(f"   👤 User ID: {user.get('id')}")
                print(f"   📧 Email: {user.get('email')}")
                print(f"   🏷️ Name: {user.get('name')}")
                print(f"   🏷️ Role: {user.get('role')}")
                print(f"   🔐 Authenticated: {session_info.get('authenticated')}")
                print(f"   🔐 Auth Method: {session_info.get('authentication_method')}")
            else:
                print(f"❌ /me endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_logout_with_bearer_token(self, session_id: str):
        """Test logout endpoint with Bearer token"""
        print(f"\n🔄 Testing logout endpoint with Bearer token: {session_id[:10]}...")
        
        try:
            headers = {"Authorization": f"Bearer {session_id}"}
            response = requests.post(f"{self.base_url}/api/auth/logout", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Logout successful!")
                print(f"   🚪 Success: {data.get('success')}")
                print(f"   🔐 Token Revoked: {data.get('token_revoked')}")
                print(f"   📝 Message: {data.get('message')}")
                if data.get('warning'):
                    print(f"   ⚠️ Warning: {data.get('warning')}")
            else:
                print(f"❌ Logout failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_refresh_with_bearer_token(self, session_id: str):
        """Test refresh endpoint with Bearer token"""
        print(f"\n🔄 Testing refresh endpoint with Bearer token: {session_id[:10]}...")
        
        try:
            headers = {"Authorization": f"Bearer {session_id}"}
            response = requests.post(f"{self.base_url}/api/auth/refresh", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token refresh successful!")
                print(f"   🔐 Access Token: {data.get('access_token', '')[:20]}...")
                print(f"   ⏰ Expires In: {data.get('expires_in')} seconds")
                print(f"   📝 Message: {data.get('message')}")
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def run_comprehensive_test(self, session_id: str):
        """Run comprehensive test of all Bearer token endpoints"""
        print("🚀 Running comprehensive Bearer token authentication test...")
        print("=" * 60)
        
        # Test without authentication
        self.test_me_without_authentication()
        
        # Test with invalid token
        self.test_me_with_invalid_token()
        
        # Test with valid session
        self.test_me_with_valid_session(session_id)
        
        # Test refresh endpoint
        self.test_refresh_with_bearer_token(session_id)
        
        # Test logout endpoint
        self.test_logout_with_bearer_token(session_id)
        
        print("\n" + "=" * 60)
        print("✅ Comprehensive test completed!")


def main():
    """Main function to run the test"""
    print("🧪 /me Endpoint Bearer Token Authentication Test")
    print("=" * 60)
    
    # Create test instance
    test = MeEndpointTest()
    
    # Get session ID from user
    session_id = input("Enter your session ID (or press Enter to skip): ").strip()
    
    if not session_id:
        print("⚠️ No session ID provided. Running tests without authentication only...")
        test.test_me_without_authentication()
        test.test_me_with_invalid_token()
    else:
        # Run comprehensive test
        test.run_comprehensive_test(session_id)


if __name__ == "__main__":
    main() 