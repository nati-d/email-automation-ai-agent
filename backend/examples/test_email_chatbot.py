"""
Test Email Chatbot

Example script to test the email chatbot functionality.
"""

import requests
import json
from typing import Dict, Any


class EmailChatbotTester:
    """Test the email chatbot endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
    
    def authenticate(self, session_id: str):
        """Set authentication token"""
        self.auth_token = session_id
        self.headers = {
            "Authorization": f"Bearer {session_id}",
            "Content-Type": "application/json"
        }
    
    def get_chatbot_info(self) -> Dict[str, Any]:
        """Get email chatbot information"""
        url = f"{self.base_url}/llm/email-chatbot/info"
        
        response = requests.get(url, headers=self.headers)
        print(f"🔧 Get Chatbot Info Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chatbot info retrieved:")
            print(f"📝 Message: {result['message']}")
            print(f"🛠️ Capabilities: {result['capabilities']}")
            return result
        else:
            print(f"❌ Failed to get chatbot info: {response.text}")
            return None
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the email chatbot"""
        url = f"{self.base_url}/llm/email-chatbot/chat"
        data = {
            "message": message
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        print(f"🔧 Send Message Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Chatbot Response:")
            print(f"   Message: {result['message']}")
            return result
        else:
            print(f"❌ Failed to send message: {response.text}")
            return None
    
    def run_demo(self):
        """Run a complete demo of the email chatbot"""
        print("🚀 EMAIL CHATBOT DEMO")
        print("=" * 50)
        
        # Get chatbot info
        print("\n1️⃣ Getting email chatbot information...")
        if not self.get_chatbot_info():
            return
        
        # Test various queries
        test_queries = [
            "Show me my recent emails",
            "What are my email statistics for this month?",
            "Find emails from work contacts",
            "Show me emails about project updates",
            "What's my recent email activity?",
            "Find emails related to budget discussions"
        ]
        
        for i, query in enumerate(test_queries, 2):
            print(f"\n{i}️⃣ Testing query: '{query}'")
            print("-" * 40)
            self.send_message(query)
            print("-" * 40)
        
        print("\n✅ Demo completed!")


def main():
    """Main function to run the demo"""
    # You'll need to replace this with a valid session ID from your OAuth login
    session_id = "your_session_id_here"
    
    if session_id == "your_session_id_here":
        print("❌ Please replace 'your_session_id_here' with a valid session ID from your OAuth login")
        print("💡 You can get a session ID by:")
        print("   1. Going through the OAuth login process")
        print("   2. Using the session_id from the auth-success redirect")
        print("   3. Or checking your browser's network tab for the session ID")
        return
    
    tester = EmailChatbotTester()
    tester.authenticate(session_id)
    tester.run_demo()


if __name__ == "__main__":
    main() 