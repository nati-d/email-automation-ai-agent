"""
Waitlist Repository Interface

Abstract repository for waitlist operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.waitlist import WaitlistEntry


class WaitlistRepository(ABC):
    """Abstract repository for waitlist operations"""
    
    @abstractmethod
    async def save(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        """Save a waitlist entry"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[WaitlistEntry]:
        """Find waitlist entry by email"""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[WaitlistEntry]:
        """Find all waitlist entries with pagination"""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Count total waitlist entries"""
        pass
    
    @abstractmethod
    async def update(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        """Update a waitlist entry"""
        pass
    
    @abstractmethod
    async def delete_by_email(self, email: str) -> bool:
        """Delete waitlist entry by email"""
        pass