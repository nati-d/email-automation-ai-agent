#!/usr/bin/env python3
"""
Test Email Categorization

This script tests the email categorization functionality.
"""

import os
import sys
import asyncio

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from infrastructure.config.settings import Settings
from infrastructure.external_services.llm_service import LLMService
from domain.entities.email import Email, EmailType
from domain.value_objects.email_address import EmailAddress


def test_email_categorization():
    """Test email categorization with different types of emails"""
    print("🧪 Testing Email Categorization")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found!")
        return False
    
    try:
        # Initialize services
        settings = Settings()
        llm_service = LLMService(settings)
        
        # Test emails
        test_emails = [
            {
                "subject": "Action Required: Complete your profile",
                "content": "Hi there, please complete your profile by filling out the required information. This is important for your account setup.",
                "expected": "tasks"
            },
            {
                "subject": "Meeting reminder for tomorrow",
                "content": "Just a reminder that we have a meeting scheduled for tomorrow at 2 PM. Please prepare your presentation.",
                "expected": "tasks"
            },
            {
                "subject": "Weekly newsletter",
                "content": "Here's your weekly newsletter with the latest updates and news from our company. Enjoy reading!",
                "expected": "inbox"
            },
            {
                "subject": "Please review and approve the document",
                "content": "I've prepared the quarterly report. Please review it and let me know if you approve or if any changes are needed.",
                "expected": "tasks"
            },
            {
                "subject": "Happy Birthday!",
                "content": "Wishing you a wonderful birthday! Hope you have a great day filled with joy and celebration.",
                "expected": "inbox"
            }
        ]
        
        results = []
        
        for i, test_email in enumerate(test_emails, 1):
            print(f"\n📧 Test Email {i}: {test_email['subject']}")
            print(f"   Expected: {test_email['expected']}")
            
            try:
                category = llm_service.categorize_email(
                    email_content=test_email['content'],
                    email_subject=test_email['subject'],
                    sender="test@example.com",
                    recipient="user@example.com"
                )
                
                is_correct = category == test_email['expected']
                status = "✅ PASS" if is_correct else "❌ FAIL"
                
                print(f"   Result: {category}")
                print(f"   Status: {status}")
                
                results.append({
                    "test": i,
                    "subject": test_email['subject'],
                    "expected": test_email['expected'],
                    "actual": category,
                    "correct": is_correct
                })
                
            except Exception as e:
                print(f"   Error: {e}")
                results.append({
                    "test": i,
                    "subject": test_email['subject'],
                    "expected": test_email['expected'],
                    "actual": "ERROR",
                    "correct": False
                })
        
        # Summary
        print(f"\n" + "=" * 50)
        print("CATEGORIZATION TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in results if r['correct'])
        total = len(results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        for result in results:
            status = "✅" if result['correct'] else "❌"
            print(f"{status} Test {result['test']}: {result['subject']}")
            print(f"   Expected: {result['expected']}, Got: {result['actual']}")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_email_entity_categorization():
    """Test email entity categorization methods"""
    print(f"\n🧪 Testing Email Entity Categorization")
    print("=" * 50)
    
    try:
        # Create email addresses
        sender = EmailAddress.create("sender@example.com")
        recipient = EmailAddress.create("recipient@example.com")
        
        # Create email entity
        email = Email(
            sender=sender,
            recipients=[recipient],
            subject="Test Email",
            body="This is a test email body."
        )
        
        print(f"✅ Email created: {email.subject}")
        print(f"   Default email type: {email.email_type.value}")
        print(f"   Is inbox: {email.is_inbox_email()}")
        print(f"   Is task: {email.is_task_email()}")
        
        # Test setting as task
        print(f"\n🔧 Setting email as task...")
        email.set_email_type(EmailType.TASKS)
        print(f"   Email type: {email.email_type.value}")
        print(f"   Is inbox: {email.is_inbox_email()}")
        print(f"   Is task: {email.is_task_email()}")
        print(f"   Categorized at: {email.categorized_at}")
        
        # Test setting as inbox
        print(f"\n🔧 Setting email as inbox...")
        email.set_email_type(EmailType.INBOX)
        print(f"   Email type: {email.email_type.value}")
        print(f"   Is inbox: {email.is_inbox_email()}")
        print(f"   Is task: {email.is_task_email()}")
        print(f"   Categorized at: {email.categorized_at}")
        
        # Test categorization data
        print(f"\n🔧 Categorization data:")
        cat_data = email.get_categorization_data()
        print(f"   {cat_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email entity test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Email Categorization Test")
    print("=" * 50)
    
    # Test 1: Email Entity
    entity_ok = test_email_entity_categorization()
    
    # Test 2: LLM Categorization
    llm_ok = test_email_categorization()
    
    # Summary
    print(f"\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Email Entity: {'✅ PASS' if entity_ok else '❌ FAIL'}")
    print(f"LLM Categorization: {'✅ PASS' if llm_ok else '❌ FAIL'}")
    
    if entity_ok and llm_ok:
        print(f"\n🎉 All tests passed! Email categorization is working correctly.")
        print(f"\nNext steps:")
        print(f"1. Start the FastAPI server: python main.py")
        print(f"2. Test with real emails through the API")
        print(f"3. Check the new endpoints:")
        print(f"   - GET /api/emails/tasks - Get task emails")
        print(f"   - GET /api/emails/inbox - Get inbox emails")
    else:
        print(f"\n⚠️ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main() 