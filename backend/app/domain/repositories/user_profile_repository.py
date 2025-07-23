"""
UserProfile Repository Interface

Abstract definition for user profile data access.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user_profile import UserProfile

class UserProfileRepository(ABC):
    """Abstract repository for user profile persistence"""

    @abstractmethod
    async def save(self, profile: UserProfile) -> UserProfile:
        pass

    @abstractmethod
    async def update(self, profile: UserProfile) -> UserProfile:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        pass 