#!/usr/bin/env python3
"""
Authentication Middleware Example

This script demonstrates how to use the authentication middleware
with the Email Agent API.
"""

import requests
import json
from typing import Optional


class AuthMiddlewareExample:
    """Example class demonstrating authentication middleware usage"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def test_without_authentication(self):
        """Test endpoints that don't require authentication"""
        print("🔓 Testing endpoints without authentication...")
        
        # Test public endpoint (optional auth)
        try:
            response = requests.get(f"{self.base_url}/api/emails/public")
            print(f"✅ Public endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📧 Found {len(data.get('emails', []))} public emails")
        except Exception as e:
            print(f"❌ Public endpoint error: {e}")
        
        # Test session status (optional auth)
        try:
            response = requests.get(f"{self.base_url}/api/auth-test/session-status")
            print(f"✅ Session status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🔐 Session status: {data.get('status')}")
        except Exception as e:
            print(f"❌ Session status error: {e}")
        
        # Test optional auth endpoint
        try:
            response = requests.get(f"{self.base_url}/api/auth-test/optional")
            print(f"✅ Optional auth endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   👤 Auth status: {data.get('authentication_status')}")
        except Exception as e:
            print(f"❌ Optional auth error: {e}")
    
    def test_with_invalid_session(self):
        """Test endpoints with invalid session ID"""
        print("\n🔒 Testing endpoints with invalid session...")
        
        invalid_session_id = "invalid-session-id"
        
        # Test protected endpoint with invalid session
        try:
            headers = {"X-Session-ID": invalid_session_id}
            response = requests.get(f"{self.base_url}/api/emails/my-emails", headers=headers)
            print(f"❌ Protected endpoint with invalid session: {response.status_code}")
            if response.status_code == 401:
                data = response.json()
                print(f"   🚫 Error: {data.get('detail', {}).get('error')}")
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
        
        # Test auth test endpoint with invalid session
        try:
            headers = {"X-Session-ID": invalid_session_id}
            response = requests.get(f"{self.base_url}/api/auth-test/protected", headers=headers)
            print(f"❌ Auth test endpoint with invalid session: {response.status_code}")
            if response.status_code == 401:
                data = response.json()
                print(f"   🚫 Error: {data.get('detail', {}).get('error')}")
        except Exception as e:
            print(f"❌ Auth test error: {e}")
    
    def test_with_valid_session(self, session_id: str):
        """Test endpoints with valid session ID"""
        print(f"\n✅ Testing endpoints with valid session: {session_id[:10]}...")
        
        # Test protected endpoint with valid session
        try:
            headers = {"X-Session-ID": session_id}
            response = requests.get(f"{self.base_url}/api/emails/my-emails", headers=headers)
            print(f"✅ Protected endpoint with valid session: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📧 Found {len(data.get('emails', []))} user emails")
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
        
        # Test auth test endpoint with valid session
        try:
            headers = {"X-Session-ID": session_id}
            response = requests.get(f"{self.base_url}/api/auth-test/protected", headers=headers)
            print(f"✅ Auth test endpoint with valid session: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                print(f"   👤 User: {user.get('name')} ({user.get('email')})")
        except Exception as e:
            print(f"❌ Auth test error: {e}")
        
        # Test user info endpoint
        try:
            headers = {"X-Session-ID": session_id}
            response = requests.get(f"{self.base_url}/api/auth-test/user-info", headers=headers)
            print(f"✅ User info endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   👤 User ID: {data.get('user_id')}")
                print(f"   📧 Email: {data.get('email')}")
                print(f"   🏷️ Role: {data.get('role')}")
        except Exception as e:
            print(f"❌ User info error: {e}")
        
        # Test session status with valid session
        try:
            headers = {"X-Session-ID": session_id}
            response = requests.get(f"{self.base_url}/api/auth-test/session-status", headers=headers)
            print(f"✅ Session status with valid session: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🔐 Status: {data.get('status')}")
                print(f"   📧 Email: {data.get('user_email')}")
        except Exception as e:
            print(f"❌ Session status error: {e}")
    
    def test_query_parameter_auth(self, session_id: str):
        """Test authentication using query parameter instead of header"""
        print(f"\n🔗 Testing authentication with query parameter...")
        
        # Test protected endpoint with query parameter
        try:
            params = {"session_id": session_id}
            response = requests.get(f"{self.base_url}/api/auth-test/protected", params=params)
            print(f"✅ Protected endpoint with query param: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                print(f"   👤 User: {user.get('name')} ({user.get('email')})")
        except Exception as e:
            print(f"❌ Query param auth error: {e}")
    
    def run_all_tests(self, session_id: Optional[str] = None):
        """Run all authentication middleware tests"""
        print("🚀 Starting Authentication Middleware Tests")
        print("=" * 50)
        
        # Test without authentication
        self.test_without_authentication()
        
        # Test with invalid session
        self.test_with_invalid_session()
        
        # Test with valid session (if provided)
        if session_id:
            self.test_with_valid_session(session_id)
            self.test_query_parameter_auth(session_id)
        else:
            print(f"\n⚠️ Skipping valid session tests - no session ID provided")
            print("   To test with valid session, run:")
            print("   python examples/auth_middleware_example.py YOUR_SESSION_ID")
        
        print("\n" + "=" * 50)
        print("✅ Authentication Middleware Tests Complete")


def main():
    """Main function to run the example"""
    import sys
    
    # Get session ID from command line argument
    session_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create example instance
    example = AuthMiddlewareExample()
    
    # Run tests
    example.run_all_tests(session_id)


if __name__ == "__main__":
    main() 