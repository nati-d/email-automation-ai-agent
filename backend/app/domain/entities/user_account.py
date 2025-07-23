"""
User Account Entity

Represents an email account associated with a user.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .base import BaseEntity
from ..value_objects.email_address import EmailAddress


@dataclass
class UserAccount(BaseEntity):
    """User account entity for tracking associated email accounts"""
    
    user_id: str  # ID of the user who owns this account association
    email: EmailAddress  # Email address of the account
    account_name: Optional[str] = None  # Optional name for the account (e.g., "Work", "Personal")
    provider: str = "google"  # OAuth provider (google, outlook, etc.)
    is_primary: bool = False  # Whether this is the user's primary account
    is_active: bool = True  # Whether this account association is active
    last_sync: Optional[datetime] = None  # Last time emails were synced from this account
    sync_enabled: bool = True  # Whether automatic sync is enabled for this account
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize UserAccount entity and validate"""
        super().__init__()
        
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        
        if not self.email:
            raise ValueError("Email cannot be empty")
        
        if not self.provider:
            raise ValueError("Provider cannot be empty")
    
    def update_last_sync(self, sync_time: Optional[datetime] = None):
        """Update the last sync time"""
        self.last_sync = sync_time or datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def disable_sync(self):
        """Disable automatic sync for this account"""
        self.sync_enabled = False
        self.updated_at = datetime.utcnow()
    
    def enable_sync(self):
        """Enable automatic sync for this account"""
        self.sync_enabled = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate this account association"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate this account association"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def set_as_primary(self):
        """Set this account as the primary account"""
        self.is_primary = True
        self.updated_at = datetime.utcnow()
    
    def set_as_secondary(self):
        """Set this account as a secondary account"""
        self.is_primary = False
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def create_primary_account(cls, user_id: str, email: EmailAddress, provider: str = "google") -> "UserAccount":
        """Create a primary account for a user"""
        return cls(
            user_id=user_id,
            email=email,
            provider=provider,
            is_primary=True,
            account_name="Primary Account"
        )
    
    @classmethod
    def create_secondary_account(cls, user_id: str, email: EmailAddress, account_name: str, provider: str = "google") -> "UserAccount":
        """Create a secondary account for a user"""
        return cls(
            user_id=user_id,
            email=email,
            provider=provider,
            is_primary=False,
            account_name=account_name
        ) 