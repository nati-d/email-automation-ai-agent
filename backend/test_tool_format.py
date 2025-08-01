"""
Test Tool Format

Simple test to verify the tool format works with Gemini.
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

def get_simple_tool() -> List[Dict[str, Any]]:
    """Define a simple tool for testing"""
    return [
        {
            "name": "search_emails",
            "description": "Search emails by various criteria",
            "parameters": {
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for subject or content"
                    }
                }
            }
        }
    ]

def test_tool_format():
    """Test if the tool format works"""
    print("🔧 TESTING TOOL FORMAT")
    print("=" * 50)
    
    try:
        # Create model with tools
        print("🔧 Creating model with tools...")
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=get_simple_tool()
        )
        print("✅ Model created successfully")
        
        # Start chat
        print("🔧 Starting chat...")
        chat = model.start_chat()
        print("✅ Chat started successfully")
        
        # Send message
        message = "do i have any email related to amazon"
        print(f"🔧 Sending message: {message}")
        
        response = chat.send_message(message)
        print("✅ Response received")
        print(f"🔧 Response text: {response.text}")
        
        # Check for function calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                for i, part in enumerate(candidate.content.parts):
                    if hasattr(part, 'function_call'):
                        print(f"✅ Found function call: {part.function_call.name}")
                        print(f"✅ Function args: {part.function_call.args}")
                        return True
        
        print("❌ No function call found")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_tool_format()
    if success:
        print("\n✅ Tool format test PASSED")
    else:
        print("\n❌ Tool format test FAILED") 