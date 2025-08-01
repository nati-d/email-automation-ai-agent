#!/usr/bin/env python3
"""
Test script to verify session expiration is set to 30 days
"""

import asyncio
from datetime import datetime, timedelta
from app.infrastructure.di.container import Container
from app.application.use_cases.oauth_use_cases import GetOAuthUserInfoUseCase

async def test_session_expiration():
    """Test that session expiration is set to 30 days"""
    print("🧪 Testing Session Expiration Configuration")
    print("=" * 50)
    
    # Get container and use case
    container = Container()
    use_case = container.oauth_user_info_use_case()
    
    # Test with a sample session ID (you'll need to replace this with a real one)
    session_id = input("Enter a valid session ID to test: ").strip()
    
    if not session_id:
        print("❌ No session ID provided. Skipping test.")
        return
    
    try:
        print(f"🔍 Testing session: {session_id[:20]}...")
        
        # Get session info
        result = await use_case.execute(session_id)
        
        # Extract expiration info
        session_info = result.get("session_info", {})
        expires_in_seconds = session_info.get("token_expires_in", 0)
        
        # Calculate days
        days_remaining = expires_in_seconds / (24 * 60 * 60)
        hours_remaining = expires_in_seconds / (60 * 60)
        
        print(f"✅ Session Info:")
        print(f"   - Expires in: {expires_in_seconds} seconds")
        print(f"   - Days remaining: {days_remaining:.1f} days")
        print(f"   - Hours remaining: {hours_remaining:.1f} hours")
        print(f"   - Provider: {session_info.get('provider', 'Unknown')}")
        print(f"   - Active: {session_info.get('session_active', False)}")
        
        # Check if it's close to 30 days
        expected_seconds = 30 * 24 * 60 * 60  # 30 days
        tolerance = 24 * 60 * 60  # 1 day tolerance
        
        if abs(expires_in_seconds - expected_seconds) <= tolerance:
            print(f"✅ SUCCESS: Session expiration is set to approximately 30 days!")
        else:
            print(f"⚠️  WARNING: Session expiration is {days_remaining:.1f} days (expected ~30 days)")
            
        # Show user info
        user = result.get("user", {})
        if user:
            print(f"👤 User: {user.get('name', 'Unknown')} ({user.get('email', 'Unknown')})")
        
    except Exception as e:
        print(f"❌ Error testing session: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_session_expiration()) 