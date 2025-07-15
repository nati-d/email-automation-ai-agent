"""
Gmail Service

Service for fetching emails from Gmail using OAuth tokens.
"""

import base64
from typing import List, Optional, Dict, Any
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import email
from email.mime.text import MIMEText

from ...domain.entities.email import Email, EmailStatus
from ...domain.value_objects.email_address import EmailAddress
from ...domain.value_objects.oauth_token import OAuthToken


class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self):
        self.service_name = "gmail"
        self.version = "v1"
    
    def _create_credentials(self, oauth_token: OAuthToken) -> Credentials:
        """Create Google credentials from OAuth token"""
        credentials = Credentials(
            token=oauth_token.access_token,
            refresh_token=oauth_token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=oauth_token.scope.split() if oauth_token.scope else []
        )
        return credentials
    
    async def fetch_recent_emails(self, oauth_token: OAuthToken, user_email: str, limit: int = 50) -> List[Email]:
        """Fetch recent emails from user's Gmail inbox"""
        try:
            print(f"🔄 GmailService.fetch_recent_emails called:")
            print(f"   - user_email: {user_email}")
            print(f"   - limit: {limit}")
            print(f"   - oauth_token.access_token: {oauth_token.access_token[:20] if oauth_token.access_token else 'None'}...")
            print(f"   - oauth_token.scope: {oauth_token.scope}")
            
            # Create Gmail service
            print("🔄 Creating Google credentials...")
            credentials = self._create_credentials(oauth_token)
            print(f"🔧 Credentials created - token: {credentials.token[:20] if credentials.token else 'None'}...")
            
            print("🔄 Building Gmail service...")
            service = build(self.service_name, self.version, credentials=credentials)
            print("✅ Gmail service built successfully")
            
            # Get list of messages
            print("🔄 Getting message list from Gmail...")
            result = service.users().messages().list(
                userId='me',
                maxResults=limit,
                q='in:inbox'  # Only inbox messages
            ).execute()
            
            messages = result.get('messages', [])
            print(f"✅ Found {len(messages)} messages to fetch")
            
            emails = []
            user_email_address = EmailAddress.create(user_email)
            
            for i, message in enumerate(messages[:limit]):
                try:
                    print(f"🔄 Fetching message {i+1}/{len(messages)}: {message['id']}")
                    
                    # Get full message
                    msg = service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Parse email
                    email_obj = self._parse_gmail_message(msg, user_email_address)
                    if email_obj:
                        emails.append(email_obj)
                        print(f"✅ Parsed email: {email_obj.subject[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Failed to fetch message {message['id']}: {str(e)}")
                    continue
            
            print(f"✅ Successfully fetched {len(emails)} emails")
            return emails
            
        except Exception as e:
            print(f"❌ Failed to fetch emails from Gmail: {str(e)}")
            import traceback
            print(f"❌ Gmail fetch traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch emails from Gmail: {str(e)}")
    
    def _parse_gmail_message(self, gmail_msg: Dict[str, Any], user_email: EmailAddress) -> Optional[Email]:
        """Parse Gmail message into our Email entity"""
        try:
            payload = gmail_msg.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract headers
            subject = self._get_header_value(headers, 'Subject') or '(No Subject)'
            sender_str = self._get_header_value(headers, 'From') or 'unknown@example.com'
            to_str = self._get_header_value(headers, 'To') or str(user_email)
            date_str = self._get_header_value(headers, 'Date')
            
            # Parse sender
            sender = self._parse_email_address(sender_str)
            if not sender:
                return None
            
            # Parse recipients 
            recipients = self._parse_email_addresses(to_str)
            if not recipients:
                recipients = [user_email]  # Fallback to user email
            
            # Extract body
            body_text, body_html = self._extract_body(payload)
            
            # Parse date
            email_date = self._parse_date(date_str) if date_str else datetime.utcnow()
            
            # Create email entity
            email = Email(
                sender=sender,
                recipients=recipients,
                subject=subject,
                body=body_text or '(No content)',
                html_body=body_html,
                status=EmailStatus.SENT,  # Gmail emails are already sent
                sent_at=email_date,
                metadata={
                    'gmail_id': gmail_msg.get('id'),
                    'gmail_thread_id': gmail_msg.get('threadId'),
                    'imported_at': datetime.utcnow().isoformat(),
                    'import_source': 'gmail_oauth'
                }
            )
            
            # Set created_at to email date for proper sorting
            email.created_at = email_date
            
            return email
            
        except Exception as e:
            print(f"⚠️ Failed to parse Gmail message: {str(e)}")
            return None
    
    def _get_header_value(self, headers: List[Dict[str, str]], name: str) -> Optional[str]:
        """Get header value by name"""
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value')
        return None
    
    def _parse_email_address(self, email_str: str) -> Optional[EmailAddress]:
        """Parse email address from string like 'Name <email@domain.com>'"""
        try:
            # Handle different formats
            if '<' in email_str and '>' in email_str:
                # Format: "Name <email@domain.com>"
                email_part = email_str.split('<')[1].split('>')[0].strip()
            else:
                # Format: "email@domain.com"
                email_part = email_str.strip()
            
            return EmailAddress.create(email_part)
        except Exception:
            return None
    
    def _parse_email_addresses(self, email_str: str) -> List[EmailAddress]:
        """Parse multiple email addresses from string"""
        addresses = []
        
        # Split by comma and parse each
        parts = email_str.split(',')
        for part in parts:
            addr = self._parse_email_address(part.strip())
            if addr:
                addresses.append(addr)
        
        return addresses
    
    def _extract_body(self, payload: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Extract text and HTML body from Gmail payload"""
        body_text = None
        body_html = None
        
        try:
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    
                    if mime_type == 'text/plain':
                        body_text = self._decode_body_data(part.get('body', {}).get('data'))
                    elif mime_type == 'text/html':
                        body_html = self._decode_body_data(part.get('body', {}).get('data'))
                    elif mime_type.startswith('multipart/'):
                        # Nested multipart
                        nested_text, nested_html = self._extract_body(part)
                        if nested_text and not body_text:
                            body_text = nested_text
                        if nested_html and not body_html:
                            body_html = nested_html
            
            else:
                # Single part message
                mime_type = payload.get('mimeType', '')
                body_data = payload.get('body', {}).get('data')
                
                if mime_type == 'text/plain':
                    body_text = self._decode_body_data(body_data)
                elif mime_type == 'text/html':
                    body_html = self._decode_body_data(body_data)
        
        except Exception as e:
            print(f"⚠️ Failed to extract body: {str(e)}")
        
        return body_text, body_html
    
    def _decode_body_data(self, data: Optional[str]) -> Optional[str]:
        """Decode base64 body data"""
        if not data:
            return None
        
        try:
            # Gmail uses URL-safe base64 encoding
            decoded_bytes = base64.urlsafe_b64decode(data + '===')  # Add padding
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"⚠️ Failed to decode body data: {str(e)}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string"""
        try:
            # Gmail date format example: "Mon, 1 Jan 2024 12:00:00 +0000"
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.utcnow() 