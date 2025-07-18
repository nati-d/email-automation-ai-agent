"""
OAuth User Info Value Object

Represents user information from OAuth provider.
"""

from dataclasses import dataclass
from typing import Optional

from ..exceptions.domain_exceptions import DomainValidationError
from .email_address import EmailAddress


@dataclass(frozen=True)
class OAuthUserInfo:
    """OAuth user information value object"""
    
    provider_id: str  # Google's 'sub' field
    email: EmailAddress
    name: str
    picture: Optional[str] = None
    locale: Optional[str] = None
    provider: str = "google"
    
    def __post_init__(self):
        """Validate OAuth user info"""
        if not self.provider_id.strip():
            raise DomainValidationError("Provider ID cannot be empty")
        
        if not self.name.strip():
            raise DomainValidationError("User name cannot be empty")
        
        if len(self.name) > 100:
            raise DomainValidationError("User name cannot exceed 100 characters")
        
        if self.provider not in ["google"]:
            raise DomainValidationError(f"Unsupported OAuth provider: {self.provider}")
        
        # Email validation is handled by EmailAddress class
    
    @classmethod
    def create_from_google(
        cls,
        google_user_data: dict
    ) -> "OAuthUserInfo":
        """Create OAuth user info from Google user data"""
        email = EmailAddress.create(google_user_data.get("email", ""))
        
        return cls(
            provider_id=google_user_data.get("sub", ""),
            email=email,
            name=google_user_data.get("name", ""),
            picture=google_user_data.get("picture"),
            locale=google_user_data.get("locale"),
            provider="google"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "provider_id": self.provider_id,
            "email": str(self.email),
            "name": self.name,
            "picture": self.picture,
            "locale": self.locale,
            "provider": self.provider
        } 