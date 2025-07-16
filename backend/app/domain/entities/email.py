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


class EmailType(Enum):
    """Email type enumeration"""
    INBOX = "inbox"
    TASKS = "tasks"


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
    # AI Summarization fields
    summary: Optional[str] = None
    main_concept: Optional[str] = None
    sentiment: Optional[str] = None
    key_topics: List[str] = field(default_factory=list)
    summarized_at: Optional[datetime] = None
    # Email categorization
    email_type: EmailType = EmailType.INBOX
    category: Optional[str] = None  # User-defined category for inbox emails
    categorized_at: Optional[datetime] = None
    
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
    
    def update_content(self, subject: Optional[str] = None, body: Optional[str] = None, html_body: Optional[str] = None) -> None:
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
    
    def set_summarization(
        self,
        summary: str,
        main_concept: str,
        sentiment: str,
        key_topics: List[str]
    ) -> None:
        """Set AI-generated summarization data"""
        print(f"🔧 DEBUG: [Email] set_summarization called")
        print(f"🔧 DEBUG: [Email] summary: {summary[:100]}...")
        print(f"🔧 DEBUG: [Email] main_concept: {main_concept}")
        print(f"🔧 DEBUG: [Email] sentiment: {sentiment}")
        print(f"🔧 DEBUG: [Email] key_topics: {key_topics}")
        
        if not summary.strip():
            print(f"🔧 DEBUG: [Email] Summary is empty, raising error")
            raise DomainValidationError("Summary cannot be empty")
        
        if not main_concept.strip():
            print(f"🔧 DEBUG: [Email] Main concept is empty, raising error")
            raise DomainValidationError("Main concept cannot be empty")
        
        if not sentiment.strip():
            print(f"🔧 DEBUG: [Email] Sentiment is empty, raising error")
            raise DomainValidationError("Sentiment cannot be empty")
        
        self.summary = summary.strip()
        self.main_concept = main_concept.strip()
        self.sentiment = sentiment.strip()
        self.key_topics = [topic.strip() for topic in key_topics if topic.strip()]
        self.summarized_at = datetime.utcnow()
        self.mark_updated()
        
        print(f"🔧 DEBUG: [Email] Summarization set successfully")
        print(f"🔧 DEBUG: [Email] Final summary: {self.summary[:100]}...")
        print(f"🔧 DEBUG: [Email] Final main_concept: {self.main_concept}")
        print(f"🔧 DEBUG: [Email] Final sentiment: {self.sentiment}")
        print(f"🔧 DEBUG: [Email] Final key_topics: {self.key_topics}")
        print(f"🔧 DEBUG: [Email] Final summarized_at: {self.summarized_at}")
    
    def has_summarization(self) -> bool:
        """Check if email has been summarized"""
        return (
            self.summary is not None and
            self.main_concept is not None and
            self.sentiment is not None and
            self.summarized_at is not None
        )
    
    def get_summarization_data(self) -> Dict[str, Any]:
        """Get summarization data as dictionary"""
        if not self.has_summarization():
            return {}
        
        return {
            "summary": self.summary,
            "main_concept": self.main_concept,
            "sentiment": self.sentiment,
            "key_topics": self.key_topics,
            "summarized_at": self.summarized_at.isoformat() if self.summarized_at else None
        }
    
    def set_email_type(self, email_type: EmailType) -> None:
        """Set email type (Inbox or Tasks)"""
        if not isinstance(email_type, EmailType):
            raise DomainValidationError(f"Invalid email type: {email_type}")
        
        self.email_type = email_type
        self.categorized_at = datetime.utcnow()
        self.mark_updated()
    
    def is_task_email(self) -> bool:
        """Check if email is categorized as a task"""
        return self.email_type == EmailType.TASKS
    
    def is_inbox_email(self) -> bool:
        """Check if email is categorized as inbox"""
        return self.email_type == EmailType.INBOX
    
    def update_category(self, category: str) -> None:
        """Update the category for inbox emails"""
        if self.email_type != EmailType.INBOX:
            raise DomainValidationError("Categories can only be set for inbox emails")
        
        self.category = category
        self.categorized_at = datetime.utcnow()
        self.mark_updated()
    
    def reset_category(self) -> None:
        """Reset the category (for re-categorization)"""
        self.category = None
        self.categorized_at = None
        self.mark_updated()
    
    def get_categorization_data(self) -> Dict[str, Any]:
        """Get categorization data as dictionary"""
        return {
            "email_type": self.email_type.value,
            "category": self.category,
            "categorized_at": self.categorized_at.isoformat() if self.categorized_at else None,
            "is_task": self.is_task_email(),
            "is_inbox": self.is_inbox_email()
        } 