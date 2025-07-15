"""
Google OAuth Service

External service for handling Google OAuth authentication flow.
"""

import secrets
from typing import Dict, Any, Tuple
from urllib.parse import urlencode

from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import requests

from ..config.settings import Settings
from ...domain.value_objects.oauth_token import OAuthToken
from ...domain.value_objects.oauth_user_info import OAuthUserInfo


class GoogleOAuthService:
    """Service for Google OAuth authentication"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri
        self.scopes = settings.google_scopes
        
        # Validate OAuth configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate OAuth configuration"""
        if not self.client_id or self.client_id.strip() == "":
            raise Exception("Google Client ID is not configured. Please set GOOGLE_CLIENT_ID environment variable.")
        
        if not self.client_secret or self.client_secret.strip() == "":
            raise Exception("Google Client Secret is not configured. Please set GOOGLE_CLIENT_SECRET environment variable.")
        
        if not self.redirect_uri or self.redirect_uri.strip() == "":
            raise Exception("Google Redirect URI is not configured. Please set GOOGLE_REDIRECT_URI environment variable.")
        
        if not self.scopes or len(self.scopes) == 0:
            raise Exception("Google OAuth scopes are not configured.")
    
    def generate_state(self) -> str:
        """Generate a secure state parameter for OAuth"""
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: str) -> str:
        """Get Google OAuth authorization URL"""
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        # Generate authorization URL with state
        auth_url, _ = flow.authorization_url(
            access_type='offline',  # Enable refresh token
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent screen for refresh token
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, code: str, state: str) -> OAuthToken:
        """Exchange authorization code for access and refresh tokens"""
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            state=state
        )
        flow.redirect_uri = self.redirect_uri
        
        # Fetch token
        try:
            print(f"🔄 Fetching token with code: {code[:10]}...")
            flow.fetch_token(code=code)
            print("✅ Token fetched successfully from Google")
        except Exception as e:
            print(f"❌ Google token fetch failed: {str(e)}")
            import traceback
            print(f"❌ Token fetch traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to exchange authorization code for tokens: {str(e)}")
        
        # Extract token information
        credentials = flow.credentials
        
        if not credentials.token:
            print("❌ No access token in credentials")
            raise Exception("No access token received from Google")
        
        print(f"✅ Access token received: {credentials.token[:20]}...")
        
        # Calculate expires_in from credentials
        expires_in = 3600  # Default to 1 hour
        if credentials.expiry:
            from datetime import datetime
            expires_in = int((credentials.expiry - datetime.utcnow()).total_seconds())
            if expires_in <= 0:
                expires_in = 3600  # Fallback if already expired
        
        # Create OAuth token value object
        return OAuthToken.create(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expires_in=expires_in,
            scope=" ".join(self.scopes)
        )
    
    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from Google using access token"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Get user info from Google OpenID Connect endpoint (more reliable for 'sub' field)
        print(f"🔄 Requesting user info from Google OpenID Connect...")
        response = requests.get(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers=headers
        )
        
        print(f"🔄 Google userinfo response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Google userinfo request failed: {response.text}")
            raise Exception(f"Failed to get user info: {response.text}")
        
        user_data = response.json()
        print(f"✅ User data received from Google: {user_data}")
        
        # Validate that we got the required sub field
        if not user_data.get('sub'):
            print(f"❌ Missing 'sub' field in Google response: {user_data}")
            raise Exception("Google did not return a valid user ID (sub field missing)")
        
        print(f"✅ Valid user data with sub: {user_data.get('sub')}")
        
        # Create OAuth user info value object
        try:
            oauth_user_info = OAuthUserInfo.create_from_google(user_data)
            print(f"✅ OAuthUserInfo created successfully for: {oauth_user_info.email}")
            return oauth_user_info
        except Exception as e:
            print(f"❌ Failed to create OAuthUserInfo: {str(e)}")
            print(f"❌ User data was: {user_data}")
            raise Exception(f"Failed to create OAuth user info: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token using refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        token_data = response.json()
        
        # Create new OAuth token
        return OAuthToken.create(
            access_token=token_data['access_token'],
            refresh_token=refresh_token,  # Keep the original refresh token
            expires_in=token_data.get('expires_in', 3600),
            scope=token_data.get('scope', " ".join(self.scopes))
        )
    
    def verify_token(self, access_token: str) -> bool:
        """Verify if access token is valid"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/tokeninfo',
            headers=headers
        )
        
        return response.status_code == 200
    
    def revoke_token(self, token: str) -> bool:
        """Revoke access or refresh token"""
        response = requests.post(
            f'https://oauth2.googleapis.com/revoke?token={token}'
        )
        
        return response.status_code == 200 