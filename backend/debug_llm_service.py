#!/usr/bin/env python3
"""
Debug LLM Service

This script tests the LLM service directly to identify issues.
"""

import os
import sys
import asyncio

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_llm_service_directly():
    """Test LLM service without any dependencies"""
    print("🧪 Testing LLM Service Directly")
    print("=" * 50)
    
    # Check environment
    print(f"🔧 Environment check:")
    print(f"   GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
    print(f"   GEMINI_API_KEY length: {len(os.getenv('GEMINI_API_KEY', ''))}")
    print(f"   GEMINI_API_KEY preview: {os.getenv('GEMINI_API_KEY', '')[:20]}...")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found!")
        return False
    
    try:
        # Import and test settings
        print(f"\n🔧 Testing Settings...")
        from infrastructure.config.settings import Settings
        settings = Settings()
        print(f"   Settings loaded successfully")
        print(f"   LLM model name: {getattr(settings, 'llm_model_name', 'NOT_FOUND')}")
        print(f"   Gemini API key present: {bool(getattr(settings, 'gemini_api_key', None))}")
        
        # Test LLM service creation
        print(f"\n🔧 Testing LLM Service Creation...")
        from infrastructure.external_services.llm_service import LLMService
        llm_service = LLMService(settings)
        print(f"   LLM Service created successfully")
        
        # Test health check
        print(f"\n🔧 Testing Health Check...")
        health_result = llm_service.health_check()
        print(f"   Health result: {health_result}")
        
        # Test basic content generation
        print(f"\n🔧 Testing Basic Content Generation...")
        test_response = llm_service.generate_content(
            system_instruction="You are a helpful assistant.",
            query="Say 'Hello World'",
            response_type="text/plain"
        )
        print(f"   Test response: {test_response}")
        
        # Test email summarization
        print(f"\n🔧 Testing Email Summarization...")
        test_email = """
        Hi there,
        
        I wanted to follow up on our meeting from yesterday. The project is going well
        and we're on track to meet our deadline. Please let me know if you have any
        questions or concerns.
        
        Best regards,
        John
        """
        
        summary_result = llm_service.summarize_email(
            email_content=test_email,
            email_subject="Project Update",
            sender="john@example.com",
            recipient="manager@example.com"
        )
        print(f"   Summary result: {summary_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Full traceback: {traceback.format_exc()}")
        return False


def test_google_generativeai_import():
    """Test if google.generativeai can be imported"""
    print(f"\n🔧 Testing google.generativeai import...")
    try:
        import google.generativeai as genai
        print(f"   ✅ google.generativeai imported successfully")
        
        # Test basic functionality
        print(f"   🔧 Testing genai.configure...")
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        print(f"   ✅ genai.configure successful")
        
        # Test model creation
        print(f"   🔧 Testing GenerativeModel creation...")
        model = genai.GenerativeModel(model_name='gemini-2.5-flash')
        print(f"   ✅ GenerativeModel created successfully")
        
        # Test content generation
        print(f"   🔧 Testing content generation...")
        response = model.generate_content("Say 'Hello'")
        print(f"   ✅ Content generation successful: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ google.generativeai test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Full traceback: {traceback.format_exc()}")
        return False


def main():
    """Main debug function"""
    print("🚀 LLM Service Debug")
    print("=" * 50)
    
    # Test 1: Google GenerativeAI import
    import_ok = test_google_generativeai_import()
    
    # Test 2: LLM Service
    service_ok = test_llm_service_directly()
    
    # Summary
    print("\n" + "=" * 50)
    print("DEBUG SUMMARY")
    print("=" * 50)
    print(f"Google GenerativeAI Import: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"LLM Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    
    if import_ok and service_ok:
        print("\n🎉 All tests passed! LLM service should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        if not import_ok:
            print("   - Check google-generativeai package installation")
            print("   - Verify API key is correct")
        if not service_ok:
            print("   - Check LLM service implementation")
            print("   - Verify settings configuration")


if __name__ == "__main__":
    main() 