"""
OAuth Repository Interface

Abstract definition for OAuth session data access.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.oauth_session import OAuthSession


class OAuthRepository(ABC):
    """Abstract OAuth repository interface"""
    
    @abstractmethod
    async def save_session(self, session: OAuthSession) -> OAuthSession:
        """Save an OAuth session"""
        pass
    
    @abstractmethod
    async def find_session_by_id(self, session_id: str) -> Optional[OAuthSession]:
        """Find OAuth session by ID"""
        pass
    
    @abstractmethod
    async def find_session_by_state(self, state: str) -> Optional[OAuthSession]:
        """Find OAuth session by state parameter"""
        pass
    
    @abstractmethod
    async def find_active_session_by_user_id(self, user_id: str) -> Optional[OAuthSession]:
        """Find active OAuth session for a user"""
        pass
    
    @abstractmethod
    async def update_session(self, session: OAuthSession) -> OAuthSession:
        """Update an OAuth session"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete an OAuth session"""
        pass
    
    @abstractmethod
    async def deactivate_user_sessions(self, user_id: str) -> bool:
        """Deactivate all sessions for a user"""
        pass 