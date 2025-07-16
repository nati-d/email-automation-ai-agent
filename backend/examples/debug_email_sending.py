#!/usr/bin/env python3
"""
Debug Email Sending

This script provides comprehensive debugging for email sending issues.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

async def debug_email_sending():
    """Debug email sending step by step"""
    
    print("🔍 Email Sending Debug Script")
    print("=" * 60)
    
    # Step 1: Check environment variables
    print("📋 Step 1: Checking Environment Variables")
    print("-" * 40)
    
    env_vars = {
        "SMTP_SERVER": os.getenv("SMTP_SERVER"),
        "SMTP_PORT": os.getenv("SMTP_PORT"),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
        "SMTP_USE_TLS": os.getenv("SMTP_USE_TLS"),
    }
    
    for var, value in env_vars.items():
        if var == "SMTP_PASSWORD":
            display_value = "*" * len(value) if value else "Not set"
        else:
            display_value = value if value else "Not set"
        print(f"   {var}: {display_value}")
    
    # Check if all required vars are set
    missing_vars = [var for var, value in env_vars.items() if not value]
    if missing_vars:
        print(f"   ❌ Missing variables: {', '.join(missing_vars)}")
    else:
        print("   ✅ All SMTP variables are set")
    
    print()
    
    # Step 2: Test settings loading
    print("📋 Step 2: Testing Settings Loading")
    print("-" * 40)
    
    try:
        from app.infrastructure.config.settings import get_settings
        settings = get_settings()
        print(f"   ✅ Settings loaded successfully")
        print(f"   📧 SMTP Server: {settings.smtp_server}")
        print(f"   📧 SMTP Port: {settings.smtp_port}")
        print(f"   📧 SMTP Username: {settings.smtp_username}")
        print(f"   📧 SMTP Password: {'*' * len(settings.smtp_password) if settings.smtp_password else 'Not set'}")
        print(f"   📧 SMTP Use TLS: {settings.smtp_use_tls}")
    except Exception as e:
        print(f"   ❌ Failed to load settings: {e}")
        return
    
    print()
    
    # Step 3: Test email service creation
    print("📋 Step 3: Testing Email Service Creation")
    print("-" * 40)
    
    try:
        from app.infrastructure.external_services.email_service import EmailService
        email_service = EmailService(settings)
        print(f"   ✅ Email service created successfully")
        print(f"   📧 Service type: {type(email_service).__name__}")
        print(f"   📧 Is configured: {email_service.is_configured()}")
    except Exception as e:
        print(f"   ❌ Failed to create email service: {e}")
        import traceback
        print(f"   🔍 Traceback: {traceback.format_exc()}")
        return
    
    print()
    
    # Step 4: Test container creation
    print("📋 Step 4: Testing Container Creation")
    print("-" * 40)
    
    try:
        from app.infrastructure.di.container import get_container
        container = get_container()
        print(f"   ✅ Container created successfully")
        
        # Test email service from container
        container_email_service = container.email_service()
        print(f"   📧 Container email service type: {type(container_email_service).__name__}")
        print(f"   📧 Container email service configured: {container_email_service.is_configured()}")
        
        # Test use case creation
        use_case = container.send_new_email_use_case()
        print(f"   📧 Use case type: {type(use_case).__name__}")
        print(f"   📧 Use case email service: {type(use_case.email_service).__name__ if use_case.email_service else 'None'}")
        
    except Exception as e:
        print(f"   ❌ Failed to create container: {e}")
        import traceback
        print(f"   🔍 Traceback: {traceback.format_exc()}")
        return
    
    print()
    
    # Step 5: Test basic SMTP connection
    print("📋 Step 5: Testing Basic SMTP Connection")
    print("-" * 40)
    
    try:
        import smtplib
        import socket
        
        print(f"   🔍 Testing connection to {settings.smtp_server}:{settings.smtp_port}")
        
        # Test DNS resolution
        try:
            ip = socket.gethostbyname(settings.smtp_server)
            print(f"   ✅ DNS resolution: {settings.smtp_server} -> {ip}")
        except Exception as dns_error:
            print(f"   ❌ DNS resolution failed: {dns_error}")
            return
        
        # Test port connectivity
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((settings.smtp_server, settings.smtp_port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Port {settings.smtp_port} is reachable")
            else:
                print(f"   ❌ Port {settings.smtp_port} is not reachable (error code: {result})")
                return
                
        except Exception as conn_error:
            print(f"   ❌ Connection test failed: {conn_error}")
            return
        
        # Test SMTP connection
        try:
            if settings.smtp_port == 465:
                print(f"   🔍 Testing SSL connection...")
                server = smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port)
                print(f"   ✅ SSL connection established")
            else:
                print(f"   🔍 Testing TLS connection...")
                server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
                print(f"   ✅ SMTP connection established")
                
                if settings.smtp_use_tls:
                    print(f"   🔍 Starting TLS...")
                    server.starttls()
                    print(f"   ✅ TLS started")
            
            print(f"   🔍 Testing login...")
            server.login(settings.smtp_username, settings.smtp_password)
            print(f"   ✅ Login successful")
            
            print(f"   🔍 Closing connection...")
            server.quit()
            print(f"   ✅ Connection closed successfully")
            
        except smtplib.SMTPAuthenticationError as auth_error:
            print(f"   ❌ Authentication failed: {auth_error}")
            print(f"   💡 Check your username and password")
            return
        except Exception as smtp_error:
            print(f"   ❌ SMTP error: {smtp_error}")
            print(f"   💡 Check your SMTP configuration")
            return
            
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
        import traceback
        print(f"   🔍 Traceback: {traceback.format_exc()}")
        return
    
    print()
    
    # Step 6: Test actual email sending
    print("📋 Step 6: Testing Actual Email Sending")
    print("-" * 40)
    
    try:
        test_sender = settings.smtp_username
        test_recipients = [settings.smtp_username]  # Send to yourself
        test_subject = "Debug Test Email"
        test_body = "This is a test email from the debug script."
        
        print(f"   📧 Sending test email...")
        print(f"      From: {test_sender}")
        print(f"      To: {test_recipients}")
        print(f"      Subject: {test_subject}")
        
        success = await email_service.send_email(
            sender=test_sender,
            recipients=test_recipients,
            subject=test_subject,
            body=test_body
        )
        
        if success:
            print(f"   ✅ Test email sent successfully!")
            print(f"   📬 Check your inbox for the test email")
        else:
            print(f"   ❌ Test email failed to send")
            
    except Exception as e:
        print(f"   ❌ Test email failed: {e}")
        import traceback
        print(f"   🔍 Traceback: {traceback.format_exc()}")
    
    print()
    print("🔍 Debug completed!")

def main():
    """Main function"""
    print("🚀 Email Sending Debug Script")
    print("=" * 60)
    
    # Run the async debug function
    asyncio.run(debug_email_sending())

if __name__ == "__main__":
    main() 