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
        flow.fetch_token(code=code)
        
        # Extract token information
        credentials = flow.credentials
        
        # Create OAuth token value object
        return OAuthToken.create(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expires_in=3600,  # Default to 1 hour
            scope=" ".join(self.scopes)
        )
    
    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from Google using access token"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Get user info from Google
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        user_data = response.json()
        
        # Create OAuth user info value object
        return OAuthUserInfo.create_from_google(user_data)
    
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