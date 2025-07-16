"""
Email Data Transfer Objects

DTOs for transferring email data between layers.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.entities.email import EmailStatus


@dataclass
class EmailDTO:
    """Email data transfer object"""
    
    id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    status: str = EmailStatus.DRAFT.value
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CreateEmailDTO:
    """Create email data transfer object"""
    
    sender: str
    recipients: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UpdateEmailDTO:
    """Update email data transfer object"""
    
    subject: Optional[str] = None
    body: Optional[str] = None
    html_body: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EmailListDTO:
    """Email list data transfer object"""
    
    emails: List[EmailDTO]
    total_count: int
    page: int = 1
    page_size: int = 50
    
    @property
    def has_next(self) -> bool:
        """Check if there are more pages"""
        return (self.page * self.page_size) < self.total_count
    
    @property
    def has_previous(self) -> bool:
        """Check if there are previous pages"""
        return self.page > 1


@dataclass
class SendEmailDTO:
    """Send email data transfer object"""
    
    recipients: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {} 