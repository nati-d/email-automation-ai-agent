"""
User Repository Interface

Abstract definition for user data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.user import User, UserRole
from ..value_objects.email_address import EmailAddress


class UserRepository(ABC):
    """Abstract user repository interface"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: EmailAddress) -> Optional[User]:
        """Find user by email"""
        pass
    
    @abstractmethod
    async def find_by_role(self, role: UserRole) -> List[User]:
        """Find users by role"""
        pass
    
    @abstractmethod
    async def find_active_users(self, limit: int = 50) -> List[User]:
        """Find active users"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update a user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email"""
        pass 