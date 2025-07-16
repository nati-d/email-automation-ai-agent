#!/usr/bin/env python3
"""
Send Email Example

This script demonstrates how to send emails using the Email Agent API.
"""

import requests
import json
from typing import Optional


class SendEmailExample:
    """Example class demonstrating email sending functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def send_email(self, session_id: str, recipients: list, subject: str, body: str, html_body: Optional[str] = None):
        """Send an email using the API"""
        
        # Prepare the request data
        email_data = {
            "recipients": recipients,
            "subject": subject,
            "body": body
        }
        
        if html_body:
            email_data["html_body"] = html_body
        
        # Send the request
        headers = {
            "Authorization": f"Bearer {session_id}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/emails/send",
                headers=headers,
                json=email_data
            )
            
            print(f"📧 Send Email Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Email sent successfully!")
                print(f"   📤 Sender: {result.get('sender')}")
                print(f"   📥 Recipients: {result.get('recipients')}")
                print(f"   📧 Subject: {result.get('email', {}).get('subject')}")
                print(f"   🆔 Email ID: {result.get('email', {}).get('id')}")
                return result
            else:
                print(f"❌ Failed to send email: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return None
    
    def test_send_email(self, session_id: str):
        """Test sending an email"""
        print("📧 Testing Email Sending Functionality")
        print("=" * 50)
        
        # Test data
        recipients = ["test@example.com"]
        subject = "Test Email from Email Agent API"
        body = """
Hello!

This is a test email sent from the Email Agent API.

Features:
- Clean Architecture implementation
- OAuth authentication
- Bearer token security
- Automatic sender detection

Best regards,
Email Agent Team
        """.strip()
        
        html_body = """
<h1>Test Email from Email Agent API</h1>

<p>Hello!</p>

<p>This is a test email sent from the Email Agent API.</p>

<h2>Features:</h2>
<ul>
    <li>Clean Architecture implementation</li>
    <li>OAuth authentication</li>
    <li>Bearer token security</li>
    <li>Automatic sender detection</li>
</ul>

<p>Best regards,<br>
Email Agent Team</p>
        """.strip()
        
        # Send email
        result = self.send_email(
            session_id=session_id,
            recipients=recipients,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        if result:
            print("\n✅ Email sending test completed successfully!")
        else:
            print("\n❌ Email sending test failed!")
        
        print("=" * 50)
        return result


def main():
    """Main function to run the example"""
    import sys
    
    # Get session ID from command line argument
    if len(sys.argv) < 2:
        print("Usage: python examples/send_email_example.py <session_id>")
        print("Example: python examples/send_email_example.py edd2ebbf-414f-4f22-add4-d0c853191f42")
        sys.exit(1)
    
    session_id = sys.argv[1]
    
    # Create example instance
    example = SendEmailExample()
    
    # Test email sending
    example.test_send_email(session_id)


if __name__ == "__main__":
    main() 