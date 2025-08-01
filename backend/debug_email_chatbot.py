"""
Debug Email Chatbot

Script to debug the email chatbot functionality.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.infrastructure.di.container import get_container
from app.application.use_cases.email_chatbot_use_case import EmailChatbotUseCase


async def debug_email_chatbot():
    """Debug the email chatbot functionality"""
    print("🔧 DEBUGGING EMAIL CHATBOT")
    print("=" * 50)
    
    try:
        # Get container
        container = get_container()
        print("✅ Container created")
        
        # Get use case
        use_case = container.email_chatbot_use_case()
        print("✅ Email chatbot use case created")
        
        # Test user email
        test_user_email = "test@example.com"
        
        # Test 1: Get chatbot info
        print("\n1️⃣ Testing get_email_chatbot_info...")
        info = await use_case.get_email_chatbot_info(test_user_email)
        print(f"✅ Info: {info}")
        
        # Test 2: Test system instruction
        print("\n2️⃣ Testing system instruction...")
        system_instruction = use_case._get_system_instruction(test_user_email)
        print(f"✅ System instruction length: {len(system_instruction)}")
        print(f"✅ System instruction preview: {system_instruction[:200]}...")
        
        # Test 3: Test tools
        print("\n3️⃣ Testing tools...")
        tools = use_case._get_email_tools(test_user_email)
        print(f"✅ Number of tools: {len(tools)}")
        for i, tool in enumerate(tools):
            print(f"   Tool {i+1}: {tool['function']['name']}")
        
        # Test 4: Test search emails function directly
        print("\n4️⃣ Testing _search_emails function directly...")
        try:
            result = await use_case._search_emails({"query": "amazon"}, test_user_email)
            print(f"✅ Search result: {result}")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Test 5: Test full chat message
        print("\n5️⃣ Testing full chat message...")
        try:
            result = await use_case.send_email_chat_message("do i have any email related to amazon", test_user_email)
            print(f"✅ Chat result: {result}")
        except Exception as e:
            print(f"❌ Chat error: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"❌ FULL TRACEBACK: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(debug_email_chatbot()) 