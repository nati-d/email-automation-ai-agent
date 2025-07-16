"""
Category Repository Interface

Abstract definition for category data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.category import Category


class CategoryRepository(ABC):
    """Abstract category repository interface"""
    
    @abstractmethod
    async def save(self, category: Category) -> Category:
        """Save a category"""
        pass
    
    @abstractmethod
    async def find_by_id(self, category_id: str) -> Optional[Category]:
        """Find category by ID"""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[Category]:
        """Find categories by user ID"""
        pass
    
    @abstractmethod
    async def find_active_by_user_id(self, user_id: str) -> List[Category]:
        """Find active categories by user ID"""
        pass
    
    @abstractmethod
    async def find_by_name_and_user(self, name: str, user_id: str) -> Optional[Category]:
        """Find category by name and user ID"""
        pass
    
    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Update a category"""
        pass
    
    @abstractmethod
    async def delete(self, category_id: str) -> bool:
        """Delete a category"""
        pass
    
    @abstractmethod
    async def exists_by_name_and_user(self, name: str, user_id: str) -> bool:
        """Check if category exists by name and user ID"""
        pass
    
    @abstractmethod
    async def count_by_user_id(self, user_id: str) -> int:
        """Count categories by user ID"""
        pass 