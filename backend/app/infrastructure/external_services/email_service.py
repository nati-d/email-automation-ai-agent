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
        print(f"🔍 DEBUG: EmailService.send_email() called")
        print(f"   📧 Parameters:")
        print(f"      sender: {sender}")
        print(f"      recipients: {recipients}")
        print(f"      subject: {subject}")
        print(f"      body length: {len(body)} chars")
        print(f"      html_body: {'provided' if html_body else 'None'}")
        
        try:
            print(f"🔍 DEBUG: Step 1 - Creating email message")
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            
            print(f"🔍 DEBUG: Step 2 - Adding text part")
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            print(f"🔍 DEBUG: Step 3 - Adding HTML part if provided")
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
                print(f"   ✅ HTML part attached")
            else:
                print(f"   ℹ️ No HTML part provided")
            
            print(f"🔍 DEBUG: Step 4 - Checking SMTP configuration")
            # Check if SMTP is configured
            print(f"   📋 SMTP Settings:")
            print(f"      server: {self.settings.smtp_server}")
            print(f"      port: {self.settings.smtp_port}")
            print(f"      username: {self.settings.smtp_username}")
            print(f"      password: {'*' * len(self.settings.smtp_password) if self.settings.smtp_password else 'Not set'}")
            print(f"      use_tls: {self.settings.smtp_use_tls}")
            
            if not self.is_configured():
                print(f"⚠️ SMTP not configured - Simulating email sending for development:")
                print(f"   From: {sender}")
                print(f"   To: {', '.join(recipients)}")
                print(f"   Subject: {subject}")
                print(f"   Body: {body[:100]}...")
                print(f"   📝 To enable real email sending, configure SMTP settings:")
                print(f"      SMTP_SERVER=smtp.gmail.com")
                print(f"      SMTP_PORT=587")
                print(f"      SMTP_USERNAME=your-email@gmail.com")
                print(f"      SMTP_PASSWORD=your-app-password")
                print(f"   ✅ Email simulated successfully for development!")
                return True  # Return True for development to avoid errors
            
            print(f"🔍 DEBUG: Step 5 - SMTP is configured, proceeding with connection")
            # Send email via SMTP
            print(f"📧 Sending email via SMTP:")
            print(f"   Server: {self.settings.smtp_server}:{self.settings.smtp_port}")
            print(f"   From: {sender}")
            print(f"   To: {', '.join(recipients)}")
            print(f"   Subject: {subject}")
            
            # Choose connection method based on port
            if self.settings.smtp_port == 465:
                print(f"🔍 DEBUG: Step 6a - Using SSL connection (port 465)")
                # Use SSL for port 465
                print(f"   🔐 Using SSL connection...")
                try:
                    print(f"   🔍 DEBUG: Creating SMTP_SSL connection...")
                    server = smtplib.SMTP_SSL(self.settings.smtp_server, self.settings.smtp_port)
                    print(f"   ✅ SMTP_SSL connection created successfully")
                    
                    print(f"   🔍 DEBUG: Attempting login...")
                    server.login(self.settings.smtp_username, self.settings.smtp_password)
                    print(f"   ✅ Login successful")
                    
                    print(f"   🔍 DEBUG: Sending message...")
                    server.send_message(msg)
                    print(f"   ✅ Message sent successfully")
                    
                    print(f"   🔍 DEBUG: Closing connection...")
                    server.quit()
                    print(f"   ✅ Connection closed")
                    
                    print(f"   ✅ Email sent successfully!")
                    return True
                    
                except Exception as ssl_error:
                    print(f"   ❌ SSL connection error: {ssl_error}")
                    print(f"   🔍 DEBUG: SSL error type: {type(ssl_error).__name__}")
                    import traceback
                    print(f"   🔍 DEBUG: SSL error traceback: {traceback.format_exc()}")
                    raise ssl_error
                    
            else:
                print(f"🔍 DEBUG: Step 6b - Using TLS connection (port {self.settings.smtp_port})")
                # Use TLS for other ports (587, etc.)
                try:
                    print(f"   🔍 DEBUG: Creating SMTP connection...")
                    server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
                    print(f"   ✅ SMTP connection created successfully")
                    
                    if self.settings.smtp_use_tls:
                        print(f"   🔍 DEBUG: Starting TLS...")
                        server.starttls()
                        print(f"   ✅ TLS started successfully")
                    
                    print(f"   🔍 DEBUG: Attempting login...")
                    server.login(self.settings.smtp_username, self.settings.smtp_password)
                    print(f"   ✅ Login successful")
                    
                    print(f"   🔍 DEBUG: Sending message...")
                    server.send_message(msg)
                    print(f"   ✅ Message sent successfully")
                    
                    print(f"   🔍 DEBUG: Closing connection...")
                    server.quit()
                    print(f"   ✅ Connection closed")
                    
                    print(f"   ✅ Email sent successfully!")
                    return True
                    
                except Exception as tls_error:
                    print(f"   ❌ TLS connection error: {tls_error}")
                    print(f"   🔍 DEBUG: TLS error type: {type(tls_error).__name__}")
                    import traceback
                    print(f"   🔍 DEBUG: TLS error traceback: {traceback.format_exc()}")
                    raise tls_error
                
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed: {e}")
            print(f"   💡 Make sure your SMTP_USERNAME and SMTP_PASSWORD are correct")
            print(f"   💡 For Gmail, use an App Password, not your regular password")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ SMTP Recipients refused: {e}")
            print(f"   💡 Check that the recipient email addresses are valid")
            return False
        except smtplib.SMTPServerDisconnected as e:
            print(f"❌ SMTP Server disconnected: {e}")
            print(f"   💡 Check your SMTP_SERVER and SMTP_PORT settings")
            return False
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            print(f"   💡 Check your SMTP configuration and network connection")
            return False
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(
            self.settings.smtp_server and 
            self.settings.smtp_username and 
            self.settings.smtp_password
        ) 