"""
Email Service

Email sending service implementation.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from ..config.settings import Settings


class EmailService:
    """Email service for sending emails via SMTP"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def send_email(
        self,
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email if SMTP is configured
            if self.settings.smtp_username and self.settings.smtp_password:
                with smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port) as server:
                    if self.settings.smtp_use_tls:
                        server.starttls()
                    server.login(self.settings.smtp_username, self.settings.smtp_password)
                    server.send_message(msg)
                return True
            else:
                # Log email for development
                print(f"📧 Email would be sent:")
                print(f"   From: {sender}")
                print(f"   To: {', '.join(recipients)}")
                print(f"   Subject: {subject}")
                print(f"   Body: {body[:100]}...")
                return True
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(
            self.settings.smtp_server and 
            self.settings.smtp_username and 
            self.settings.smtp_password
        ) 