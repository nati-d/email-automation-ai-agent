#!/usr/bin/env python3
"""
Email Summarization Example

This script demonstrates the email summarization functionality using the Email Agent API.
It shows how to:
1. Summarize individual emails
2. Summarize multiple emails in batch
3. View summarization results

Requirements:
- FastAPI server running on http://localhost:8000
- Valid GEMINI_API_KEY in environment
- Authenticated user session
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000/api"
SESSION_ID = None  # Will be set after authentication


async def authenticate_user() -> str:
    """Authenticate user and get session ID"""
    print("🔐 Authenticating user...")
    
    # This is a simplified example - in real usage, you'd go through the OAuth flow
    # For testing, you can use an existing session ID or implement the full OAuth flow
    
    # Option 1: Use existing session ID (if you have one)
    existing_session = os.getenv("EMAIL_AGENT_SESSION_ID")
    if existing_session:
        print(f"✅ Using existing session ID: {existing_session[:20]}...")
        return existing_session
    
    # Option 2: Implement OAuth flow (simplified)
    print("⚠️ No existing session found. Please implement OAuth flow or set EMAIL_AGENT_SESSION_ID")
    print("   You can get a session ID by:")
    print("   1. Going through the OAuth flow in the web interface")
    print("   2. Setting EMAIL_AGENT_SESSION_ID environment variable")
    print("   3. Or implementing the full OAuth flow here")
    
    # For demo purposes, return a placeholder
    return "demo_session_id"


async def get_user_emails(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's emails"""
    print(f"📧 Fetching user emails (limit: {limit})...")
    
    headers = {"Authorization": f"Bearer {session_id}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/emails?limit={limit}", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                emails = data.get("emails", [])
                print(f"✅ Found {len(emails)} emails")
                return emails
            else:
                print(f"❌ Failed to fetch emails: {response.status}")
                error_data = await response.json()
                print(f"   Error: {error_data}")
                return []


async def summarize_single_email(session_id: str, email_id: str) -> Dict[str, Any]:
    """Summarize a single email"""
    print(f"🤖 Summarizing email: {email_id}")
    
    headers = {"Authorization": f"Bearer {session_id}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}/emails/{email_id}/summarize", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Email summarized successfully")
                return data
            else:
                print(f"❌ Failed to summarize email: {response.status}")
                error_data = await response.json()
                print(f"   Error: {error_data}")
                return {}


async def summarize_multiple_emails(session_id: str, email_ids: List[str]) -> Dict[str, Any]:
    """Summarize multiple emails in batch"""
    print(f"🤖 Summarizing {len(email_ids)} emails in batch...")
    
    headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    
    payload = email_ids
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}/emails/summarize-batch", 
                               headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Batch summarization completed")
                return data
            else:
                print(f"❌ Failed to summarize emails: {response.status}")
                error_data = await response.json()
                print(f"   Error: {error_data}")
                return {}


def display_email_summary(email: Dict[str, Any]) -> None:
    """Display email summary in a formatted way"""
    print(f"\n📧 Email: {email.get('subject', 'No subject')}")
    print(f"   From: {email.get('sender', 'Unknown')}")
    print(f"   To: {', '.join(email.get('recipients', []))}")
    print(f"   Status: {email.get('status', 'Unknown')}")
    
    # Check if email has summarization
    summary = email.get('summary')
    main_concept = email.get('main_concept')
    sentiment = email.get('sentiment')
    key_topics = email.get('key_topics', [])
    summarized_at = email.get('summarized_at')
    
    if summary and main_concept and sentiment:
        print(f"   🤖 AI Summary:")
        print(f"      Summary: {summary}")
        print(f"      Main Concept: {main_concept}")
        print(f"      Sentiment: {sentiment}")
        print(f"      Key Topics: {', '.join(key_topics) if key_topics else 'None'}")
        print(f"      Summarized: {summarized_at}")
    else:
        print(f"   ⚠️ No AI summarization available")


def display_summarization_result(result: Dict[str, Any]) -> None:
    """Display summarization result"""
    print(f"\n🤖 Summarization Result:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Message: {result.get('message', 'No message')}")
    
    if result.get('already_summarized'):
        print(f"   Status: Already summarized")
    
    summarization = result.get('summarization', {})
    if summarization:
        print(f"   Summary: {summarization.get('summary', 'N/A')}")
        print(f"   Main Concept: {summarization.get('main_concept', 'N/A')}")
        print(f"   Sentiment: {summarization.get('sentiment', 'N/A')}")
        print(f"   Key Topics: {', '.join(summarization.get('key_topics', []))}")


def display_batch_result(result: Dict[str, Any]) -> None:
    """Display batch summarization result"""
    print(f"\n🤖 Batch Summarization Result:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Total Processed: {result.get('total_processed', 0)}")
    print(f"   Successful: {result.get('successful', 0)}")
    print(f"   Already Summarized: {result.get('already_summarized', 0)}")
    print(f"   Failed: {result.get('failed', 0)}")
    
    errors = result.get('errors', [])
    if errors:
        print(f"   Errors: {len(errors)}")
        for i, error in enumerate(errors[:3]):  # Show first 3 errors
            print(f"     {i+1}. {error}")
        if len(errors) > 3:
            print(f"     ... and {len(errors) - 3} more errors")


async def main():
    """Main function to demonstrate email summarization"""
    print("🚀 Email Summarization Example")
    print("=" * 50)
    
    # Check if Gemini API key is available
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("   Please set GEMINI_API_KEY to use email summarization features")
        return
    
    # Authenticate user
    session_id = await authenticate_user()
    if not session_id or session_id == "demo_session_id":
        print("❌ Authentication failed. Cannot proceed without valid session.")
        return
    
    print(f"✅ Authenticated with session: {session_id[:20]}...")
    
    # Get user's emails
    emails = await get_user_emails(session_id, limit=5)
    if not emails:
        print("❌ No emails found. Cannot demonstrate summarization.")
        return
    
    print(f"\n📧 Found {len(emails)} emails")
    
    # Display emails with their current summarization status
    print("\n" + "=" * 50)
    print("CURRENT EMAILS AND SUMMARIZATION STATUS")
    print("=" * 50)
    
    for i, email in enumerate(emails, 1):
        print(f"\n{i}. ", end="")
        display_email_summary(email)
    
    # Example 1: Summarize a single email
    print("\n" + "=" * 50)
    print("EXAMPLE 1: SUMMARIZE SINGLE EMAIL")
    print("=" * 50)
    
    if emails:
        first_email = emails[0]
        email_id = first_email.get('id')
        
        if email_id:
            result = await summarize_single_email(session_id, email_id)
            display_summarization_result(result)
        else:
            print("❌ No email ID found for summarization")
    
    # Example 2: Summarize multiple emails in batch
    print("\n" + "=" * 50)
    print("EXAMPLE 2: SUMMARIZE MULTIPLE EMAILS IN BATCH")
    print("=" * 50)
    
    # Get email IDs for batch summarization (limit to 3 for demo)
    email_ids = [email.get('id') for email in emails[:3] if email.get('id')]
    
    if email_ids:
        result = await summarize_multiple_emails(session_id, email_ids)
        display_batch_result(result)
    else:
        print("❌ No email IDs found for batch summarization")
    
    # Example 3: Show updated emails with summarization
    print("\n" + "=" * 50)
    print("EXAMPLE 3: UPDATED EMAILS WITH SUMMARIZATION")
    print("=" * 50)
    
    # Fetch emails again to see updated summarization
    updated_emails = await get_user_emails(session_id, limit=5)
    
    for i, email in enumerate(updated_emails, 1):
        print(f"\n{i}. ", end="")
        display_email_summary(email)
    
    print("\n" + "=" * 50)
    print("✅ Email Summarization Example Completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main()) 