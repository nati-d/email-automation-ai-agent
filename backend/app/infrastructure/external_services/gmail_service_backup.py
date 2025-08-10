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
from email.mime.multipart import MIMEMultipart

from ...domain.entities.email import Email, EmailStatus
from ...domain.value_objects.email_address import EmailAddress
from ...domain.value_objects.oauth_token import OAuthToken


class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.service_name = "gmail"
        self.version = "v1"
        self.client_id = client_id
        self.client_secret = client_secret
    
    def _create_credentials_simple(self, oauth_token) -> Credentials:
        """Create Google credentials from OAuth token - SIMPLE VERSION"""
        from datetime import datetime
        
        print(f"🔍 Creating credentials for token expiring at: {oauth_token.expires_at}")
        print(f"🔍 Token expires in: {oauth_token.expires_in_seconds()} seconds")
        
        credentials = Credentials(
            token=oauth_token.access_token,
            refresh_token=oauth_token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=oauth_token.scope.split() if oauth_token.scope else [],
            expiry=oauth_token.expires_at
        )
        
        # Simple refresh logic - only refresh if expired
        if credentials.expired and credentials.refresh_token:
            try:
                print("🔄 Token is expired, refreshing...")
                from google.auth.transport.requests import Request
                credentials.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Token refresh failed: {str(e)}")
                raise Exception(f"Failed to refresh OAuth token: {str(e)}")
        elif credentials.expired and not credentials.refresh_token:
            raise Exception("Token is expired and no refresh token available")
        else:
            print("✅ Token is valid, no refresh needed")
        
        return credentials
    
    async def ensure_valid_token(self, oauth_session, oauth_repository) -> bool:
        """Ensure the OAuth token is valid and refresh if needed. Returns True if token is valid."""
        try:
            oauth_token = oauth_session.token
            expires_in_seconds = oauth_token.expires_in_seconds()
            
            # If token expires within 2 hours, refresh it proactively
            if expires_in_seconds < 7200:  # 2 hours
                print(f"🔄 Token expires in {expires_in_seconds/3600:.1f} hours, refreshing proactively...")
                
                # Refresh the token
                await self._create_and_refresh_credentials(oauth_session, oauth_repository)
                return True
            else:
                print(f"✅ Token is valid for {expires_in_seconds/3600:.1f} hours")
                return True
                
        except Exception as e:
            print(f"❌ Token validation failed: {str(e)}")
            return False
    
    def _create_credentials(self, oauth_token: OAuthToken) -> Credentials:
        """Create Google credentials from OAuth token (legacy method for backward compatibility)"""
        credentials = Credentials(
            token=oauth_token.access_token,
            refresh_token=oauth_token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
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
                    email_obj = self._parse_gmail_message(msg, user_email_address, email_type='inbox')
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

    async def fetch_starred_emails(self, oauth_token: OAuthToken, user_email: str, limit: int = 50) -> List[Email]:
        """Fetch starred emails from user's Gmail account"""
        try:
            print(f"🔄 GmailService.fetch_starred_emails called:")
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
            
            # Get list of starred messages
            print("🔄 Getting starred message list from Gmail...")
            result = service.users().messages().list(
                userId='me',
                maxResults=limit,
                q='is:starred'  # Only starred messages
            ).execute()
            
            messages = result.get('messages', [])
            print(f"✅ Found {len(messages)} starred messages to fetch")
            
            emails = []
            user_email_address = EmailAddress.create(user_email)
            
            for i, message in enumerate(messages[:limit]):
                try:
                    print(f"🔄 Fetching starred message {i+1}/{len(messages)}: {message['id']}")
                    
                    # Get full message
                    msg = service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Parse email
                    email_obj = self._parse_gmail_message(msg, user_email_address, email_type='inbox', is_starred=True)
                    if email_obj:
                        emails.append(email_obj)
                        print(f"✅ Parsed starred email: {email_obj.subject[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Failed to fetch starred message {message['id']}: {str(e)}")
                    continue
            
            print(f"✅ Successfully fetched {len(emails)} starred emails")
            return emails
            
        except Exception as e:
            print(f"❌ Failed to fetch starred emails from Gmail: {str(e)}")
            import traceback
            print(f"❌ Gmail starred fetch traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch starred emails from Gmail: {str(e)}")
    
    async def fetch_sent_emails(self, oauth_token: OAuthToken, user_email: str, limit: int = 50) -> List[Email]:
        """Fetch sent emails from user's Gmail account"""
        try:
            print(f"🔄 GmailService.fetch_sent_emails called:")
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
            
            # Get list of sent messages
            print("🔄 Getting sent message list from Gmail...")
            result = service.users().messages().list(
                userId='me',
                maxResults=limit,
                q='in:sent'  # Only sent messages
            ).execute()
            
            messages = result.get('messages', [])
            print(f"✅ Found {len(messages)} sent messages to fetch")
            
            emails = []
            user_email_address = EmailAddress.create(user_email)
            
            for i, message in enumerate(messages[:limit]):
                try:
                    print(f"🔄 Fetching sent message {i+1}/{len(messages)}: {message['id']}")
                    
                    # Get full message
                    msg = service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Parse email
                    email_obj = self._parse_gmail_message(msg, user_email_address, email_type='sent')
                    if email_obj:
                        emails.append(email_obj)
                        print(f"✅ Parsed sent email: {email_obj.subject[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Failed to fetch sent message {message['id']}: {str(e)}")
                    continue
            
            print(f"✅ Successfully fetched {len(emails)} sent emails")
            return emails
            
        except Exception as e:
            print(f"❌ Failed to fetch sent emails from Gmail: {str(e)}")
            import traceback
            print(f"❌ Gmail fetch traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch sent emails from Gmail: {str(e)}")
    
    def _parse_gmail_message(self, gmail_msg: Dict[str, Any], user_email: EmailAddress, email_type: str = 'inbox', is_starred: bool = False) -> Optional[Email]:
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
            
            # Create email entity with proper email_type and starred flag
            metadata = {
                'gmail_id': gmail_msg.get('id'),
                'gmail_thread_id': gmail_msg.get('threadId'),
                'imported_at': datetime.utcnow().isoformat(),
                'import_source': 'gmail_oauth',
                'is_starred': is_starred
            }
            
            email = Email(
                sender=sender,
                recipients=recipients,
                subject=subject,
                body=body_text or '(No content)',
                html_body=body_html,
                status=EmailStatus.SENT,  # Gmail emails are already sent
                sent_at=email_date,
                # Account ownership fields
                account_owner=str(user_email),  # The logged-in user's email
                email_holder=str(user_email),   # The email account that holds these emails
                email_type=email_type,  # Set the email type (inbox, sent, etc.)
                metadata=metadata
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
    
    async def send_email_via_gmail(
        self, 
        oauth_token: OAuthToken, 
        sender_email: str,
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> bool:
        """Send email through Gmail API on behalf of the user"""
        try:
            print(f"🔄 GmailService.send_email_via_gmail called:")
            print(f"   - sender_email: {sender_email}")
            print(f"   - recipients: {recipients}")
            print(f"   - subject: {subject}")
            print(f"   - body length: {len(body)} chars")
            print(f"   - html_body: {'provided' if html_body else 'None'}")
            print(f"   - oauth_token.access_token: {oauth_token.access_token[:20] if oauth_token.access_token else 'None'}...")
            
            # Create Gmail service with simple credentials
            print("🔄 Creating Google credentials...")
            credentials = self._create_credentials_simple(oauth_token)
            print(f"🔧 Credentials created - token: {credentials.token[:20] if credentials.token else 'None'}...")
            
            print("🔄 Building Gmail service...")
            service = build(self.service_name, self.version, credentials=credentials)
            print("✅ Gmail service built successfully")
            
            # Create email message
            print("🔄 Creating email message...")
            message = self._create_email_message(sender_email, recipients, subject, body, html_body)
            print("✅ Email message created")
            
            # Send email through Gmail API
            print("🔄 Sending email through Gmail API...")
            result = service.users().messages().send(
                userId='me',
                body={'raw': message}
            ).execute()
            
            print(f"✅ Email sent successfully through Gmail API!")
            print(f"   📧 Message ID: {result.get('id')}")
            print(f"   📧 Thread ID: {result.get('threadId')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email through Gmail API: {str(e)}")
            import traceback
            print(f"❌ Gmail send traceback: {traceback.format_exc()}")
            return False
    
    def _create_email_message(
        self, 
        sender_email: str, 
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> str:
        """Create email message in Gmail API format"""
        try:
            # Create message
            if html_body:
                # Create multipart message with both text and HTML
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = ', '.join(recipients)
                
                # Add text part
                text_part = MIMEText(body, 'plain', 'utf-8')
                msg.attach(text_part)
                
                # Add HTML part
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            else:
                # Create simple text message
                msg = MIMEText(body, 'plain', 'utf-8')
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = ', '.join(recipients)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            return raw_message
            
        except Exception as e:
            print(f"❌ Failed to create email message: {str(e)}")
            raise Exception(f"Failed to create email message: {str(e)}")
    
    async def fetch_draft_emails(self, oauth_token: OAuthToken, user_email: str, limit: int = 50) -> List[Email]:
        """Fetch draft emails from user's Gmail account"""
        try:
            print(f"🔄 GmailService.fetch_draft_emails called:")
            print(f"   - user_email: {user_email}")
            print(f"   - limit: {limit}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Get list of draft messages
            result = service.users().drafts().list(
                userId='me',
                maxResults=limit
            ).execute()
            
            drafts = result.get('drafts', [])
            print(f"✅ Found {len(drafts)} draft messages to fetch")
            
            emails = []
            user_email_address = EmailAddress.create(user_email)
            
            for i, draft in enumerate(drafts[:limit]):
                try:
                    print(f"🔄 Fetching draft {i+1}/{len(drafts)}: {draft['id']}")
                    
                    # Get full draft
                    draft_detail = service.users().drafts().get(
                        userId='me',
                        id=draft['id']
                    ).execute()
                    
                    # Parse the message part of the draft
                    message = draft_detail.get('message', {})
                    email_obj = self._parse_gmail_message(message, user_email_address, email_type='draft')
                    
                    if email_obj:
                        # Set draft-specific properties
                        email_obj.status = EmailStatus.DRAFT
                        email_obj.metadata['gmail_draft_id'] = draft['id']
                        email_obj.metadata['is_gmail_draft'] = True
                        email_obj.metadata['synced_with_gmail'] = True
                        emails.append(email_obj)
                        print(f"✅ Parsed draft: {email_obj.subject[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Failed to fetch draft {draft['id']}: {str(e)}")
                    continue
            
            print(f"✅ Successfully fetched {len(emails)} draft emails")
            return emails
            
        except Exception as e:
            print(f"❌ Failed to fetch drafts from Gmail: {str(e)}")
            raise Exception(f"Failed to fetch drafts from Gmail: {str(e)}")
    
    async def create_gmail_draft(
        self, 
        oauth_token: OAuthToken, 
        sender_email: str,
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> Optional[str]:
        """Create a draft in Gmail and return the draft ID"""
        try:
            print(f"🔄 GmailService.create_gmail_draft called:")
            print(f"   - sender_email: {sender_email}")
            print(f"   - recipients: {recipients}")
            print(f"   - subject: {subject}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Create email message
            message = self._create_email_message(sender_email, recipients, subject, body, html_body)
            
            # Create draft through Gmail API
            draft_body = {
                'message': {
                    'raw': message
                }
            }
            
            result = service.users().drafts().create(
                userId='me',
                body=draft_body
            ).execute()
            
            draft_id = result.get('id')
            print(f"✅ Gmail draft created successfully! Draft ID: {draft_id}")
            
            return draft_id
            
        except Exception as e:
            print(f"❌ Failed to create Gmail draft: {str(e)}")
            return None
    
    async def update_gmail_draft(
        self, 
        oauth_token: OAuthToken, 
        draft_id: str,
        sender_email: str,
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> bool:
        """Update an existing Gmail draft"""
        try:
            print(f"🔄 GmailService.update_gmail_draft called:")
            print(f"   - draft_id: {draft_id}")
            print(f"   - subject: {subject}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Create email message
            message = self._create_email_message(sender_email, recipients, subject, body, html_body)
            
            # Update draft through Gmail API
            draft_body = {
                'id': draft_id,
                'message': {
                    'raw': message
                }
            }
            
            result = service.users().drafts().update(
                userId='me',
                id=draft_id,
                body=draft_body
            ).execute()
            
            print(f"✅ Gmail draft updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update Gmail draft: {str(e)}")
            return False
    
    async def delete_gmail_draft(self, oauth_token: OAuthToken, draft_id: str) -> bool:
        """Delete a Gmail draft"""
        try:
            print(f"🔄 GmailService.delete_gmail_draft called:")
            print(f"   - draft_id: {draft_id}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Delete draft through Gmail API
            service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()
            
            print(f"✅ Gmail draft deleted successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete Gmail draft: {str(e)}")
            return False
    
    async def send_gmail_draft(self, oauth_token: OAuthToken, draft_id: str) -> bool:
        """Send a Gmail draft"""
        try:
            print(f"🔄 GmailService.send_gmail_draft called:")
            print(f"   - draft_id: {draft_id}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Send draft through Gmail API
            result = service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            
            print(f"✅ Gmail draft sent successfully!")
            print(f"   📧 Message ID: {result.get('id')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send Gmail draft: {str(e)}")
            return False
    

    
    async def create_gmail_draft(
        self, 
        oauth_token: OAuthToken, 
        sender_email: str,
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> Optional[str]:
        """Create a draft in Gmail and return the draft ID"""
        try:
            print(f"🔄 GmailService.create_gmail_draft called:")
            print(f"   - sender_email: {sender_email}")
            print(f"   - recipients: {recipients}")
            print(f"   - subject: {subject}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Create email message
            message = self._create_email_message(sender_email, recipients, subject, body, html_body)
            
            # Create draft through Gmail API
            draft_body = {
                'message': {
                    'raw': message
                }
            }
            
            result = service.users().drafts().create(
                userId='me',
                body=draft_body
            ).execute()
            
            draft_id = result.get('id')
            print(f"✅ Gmail draft created successfully! Draft ID: {draft_id}")
            
            return draft_id
            
        except Exception as e:
            print(f"❌ Failed to create Gmail draft: {str(e)}")
            return None
    
    async def update_gmail_draft(
        self, 
        oauth_token: OAuthToken, 
        draft_id: str,
        sender_email: str,
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> bool:
        """Update an existing Gmail draft"""
        try:
            print(f"🔄 GmailService.update_gmail_draft called:")
            print(f"   - draft_id: {draft_id}")
            print(f"   - subject: {subject}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Create email message
            message = self._create_email_message(sender_email, recipients, subject, body, html_body)
            
            # Update draft through Gmail API
            draft_body = {
                'id': draft_id,
                'message': {
                    'raw': message
                }
            }
            
            result = service.users().drafts().update(
                userId='me',
                id=draft_id,
                body=draft_body
            ).execute()
            
            print(f"✅ Gmail draft updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update Gmail draft: {str(e)}")
            return False
    
    async def delete_gmail_draft(self, oauth_token: OAuthToken, draft_id: str) -> bool:
        """Delete a Gmail draft"""
        try:
            print(f"🔄 GmailService.delete_gmail_draft called:")
            print(f"   - draft_id: {draft_id}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Delete draft through Gmail API
            service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()
            
            print(f"✅ Gmail draft deleted successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete Gmail draft: {str(e)}")
            return False
    
    async def send_gmail_draft(self, oauth_token: OAuthToken, draft_id: str) -> bool:
        """Send a Gmail draft"""
        try:
            print(f"🔄 GmailService.send_gmail_draft called:")
            print(f"   - draft_id: {draft_id}")
            
            # Create Gmail service
            credentials = self._create_credentials(oauth_token)
            service = build(self.service_name, self.version, credentials=credentials)
            
            # Send draft through Gmail API
            result = service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            
            print(f"✅ Gmail draft sent successfully!")
            print(f"   📧 Message ID: {result.get('id')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send Gmail draft: {str(e)}")
            return False 