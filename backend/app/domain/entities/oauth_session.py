"""
OAuth Session Entity

Represents an OAuth authentication session with tokens and user information.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .base import BaseEntity
from ..value_objects.oauth_token import OAuthToken
from ..value_objects.oauth_user_info import OAuthUserInfo
from ..exceptions.domain_exceptions import DomainValidationError


@dataclass
class OAuthSession(BaseEntity):
    """OAuth session entity with business logic"""
    
    user_id: Optional[str]  # Reference to User entity (None for new users)
    token: OAuthToken
    user_info: OAuthUserInfo
    state: str  # OAuth state parameter for security
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize OAuth session and validate"""
        super().__init__()
        self._validate()
    
    def _validate(self) -> None:
        """Validate OAuth session business rules"""
        if not self.state.strip():
            raise DomainValidationError("OAuth state cannot be empty")
        
        if len(self.state) < 16:
            raise DomainValidationError("OAuth state must be at least 16 characters for security")
        
        if self.token.is_expired():
            raise DomainValidationError("Cannot create session with expired token")
    
    def deactivate(self) -> None:
        """Deactivate OAuth session"""
        self.is_active = False
        self.mark_updated()
    
    def refresh_token(self, new_token: OAuthToken) -> None:
        """Update session with new token"""
        if new_token.is_expired():
            raise DomainValidationError("Cannot refresh with expired token")
        
        self.token = new_token
        self.mark_updated()
    
    def associate_user(self, user_id: str) -> None:
        """Associate session with a user"""
        if not user_id.strip():
            raise DomainValidationError("User ID cannot be empty")
        
        self.user_id = user_id
        self.mark_updated()
    
    def is_valid(self) -> bool:
        """Check if session is valid and active"""
        return self.is_active and not self.token.is_expired()
    
    def get_access_token(self) -> str:
        """Get access token if session is valid"""
        if not self.is_valid():
            raise DomainValidationError("Session is not valid")
        
        return self.token.access_token 