#!/usr/bin/env python3
"""
Debug script to analyze OAuth token expiration issues
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.infrastructure.di.container import get_container

async def debug_token_issue():
    """Debug OAuth token expiration issues"""
    print("🔍 Starting OAuth Token Debug Analysis")
    print("=" * 60)
    
    try:
        # Get container and repositories
        container = get_container()
        oauth_repository = container.oauth_repository()
        gmail_service = container.gmail_service()
        
        # Test user email (replace with actual user email)
        test_user_email = "test@example.com"  # Replace with actual user email
        
        print(f"🔍 Looking for OAuth session for user: {test_user_email}")
        
        # Find OAuth session
        oauth_session = await oauth_repository.find_by_user_email(test_user_email)
        
        if not oauth_session:
            print(f"❌ No OAuth session found for user: {test_user_email}")
            return
        
        print(f"✅ Found OAuth session: {oauth_session.id}")
        print(f"📧 User email: {oauth_session.user_info.email}")
        print(f"👤 User name: {oauth_session.user_info.name}")
        print(f"🔑 Session active: {oauth_session.is_active}")
        
        # Analyze token
        token = oauth_session.token
        print(f"\n🔍 Token Analysis:")
        print(f"   - Access token: {token.access_token[:20]}...")
        print(f"   - Refresh token: {'Present' if token.refresh_token else 'Missing'}")
        if token.refresh_token:
            print(f"   - Refresh token: {token.refresh_token[:20]}...")
        print(f"   - Token type: {token.token_type}")
        print(f"   - Scope: {token.scope}")
        print(f"   - Expires at: {token.expires_at}")
        print(f"   - Current time: {datetime.utcnow()}")
        print(f"   - Is expired: {token.is_expired()}")
        print(f"   - Expires in seconds: {token.expires_in_seconds()}")
        print(f"   - Expires in minutes: {token.expires_in_seconds() / 60:.1f}")
        print(f"   - Expires in hours: {token.expires_in_seconds() / 3600:.1f}")
        
        # Test token refresh
        print(f"\n🔄 Testing Token Refresh:")
        try:
            credentials = await gmail_service._create_and_refresh_credentials(
                oauth_session, oauth_repository
            )
            print(f"✅ Token refresh test completed successfully")
            print(f"   - New credentials token: {credentials.token[:20]}...")
            print(f"   - New credentials expiry: {credentials.expiry}")
            
            # Check if session was updated
            updated_session = await oauth_repository.find_by_user_email(test_user_email)
            if updated_session:
                updated_token = updated_session.token
                print(f"✅ Updated session retrieved from database")
                print(f"   - Updated access token: {updated_token.access_token[:20]}...")
                print(f"   - Updated expires at: {updated_token.expires_at}")
                print(f"   - Updated is expired: {updated_token.is_expired()}")
                print(f"   - Updated expires in seconds: {updated_token.expires_in_seconds()}")
            else:
                print(f"❌ Could not retrieve updated session from database")
                
        except Exception as e:
            print(f"❌ Token refresh test failed: {str(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
        
        print(f"\n" + "=" * 60)
        print(f"🔍 Debug analysis complete")
        
    except Exception as e:
        print(f"❌ Debug script failed: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_token_issue())