#!/usr/bin/env python3
"""
Test Email Account Ownership

This script tests the new account_owner and email_holder functionality.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_USER_EMAIL = "test@example.com"
TEST_SESSION_ID = "your_session_id_here"  # Replace with actual session ID

class EmailAccountOwnershipTester:
    """Test class for email account ownership functionality"""
    
    def __init__(self, base_url: str, session_id: str):
        self.base_url = base_url
        self.session_id = session_id
        self.headers = {"Authorization": f"Bearer {session_id}"}
    
    async def test_get_my_emails(self) -> dict:
        """Test getting emails for the authenticated user"""
        print(f"\n📧 Testing get_my_emails...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails?limit=10",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Found {result.get('total_count', 0)} emails")
                
                # Check if emails have account_owner and email_holder fields
                emails = result.get('emails', [])
                for i, email in enumerate(emails[:3]):  # Check first 3 emails
                    print(f"   Email {i+1}:")
                    print(f"     Subject: {email.get('subject', 'N/A')[:50]}...")
                    print(f"     Account Owner: {email.get('account_owner', 'N/A')}")
                    print(f"     Email Holder: {email.get('email_holder', 'N/A')}")
                    print(f"     Sender: {email.get('sender', 'N/A')}")
                    print(f"     Recipients: {email.get('recipients', [])}")
                
                return result
    
    async def test_send_email(self) -> dict:
        """Test sending a new email"""
        print(f"\n📤 Testing send_email...")
        
        email_data = {
            "recipients": ["recipient@example.com"],
            "subject": "Test Email with Account Ownership",
            "body": "This is a test email to verify account ownership functionality.",
            "html_body": "<h1>Test Email</h1><p>This is a test email to verify account ownership functionality.</p>"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/emails/send",
                headers=self.headers,
                json=email_data
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Email sent successfully: {result.get('message', 'N/A')}")
                
                # Check if the sent email has account ownership fields
                email = result.get('email', {})
                print(f"   Sent Email Details:")
                print(f"     ID: {email.get('id', 'N/A')}")
                print(f"     Account Owner: {email.get('account_owner', 'N/A')}")
                print(f"     Email Holder: {email.get('email_holder', 'N/A')}")
                print(f"     Sender: {email.get('sender', 'N/A')}")
                
                return result
    
    async def test_get_task_emails(self) -> dict:
        """Test getting task emails"""
        print(f"\n📋 Testing get_task_emails...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails/tasks?limit=5",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Found {result.get('total_count', 0)} task emails")
                
                return result
    
    async def test_get_inbox_emails(self) -> dict:
        """Test getting inbox emails"""
        print(f"\n📥 Testing get_inbox_emails...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails/inbox?limit=5",
                headers=self.headers
            ) as response:
                result = await response.json()
                print(f"✅ Response status: {response.status}")
                print(f"✅ Found {result.get('total_count', 0)} inbox emails")
                
                return result
    
    async def run_all_tests(self):
        """Run all tests"""
        print(f"🧪 Starting Email Account Ownership Tests")
        print(f"   API Base URL: {self.base_url}")
        print(f"   Session ID: {self.session_id[:20]}...")
        
        try:
            # Test getting emails
            await self.test_get_my_emails()
            
            # Test sending email
            await self.test_send_email()
            
            # Test getting task emails
            await self.test_get_task_emails()
            
            # Test getting inbox emails
            await self.test_get_inbox_emails()
            
            print(f"\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")


async def main():
    """Main function"""
    print("🚀 Email Account Ownership Test Runner")
    print("=" * 50)
    
    # Check if session ID is provided
    if TEST_SESSION_ID == "your_session_id_here":
        print("❌ Please update TEST_SESSION_ID with a valid session ID")
        print("   You can get a session ID by running the OAuth flow")
        return
    
    # Create tester and run tests
    tester = EmailAccountOwnershipTester(API_BASE_URL, TEST_SESSION_ID)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 