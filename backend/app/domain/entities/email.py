"""
Email Entity

Core business object representing an email message.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .base import BaseEntity
from ..value_objects.email_address import EmailAddress
from ..exceptions.domain_exceptions import DomainValidationError


class EmailStatus(Enum):
    """Email status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Email(BaseEntity):
    """Email entity with business logic"""
    
    sender: EmailAddress
    recipients: List[EmailAddress]
    subject: str
    body: str
    html_body: Optional[str] = None
    status: EmailStatus = EmailStatus.DRAFT
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize Email entity and validate"""
        super().__init__()
        self._validate()
    
    def _validate(self) -> None:
        """Validate email business rules"""
        if not self.subject.strip():
            raise DomainValidationError("Email subject cannot be empty")
        
        if not self.body.strip():
            raise DomainValidationError("Email body cannot be empty")
        
        if not self.recipients:
            raise DomainValidationError("Email must have at least one recipient")
        
        if len(self.recipients) > 100:
            raise DomainValidationError("Email cannot have more than 100 recipients")
    
    def add_recipient(self, recipient: EmailAddress) -> None:
        """Add a recipient to the email"""
        if recipient not in self.recipients:
            if len(self.recipients) >= 100:
                raise DomainValidationError("Cannot add more than 100 recipients")
            self.recipients.append(recipient)
            self.mark_updated()
    
    def remove_recipient(self, recipient: EmailAddress) -> None:
        """Remove a recipient from the email"""
        if recipient in self.recipients:
            self.recipients.remove(recipient)
            self.mark_updated()
    
    def schedule(self, scheduled_at: datetime) -> None:
        """Schedule the email for future sending"""
        if scheduled_at <= datetime.utcnow():
            raise DomainValidationError("Cannot schedule email for past time")
        
        self.scheduled_at = scheduled_at
        self.status = EmailStatus.SCHEDULED
        self.mark_updated()
    
    def mark_as_sending(self) -> None:
        """Mark email as currently being sent"""
        if self.status not in [EmailStatus.DRAFT, EmailStatus.SCHEDULED]:
            raise DomainValidationError(f"Cannot send email with status {self.status.value}")
        
        self.status = EmailStatus.SENDING
        self.mark_updated()
    
    def mark_as_sent(self) -> None:
        """Mark email as successfully sent"""
        if self.status != EmailStatus.SENDING:
            raise DomainValidationError(f"Cannot mark email as sent with status {self.status.value}")
        
        self.status = EmailStatus.SENT
        self.sent_at = datetime.utcnow()
        self.mark_updated()
    
    def mark_as_failed(self, error_message: str) -> None:
        """Mark email as failed to send"""
        if self.status != EmailStatus.SENDING:
            raise DomainValidationError(f"Cannot mark email as failed with status {self.status.value}")
        
        self.status = EmailStatus.FAILED
        self.metadata["error_message"] = error_message
        self.metadata["failed_at"] = datetime.utcnow().isoformat()
        self.mark_updated()
    
    def cancel(self) -> None:
        """Cancel a scheduled email"""
        if self.status not in [EmailStatus.DRAFT, EmailStatus.SCHEDULED]:
            raise DomainValidationError(f"Cannot cancel email with status {self.status.value}")
        
        self.status = EmailStatus.CANCELLED
        self.mark_updated()
    
    def is_editable(self) -> bool:
        """Check if email can be edited"""
        return self.status in [EmailStatus.DRAFT, EmailStatus.SCHEDULED]
    
    def update_content(self, subject: str = None, body: str = None, html_body: str = None) -> None:
        """Update email content if editable"""
        if not self.is_editable():
            raise DomainValidationError(f"Cannot edit email with status {self.status.value}")
        
        if subject is not None:
            if not subject.strip():
                raise DomainValidationError("Email subject cannot be empty")
            self.subject = subject
        
        if body is not None:
            if not body.strip():
                raise DomainValidationError("Email body cannot be empty")
            self.body = body
        
        if html_body is not None:
            self.html_body = html_body
        
        self.mark_updated() 