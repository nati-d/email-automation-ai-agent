#!/usr/bin/env python3
"""
Test SMTP Configuration

This script tests your SMTP configuration to ensure emails can be sent.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_config():
    """Test SMTP configuration"""
    
    # Get SMTP settings from environment
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    print("🧪 SMTP Configuration Test")
    print("=" * 50)
    print(f"🔧 Configuration:")
    print(f"   Server: {smtp_server}:{smtp_port}")
    print(f"   Username: {smtp_username}")
    print(f"   TLS: {smtp_use_tls}")
    print(f"   Password: {'*' * len(smtp_password) if smtp_password else 'Not set'}")
    print()
    
    # Check if credentials are set
    if not smtp_username or not smtp_password:
        print("❌ SMTP_USERNAME or SMTP_PASSWORD not set")
        print("💡 Add these to your .env file:")
        print("   SMTP_USERNAME=your-email@gmail.com")
        print("   SMTP_PASSWORD=your-app-password")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "SMTP Test Email - Email Agent API"
        msg['From'] = smtp_username
        msg['To'] = smtp_username  # Send to yourself for testing
        
        text_content = """
This is a test email to verify your SMTP configuration is working correctly.

If you received this email, your SMTP settings are properly configured and the Email Agent API can send emails successfully.

Test Details:
- Server: {server}:{port}
- Username: {username}
- TLS: {tls}

Best regards,
Email Agent API Test Script
        """.format(server=smtp_server, port=smtp_port, username=smtp_username, tls=smtp_use_tls)
        
        html_content = f"""
<html>
<head>
    <title>SMTP Test Email</title>
</head>
<body>
    <h2>✅ SMTP Configuration Test Successful!</h2>
    <p>This is a test email to verify your SMTP configuration is working correctly.</p>
    
    <p>If you received this email, your SMTP settings are properly configured and the Email Agent API can send emails successfully.</p>
    
    <h3>Test Details:</h3>
    <ul>
        <li><strong>Server:</strong> {smtp_server}:{smtp_port}</li>
        <li><strong>Username:</strong> {smtp_username}</li>
        <li><strong>TLS:</strong> {smtp_use_tls}</li>
    </ul>
    
    <p><em>Best regards,<br>Email Agent API Test Script</em></p>
</body>
</html>
        """
        
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        msg.attach(text_part)
        msg.attach(html_part)
        
        print("📧 Attempting to send test email...")
        
        # Connect and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_use_tls:
                print("   🔐 Starting TLS...")
                server.starttls()
            
            print("   🔑 Logging in...")
            server.login(smtp_username, smtp_password)
            
            print("   📤 Sending test email...")
            server.send_message(msg)
            
            print("   ✅ SMTP configuration is working!")
            print("   📬 Check your inbox for the test email")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ SMTP Authentication failed: {e}")
        print("   💡 Common solutions:")
        print("      - Use an App Password instead of your regular password")
        print("      - Enable 2-Factor Authentication on your Gmail account")
        print("      - Double-check your username and password")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"   ❌ SMTP Recipients refused: {e}")
        print("   💡 Check that the recipient email address is valid")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"   ❌ SMTP Server disconnected: {e}")
        print("   💡 Check your SMTP_SERVER and SMTP_PORT settings")
        return False
        
    except Exception as e:
        print(f"   ❌ SMTP test failed: {e}")
        print("   💡 Check your SMTP configuration and network connection")
        return False

def check_env_file():
    """Check if .env file exists and has SMTP settings"""
    print("📁 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("   💡 Create a .env file with your SMTP settings")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        
    smtp_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']
    missing_vars = []
    
    for var in smtp_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ⚠️ Missing SMTP variables: {', '.join(missing_vars)}")
        print("   💡 Add these to your .env file")
        return False
    else:
        print("   ✅ .env file contains SMTP variables")
        return True

def main():
    """Main function"""
    print("🚀 Email Agent API - SMTP Configuration Test")
    print("=" * 60)
    
    # Check .env file
    env_ok = check_env_file()
    print()
    
    if not env_ok:
        print("📝 Example .env configuration:")
        print("""
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_USE_TLS=true
        """)
        print("💡 For Gmail, you need to:")
        print("   1. Enable 2-Factor Authentication")
        print("   2. Generate an App Password")
        print("   3. Use the App Password in SMTP_PASSWORD")
        return
    
    # Test SMTP configuration
    success = test_smtp_config()
    
    print()
    if success:
        print("🎉 SMTP configuration is working correctly!")
        print("   You can now send emails through the Email Agent API")
    else:
        print("❌ SMTP configuration needs to be fixed")
        print("   Check the error messages above for guidance")

if __name__ == "__main__":
    main() 