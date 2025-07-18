"""
User Account Repository Interface

Abstract interface for user account data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.user_account import UserAccount
from ..value_objects.email_address import EmailAddress


class UserAccountRepository(ABC):
    """Abstract interface for user account repository"""
    
    @abstractmethod
    async def save(self, user_account: UserAccount) -> UserAccount:
        """Save a user account"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_account_id: str) -> Optional[UserAccount]:
        """Find user account by ID"""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[UserAccount]:
        """Find all accounts for a user"""
        pass
    
    @abstractmethod
    async def find_by_user_and_email(self, user_id: str, email: EmailAddress) -> Optional[UserAccount]:
        """Find a specific account for a user by email"""
        pass
    
    @abstractmethod
    async def find_primary_account(self, user_id: str) -> Optional[UserAccount]:
        """Find the primary account for a user"""
        pass
    
    @abstractmethod
    async def find_active_accounts(self, user_id: str) -> List[UserAccount]:
        """Find all active accounts for a user"""
        pass
    
    @abstractmethod
    async def update(self, user_account: UserAccount) -> UserAccount:
        """Update a user account"""
        pass
    
    @abstractmethod
    async def delete(self, user_account_id: str) -> bool:
        """Delete a user account"""
        pass
    
    @abstractmethod
    async def deactivate_account(self, user_id: str, email: EmailAddress) -> bool:
        """Deactivate a specific account for a user"""
        pass
    
    @abstractmethod
    async def activate_account(self, user_id: str, email: EmailAddress) -> bool:
        """Activate a specific account for a user"""
        pass 