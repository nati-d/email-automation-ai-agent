"""
User Entity

Core business object representing a user.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from .base import BaseEntity
from ..value_objects.email_address import EmailAddress
from ..exceptions.domain_exceptions import DomainValidationError


class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"


@dataclass
class User(BaseEntity):
    """User entity with business logic"""
    
    email: EmailAddress
    name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    last_login: Optional[datetime] = None
    
    # OAuth-related fields
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None
    oauth_provider: Optional[str] = None
    
    def __post_init__(self):
        """Initialize User entity and validate"""
        super().__init__()
        self._validate()
    
    def _validate(self) -> None:
        """Validate user business rules"""
        if not self.name.strip():
            raise DomainValidationError("User name cannot be empty")
        
        if len(self.name) > 100:
            raise DomainValidationError("User name cannot exceed 100 characters")
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.mark_updated()
    
    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.mark_updated()
    
    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.mark_updated()
    
    def change_role(self, new_role: UserRole) -> None:
        """Change user role"""
        if new_role != self.role:
            self.role = new_role
            self.mark_updated()
    
    def update_name(self, name: str) -> None:
        """Update user name"""
        if not name.strip():
            raise DomainValidationError("User name cannot be empty")
        
        if len(name) > 100:
            raise DomainValidationError("User name cannot exceed 100 characters")
        
        self.name = name
        self.mark_updated()
    
    def set_oauth_info(self, google_id: str, profile_picture: Optional[str] = None, provider: str = "google") -> None:
        """Set OAuth information for the user"""
        if not google_id.strip():
            raise DomainValidationError("Google ID cannot be empty")
        
        self.google_id = google_id
        self.profile_picture = profile_picture
        self.oauth_provider = provider
        self.mark_updated()
    
    @classmethod
    def create_from_oauth(
        cls,
        email: EmailAddress,
        name: str,
        google_id: str,
        profile_picture: Optional[str] = None,
        role: UserRole = UserRole.USER
    ) -> "User":
        """Create a new user from OAuth information"""
        user = cls(
            email=email,
            name=name,
            role=role,
            google_id=google_id,
            profile_picture=profile_picture,
            oauth_provider="google"
        )
        return user
    
    def is_oauth_user(self) -> bool:
        """Check if user was created via OAuth"""
        return self.google_id is not None and self.oauth_provider is not None 