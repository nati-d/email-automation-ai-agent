#!/usr/bin/env python3
"""
Quick Test for Email Summarization

This script tests the email summarization functionality without requiring
a full server setup or authentication.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from infrastructure.config.settings import Settings
from infrastructure.external_services.llm_service import LLMService
from domain.entities.email import Email
from domain.value_objects.email_address import EmailAddress


async def test_llm_service():
    """Test the LLM service directly"""
    print("🧪 Testing LLM Service...")
    
    # Check if API key is available
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("   Please set GEMINI_API_KEY to test email summarization")
        return False
    
    try:
        # Initialize settings and LLM service
        settings = Settings()
        llm_service = LLMService(settings)
        
        # Test health check
        health_result = llm_service.health_check()
        print(f"✅ LLM Service Health: {health_result.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Service test failed: {e}")
        return False


def test_email_entity():
    """Test the Email entity with summarization fields"""
    print("\n🧪 Testing Email Entity...")
    
    try:
        # Create email addresses
        sender = EmailAddress.create("sender@example.com")
        recipient = EmailAddress.create("recipient@example.com")
        
        # Create email entity
        email = Email(
            sender=sender,
            recipients=[recipient],
            subject="Test Email Subject",
            body="This is a test email body with some content to summarize."
        )
        
        print(f"✅ Email created: {email.subject}")
        
        # Test summarization methods
        email.set_summarization(
            summary="This is a test email about testing",
            main_concept="Testing",
            sentiment="neutral",
            key_topics=["testing", "email", "example"]
        )
        
        print(f"✅ Summarization set successfully")
        print(f"   Summary: {email.summary}")
        print(f"   Main Concept: {email.main_concept}")
        print(f"   Sentiment: {email.sentiment}")
        print(f"   Key Topics: {email.key_topics}")
        print(f"   Has Summarization: {email.has_summarization()}")
        
        # Test get_summarization_data
        summary_data = email.get_summarization_data()
        print(f"✅ Summary data: {summary_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email entity test failed: {e}")
        return False


async def test_email_summarization():
    """Test email summarization with LLM service"""
    print("\n🧪 Testing Email Summarization...")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Skipping LLM test - no API key")
        return False
    
    try:
        # Initialize services
        settings = Settings()
        llm_service = LLMService(settings)
        
        # Test email content
        test_email_content = """
        Hi there,
        
        I hope this email finds you well. I wanted to follow up on our meeting from last week
        regarding the new project proposal. The team has been working hard on the initial
        design and we're excited to share our progress with you.
        
        We've identified several key areas that need attention:
        1. User interface improvements
        2. Performance optimization
        3. Security enhancements
        
        Please let me know if you have any questions or if you'd like to schedule another
        meeting to discuss the details further.
        
        Best regards,
        John Doe
        """
        
        print(f"📧 Test email content length: {len(test_email_content)} characters")
        
        # Test summarization
        result = llm_service.summarize_email(
            email_content=test_email_content,
            email_subject="Project Update - Follow Up",
            sender="john.doe@company.com",
            recipient="manager@company.com"
        )
        
        print(f"✅ Summarization completed:")
        print(f"   Summary: {result.get('summary', 'N/A')}")
        print(f"   Main Concept: {result.get('main_concept', 'N/A')}")
        print(f"   Sentiment: {result.get('sentiment', 'N/A')}")
        print(f"   Key Topics: {result.get('key_topics', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email summarization test failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function"""
    print("🚀 Email Summarization Test")
    print("=" * 50)
    
    # Test 1: LLM Service
    llm_ok = await test_llm_service()
    
    # Test 2: Email Entity
    entity_ok = test_email_entity()
    
    # Test 3: Email Summarization
    summarization_ok = await test_email_summarization()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"LLM Service: {'✅ PASS' if llm_ok else '❌ FAIL'}")
    print(f"Email Entity: {'✅ PASS' if entity_ok else '❌ FAIL'}")
    print(f"Email Summarization: {'✅ PASS' if summarization_ok else '❌ FAIL'}")
    
    if llm_ok and entity_ok and summarization_ok:
        print("\n🎉 All tests passed! Email summarization is working correctly.")
        print("\nNext steps:")
        print("1. Start the FastAPI server: python main.py")
        print("2. Test with real emails through the API")
        print("3. Check the documentation: docs/EMAIL_SUMMARIZATION.md")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        if not llm_ok:
            print("   - Make sure GEMINI_API_KEY is set correctly")
        if not entity_ok:
            print("   - Check the Email entity implementation")
        if not summarization_ok:
            print("   - Verify LLM service configuration")


if __name__ == "__main__":
    asyncio.run(main()) 