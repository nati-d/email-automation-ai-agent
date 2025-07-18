#!/usr/bin/env python3
"""
Test Add Another Account

This script tests the add_another_account endpoint functionality.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_SESSION_ID = "your_session_id_here"  # Replace with actual session ID

class AddAnotherAccountTester:
    """Test class for add another account functionality"""
    
    def __init__(self, base_url: str, session_id: str):
        self.base_url = base_url
        self.session_id = session_id
        self.headers = {"Authorization": f"Bearer {session_id}"}
    
    async def test_get_current_user(self) -> dict:
        """Test getting current user info"""
        print(f"\n👤 Testing get_current_user...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/oauth/user-info",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Current user: {result.get('email', 'N/A')}")
                print(f"✅ User name: {result.get('name', 'N/A')}")
                return result
    
    async def test_get_my_emails(self) -> dict:
        """Test getting emails for the current user"""
        print(f"\n📧 Testing get_my_emails (before adding account)...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails?limit=5",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Found {result.get('total_count', 0)} emails")
                
                # Show account ownership info for existing emails
                emails = result.get('emails', [])
                for i, email in enumerate(emails[:3]):
                    print(f"   Email {i+1}:")
                    print(f"     Subject: {email.get('subject', 'N/A')[:50]}...")
                    print(f"     Account Owner: {email.get('account_owner', 'N/A')}")
                    print(f"     Email Holder: {email.get('email_holder', 'N/A')}")
                
                return result
    
    async def test_add_another_account(self, code: str, state: str) -> dict:
        """Test adding another email account"""
        print(f"\n➕ Testing add_another_account...")
        print(f"   Code: {code[:20] if code else 'None'}...")
        print(f"   State: {state[:20] if state else 'None'}...")
        
        data = {
            "code": code,
            "state": state
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/oauth/add-another-account",
                headers=self.headers,
                json=data
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Success: {result.get('success', False)}")
                
                if result.get('success'):
                    account_added = result.get('account_added', {})
                    existing_user = result.get('existing_user', {})
                    email_import = result.get('email_import', {})
                    
                    print(f"✅ Account added successfully:")
                    print(f"   - New account email: {account_added.get('email', 'N/A')}")
                    print(f"   - New account name: {account_added.get('name', 'N/A')}")
                    print(f"   - Existing user: {existing_user.get('email', 'N/A')}")
                    print(f"   - Emails imported: {email_import.get('emails_imported', 0)}")
                else:
                    print(f"❌ Failed to add account:")
                    print(f"   - Error: {result.get('error', 'N/A')}")
                    print(f"   - Message: {result.get('message', 'N/A')}")
                
                return result
    
    async def test_get_my_emails_after_add(self) -> dict:
        """Test getting emails after adding another account"""
        print(f"\n📧 Testing get_my_emails (after adding account)...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails?limit=10",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Found {result.get('total_count', 0)} emails")
                
                # Show account ownership info for all emails
                emails = result.get('emails', [])
                print(f"📊 Email account ownership breakdown:")
                
                account_owners = {}
                email_holders = {}
                
                for email in emails:
                    account_owner = email.get('account_owner', 'N/A')
                    email_holder = email.get('email_holder', 'N/A')
                    
                    account_owners[account_owner] = account_owners.get(account_owner, 0) + 1
                    email_holders[email_holder] = email_holders.get(email_holder, 0) + 1
                
                print(f"   Account Owners:")
                for owner, count in account_owners.items():
                    print(f"     - {owner}: {count} emails")
                
                print(f"   Email Holders:")
                for holder, count in email_holders.items():
                    print(f"     - {holder}: {count} emails")
                
                return result
    
    async def test_get_oauth_url(self) -> dict:
        """Test getting OAuth URL for adding another account"""
        print(f"\n🔗 Testing get_oauth_url...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/oauth/login",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Authorization URL: {result.get('authorization_url', 'N/A')[:100]}...")
                print(f"✅ State: {result.get('state', 'N/A')}")
                return result
    
    async def run_all_tests(self):
        """Run all tests"""
        print(f"🧪 Starting Add Another Account Tests")
        print(f"   API Base URL: {self.base_url}")
        print(f"   Session ID: {self.session_id[:20]}...")
        
        try:
            # Test getting current user
            current_user = await self.test_get_current_user()
            
            # Test getting emails before adding account
            await self.test_get_my_emails()
            
            # Test getting OAuth URL (for manual testing)
            oauth_result = await self.test_get_oauth_url()
            
            print(f"\n📋 Manual Testing Instructions:")
            print(f"1. Open this URL in your browser:")
            print(f"   {oauth_result.get('authorization_url', 'N/A')}")
            print(f"2. Complete the OAuth flow for a different Gmail account")
            print(f"3. Copy the 'code' and 'state' from the callback URL")
            print(f"4. Update the test_add_another_account call below")
            
            # Uncomment and update with actual code and state for testing
            # await self.test_add_another_account("your_code_here", "your_state_here")
            
            # Test getting emails after adding account (if account was added)
            # await self.test_get_my_emails_after_add()
            
            print(f"\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")


async def main():
    """Main function"""
    print("🚀 Add Another Account Test Runner")
    print("=" * 50)
    
    # Check if session ID is provided
    if TEST_SESSION_ID == "your_session_id_here":
        print("❌ Please update TEST_SESSION_ID with a valid session ID")
        print("   You can get a session ID by running the OAuth flow")
        return
    
    # Create tester and run tests
    tester = AddAnotherAccountTester(API_BASE_URL, TEST_SESSION_ID)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 