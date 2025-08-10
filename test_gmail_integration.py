#!/usr/bin/env python3
"""
Test Gmail API integration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.infrastructure.di.container import get_container

async def test_gmail_integration():
    """Test Gmail API integration"""
    print("🚀 Testing Gmail API Integration")
    print("=" * 50)
    
    try:
        # Get container and services
        container = get_container()
        oauth_repository = container.oauth_repository()
        gmail_service = container.gmail_service()
        
        # Test user email (replace with actual user email)
        test_user_email = "natnaelmalike@gmail.com"  # Your actual email
        
        print(f"🔍 Testing Gmail integration for user: {test_user_email}")
        
        # Find OAuth session
        oauth_session = await oauth_repository.find_by_user_email(test_user_email)
        
        if not oauth_session:
            print(f"❌ No OAuth session found for user: {test_user_email}")
            print("Please log in through the web interface first.")
            return
        
        print(f"✅ Found OAuth session: {oauth_session.id}")
        print(f"📧 User email: {oauth_session.user_info.email}")
        print(f"👤 User name: {oauth_session.user_info.name}")
        
        # Test token
        token = oauth_session.token
        print(f"\n🔍 Token Status:")
        print(f"   - Access token: {token.access_token[:20]}...")
        print(f"   - Refresh token: {'Present' if token.refresh_token else 'Missing'}")
        print(f"   - Expires at: {token.expires_at}")
        print(f"   - Is expired: {token.is_expired()}")
        print(f"   - Expires in: {token.expires_in_seconds()} seconds")
        
        # Test Gmail API - Send a test email
        print(f"\n📧 Testing Gmail API - Send Email:")
        try:
            success = await gmail_service.send_email_via_gmail(
                oauth_token=token,
                sender_email=test_user_email,
                recipients=[test_user_email],  # Send to yourself
                subject=f"Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                body="This is a test email sent via Gmail API to verify the integration is working.",
                html_body="<p>This is a <strong>test email</strong> sent via Gmail API to verify the integration is working.</p>"
            )
            
            if success:
                print("✅ Gmail API send test SUCCESSFUL!")
                print("   Check your email inbox for the test message.")
            else:
                print("❌ Gmail API send test FAILED!")
                
        except Exception as e:
            print(f"❌ Gmail API send test ERROR: {str(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
        
        print(f"\n" + "=" * 50)
        print(f"🔍 Gmail integration test complete")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_gmail_integration())