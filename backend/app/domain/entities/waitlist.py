"""
Waitlist Domain Entity

Represents a waitlist registration in the domain layer.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class WaitlistEntry:
    """Waitlist entry domain entity"""
    
    email: str
    name: Optional[str] = None
    use_case: Optional[str] = None
    referral_source: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[str] = None
    is_notified: bool = False
    
    @classmethod
    def create(
        cls,
        email: str,
        name: Optional[str] = None,
        use_case: Optional[str] = None,
        referral_source: Optional[str] = None
    ) -> "WaitlistEntry":
        """Create a new waitlist entry"""
        return cls(
            email=email.lower().strip(),
            name=name.strip() if name else None,
            use_case=use_case.strip() if use_case else None,
            referral_source=referral_source.strip() if referral_source else None
        )
    

    
    def update_notification_status(self, is_notified: bool = True):
        """Update notification status"""
        self.is_notified = is_notified
        self.updated_at = datetime.utcnow()