"""
Gemini Service Example

Example script demonstrating how to use the streamlined Gemini service.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.di.container import get_container
from app.infrastructure.config.settings import get_settings

def main():
    """Main function to demonstrate Gemini service usage"""
    
    # Load environment variables
    load_dotenv()
    
    print("🤖 Gemini Service Example")
    print("=" * 50)
    
    try:
        # Get the container and LLM service
        container = get_container()
        llm_service = container.llm_service()
        
        print("✅ Gemini Service initialized successfully")
        print(f"📝 Model: {llm_service.model_name}")
        print(f"👁️ Vision Model: {llm_service.vision_model_name}")
        print(f"🚀 Pro Model: {llm_service.pro_model_name}")
        print(f"🎯 Using Gemini 2.5 Flash - Latest and most capable model!")
        print()
        
        # Example 1: Basic content generation
        print("📝 Example 1: Basic Content Generation")
        print("-" * 30)
        response = llm_service.generate_content(
            system_instruction="You are a helpful assistant.",
            query="Explain what Gemini is in one sentence.",
            response_type="text/plain"
        )
        print(f"Response: {response}")
        print()
        
        # Example 2: Generate email content
        print("📧 Example 2: Generate Email Content")
        print("-" * 30)
        prompt = "Write a professional email to schedule a meeting with a client"
        context = "The client is a potential business partner, and we want to discuss collaboration opportunities"
        
        content = llm_service.generate_email_content(prompt, context)
        print(f"Prompt: {prompt}")
        print(f"Context: {context}")
        print(f"Generated Content:\n{content}")
        print()
        
        # Example 3: Analyze email sentiment
        print("📊 Example 3: Analyze Email Sentiment")
        print("-" * 30)
        email_content = """
        Hi John,
        
        I hope this email finds you well. I wanted to follow up on our previous discussion about the project timeline.
        I understand there have been some delays, and I want to assure you that we're working hard to get back on track.
        
        We value our partnership and are committed to delivering quality results. Please let me know if you have any concerns.
        
        Best regards,
        Sarah
        """
        
        analysis = llm_service.analyze_email_sentiment(email_content)
        print(f"Email Content:\n{email_content}")
        print(f"Sentiment Analysis:")
        print(f"  - Sentiment: {analysis.get('sentiment', 'unknown')}")
        print(f"  - Tone: {analysis.get('tone', 'unknown')}")
        print(f"  - Professionalism Score: {analysis.get('professionalism_score', 0)}/10")
        print(f"  - Suggestions: {', '.join(analysis.get('suggestions', []))}")
        print(f"  - Summary: {analysis.get('summary', 'No summary available')}")
        print()
        
        # Example 4: Suggest email subject
        print("📝 Example 4: Suggest Email Subject")
        print("-" * 30)
        email_content = """
        Hi Team,
        
        I wanted to share some exciting news about our Q4 performance. We've exceeded our targets by 15% and achieved record customer satisfaction scores.
        
        Let's celebrate this success and discuss our plans for Q1.
        
        Thanks,
        Manager
        """
        
        subject = llm_service.suggest_email_subject(email_content, "Internal team communication")
        print(f"Email Content:\n{email_content}")
        print(f"Suggested Subject: {subject}")
        print()
        
        # Example 5: Generate email response
        print("💬 Example 5: Generate Email Response")
        print("-" * 30)
        original_email = """
        Hi Sarah,
        
        Thank you for your proposal. I've reviewed it and have some questions about the timeline and budget.
        Could we schedule a call to discuss these details?
        
        Best regards,
        John
        """
        
        response = llm_service.generate_email_response(
            original_email, 
            response_type="acknowledge",
            additional_context="We want to be accommodating and professional"
        )
        print(f"Original Email:\n{original_email}")
        print(f"Generated Response:\n{response}")
        print()
        
        # Example 6: Smart email composer
        print("🎯 Example 6: Smart Email Composer")
        print("-" * 30)
        purpose = "Thank a customer for their recent purchase"
        recipient_context = "Customer bought a premium software license worth $5000"
        tone = "grateful"
        
        result = llm_service.generate_email_content(purpose, recipient_context)
        subject = llm_service.suggest_email_subject(result, recipient_context)
        
        print(f"Purpose: {purpose}")
        print(f"Recipient Context: {recipient_context}")
        print(f"Tone: {tone}")
        print(f"Generated Subject: {subject}")
        print(f"Generated Content:\n{result}")
        print()
        
        # Example 7: Chat functionality
        print("💭 Example 7: Chat Functionality")
        print("-" * 30)
        chat = llm_service.start_chat(
            system_instruction="You are a helpful email assistant.",
            session_id="test_session"
        )
        
        response1 = llm_service.send_message("Hello! Can you help me write an email?", "test_session")
        print(f"User: Hello! Can you help me write an email?")
        print(f"Assistant: {response1}")
        
        response2 = llm_service.send_message("I need to thank a client for their business", "test_session")
        print(f"User: I need to thank a client for their business")
        print(f"Assistant: {response2}")
        
        # End the chat session
        llm_service.end_chat("test_session")
        print("✅ Chat session ended")
        print()
        
        # Example 8: Health check
        print("🏥 Example 8: Health Check")
        print("-" * 30)
        health_info = llm_service.health_check()
        print(f"Status: {health_info.get('status', 'unknown')}")
        print(f"Service: {health_info.get('service', 'unknown')}")
        print(f"Model: {health_info.get('model', 'unknown')}")
        print(f"Test Response: {health_info.get('test_response', 'unknown')}")
        print(f"Available Models: {health_info.get('available_models', [])}")
        print()
        
        # Example 9: Model information
        print("ℹ️ Example 9: Model Information")
        print("-" * 30)
        model_info = llm_service.get_model_info()
        print(f"Model Name: {model_info.get('name', 'unknown')}")
        print(f"Display Name: {model_info.get('display_name', 'unknown')}")
        print(f"Description: {model_info.get('description', 'unknown')}")
        print(f"Generation Methods: {model_info.get('generation_methods', [])}")
        print()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you have set the required environment variables:")
        print("   - GEMINI_API_KEY")
        print("2. Check that the google-generativeai package is installed")
        print("3. Verify your API key is valid and has the necessary permissions")

if __name__ == "__main__":
    main() 