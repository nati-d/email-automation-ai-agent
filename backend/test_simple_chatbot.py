"""
Simple Email Chatbot Test

Test basic function calling with Gemini.
"""

import os
import google.generativeai as genai
from typing import Dict, List, Any

# Set up Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

def get_email_tools() -> List[Dict[str, Any]]:
    """Define simple email tools for testing"""
    return [
        {
            "name": "search_emails",
            "description": "Search emails by various criteria",
            "parameters": {
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for subject or content"
                    },
                    "sender": {
                        "type": "string",
                        "description": "Filter by sender email address"
                    }
                }
            }
        }
    ]

def mock_search_emails(args: Dict[str, Any]) -> str:
    """Mock email search function"""
    print(f"🔧 Mock search_emails called with: {args}")
    return f"Found 3 emails matching '{args.get('query', 'unknown')}':\n\n📧 Email 1: Amazon order confirmation\n📧 Email 2: Amazon delivery update\n📧 Email 3: Amazon Prime renewal"

def test_function_calling():
    """Test basic function calling with Gemini"""
    print("🔧 TESTING FUNCTION CALLING")
    print("=" * 50)
    
    try:
        # Create model with tools
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=get_email_tools()
        )
        
        print("✅ Model created with tools")
        
        # Start chat
        chat = model.start_chat()
        print("✅ Chat started")
        
        # Send message
        message = "do i have any email related to amazon"
        print(f"🔧 Sending message: {message}")
        
        response = chat.send_message(message)
        print(f"✅ Response received")
        print(f"🔧 Response type: {type(response)}")
        print(f"🔧 Response attributes: {dir(response)}")
        
        # Check for function calls
        function_calls = []
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        function_calls.append(part.function_call)
                        print(f"🔧 Found function call: {part.function_call.name}")
        
        if hasattr(response, 'function_calls'):
            function_calls.extend(response.function_calls)
            print(f"🔧 Found function calls in response.function_calls")
        
        if function_calls:
            print(f"✅ Found {len(function_calls)} function calls")
            for function_call in function_calls:
                print(f"🔧 Executing: {function_call.name}")
                if function_call.name == "search_emails":
                    result = mock_search_emails(function_call.args)
                    print(f"🔧 Function result: {result}")
                    
                    # Send result back
                    final_response = chat.send_message(result)
                    print(f"✅ Final response: {final_response.text}")
        else:
            print("❌ No function calls found")
            print(f"🔧 Direct response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")

if __name__ == "__main__":
    test_function_calling() 