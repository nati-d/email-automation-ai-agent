"""
OAuth Token Value Object

Represents OAuth access and refresh tokens with validation.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

from ..exceptions.domain_exceptions import DomainValidationError


@dataclass(frozen=True)
class OAuthToken:
    """OAuth token value object"""
    
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    scope: str
    token_type: str = "Bearer"
    
    def __post_init__(self):
        """Validate OAuth token"""
        if not self.access_token.strip():
            raise DomainValidationError("Access token cannot be empty")
        
        if len(self.access_token) < 10:
            raise DomainValidationError("Access token appears to be invalid")
        
        if self.expires_at <= datetime.utcnow():
            raise DomainValidationError("Token is already expired")
        
        if not self.scope.strip():
            raise DomainValidationError("Token scope cannot be empty")
    
    @classmethod
    def create(
        cls,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
        scope: str = "",
        token_type: str = "Bearer"
    ) -> "OAuthToken":
        """Create OAuth token with expiration time calculated from expires_in seconds"""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=scope,
            token_type=token_type
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() >= self.expires_at
    
    def expires_in_seconds(self) -> int:
        """Get remaining seconds until expiration"""
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat(),
            "expires_in": self.expires_in_seconds(),
            "scope": self.scope,
            "token_type": self.token_type
        } 