"""
Email Repository Interface

Abstract definition for email data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.email import Email, EmailStatus
from ..value_objects.email_address import EmailAddress


class EmailRepository(ABC):
    """Abstract email repository interface"""
    
    @abstractmethod
    async def save(self, email: Email) -> Email:
        """Save an email"""
        pass
    
    @abstractmethod
    async def find_by_id(self, email_id: str) -> Optional[Email]:
        """Find email by ID"""
        pass
    
    @abstractmethod
    async def find_by_sender(self, sender: EmailAddress, limit: int = 50) -> List[Email]:
        """Find emails by sender"""
        pass
    
    @abstractmethod
    async def find_by_recipient(self, recipient: EmailAddress, limit: int = 50) -> List[Email]:
        """Find emails by recipient"""
        pass
    
    @abstractmethod
    async def find_by_account_owner(self, account_owner: str, limit: int = 50) -> List[Email]:
        """Find emails by account owner (logged-in user)"""
        pass
    

    async def find_by_status(self, status: EmailStatus, limit: int = 50) -> List[Email]:
        """Find emails by status"""
        pass
    
    @abstractmethod
    async def find_scheduled_emails(self, before: datetime = None) -> List[Email]:
        """Find scheduled emails to be sent"""
        pass
    
    @abstractmethod
    async def update(self, email: Email) -> Email:
        """Update an email"""
        pass
    
    @abstractmethod
    async def delete(self, email_id: str) -> bool:
        """Delete an email"""
        pass
    
    @abstractmethod
    async def count_by_sender(self, sender: EmailAddress) -> int:
        """Count emails by sender"""
        pass
    
    @abstractmethod
    async def find_recent_emails(self, limit: int = 10) -> List[Email]:
        """Find recent emails"""
        pass
    
    @abstractmethod
    async def find_sent_emails(self, account_owner: str, limit: int = 50) -> List[Email]:
        """Find sent emails from the 'sent_email' collection"""
        pass
    
    @abstractmethod
    async def find_draft_emails(self, account_owner: str, limit: int = 50) -> List[Email]:
        """Find draft emails for the user"""
        pass
    
    @abstractmethod
    async def save_draft(self, email: Email) -> Email:
        """Save an email draft"""
        pass
    
    @abstractmethod
    async def update_draft(self, email: Email) -> Email:
        """Update an existing draft"""
        pass
    
    @abstractmethod
    async def delete_draft(self, email_id: str, account_owner: str) -> bool:
        """Delete a draft email"""
        pass 