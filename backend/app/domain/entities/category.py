"""
Category Entity

Core business object representing a user-defined email category.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from .base import BaseEntity
from ..exceptions.domain_exceptions import DomainValidationError


@dataclass
class Category(BaseEntity):
    """Category entity with business logic"""
    
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize Category entity and validate"""
        super().__init__()
        self._validate()
    
    def _validate(self) -> None:
        """Validate category business rules"""
        if not self.user_id.strip():
            raise DomainValidationError("User ID cannot be empty")
        
        if not self.name.strip():
            raise DomainValidationError("Category name cannot be empty")
        
        if len(self.name) > 50:
            raise DomainValidationError("Category name cannot exceed 50 characters")
        
        if self.description and len(self.description) > 200:
            raise DomainValidationError("Category description cannot exceed 200 characters")
        
        if self.color and not self._is_valid_color(self.color):
            raise DomainValidationError("Invalid color format. Use hex color (e.g., #FF5733)")
    
    def _is_valid_color(self, color: str) -> bool:
        """Validate hex color format"""
        if not color.startswith('#'):
            return False
        if len(color) != 7:  # #RRGGBB
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def update_name(self, name: str) -> None:
        """Update category name"""
        if not name.strip():
            raise DomainValidationError("Category name cannot be empty")
        
        if len(name) > 50:
            raise DomainValidationError("Category name cannot exceed 50 characters")
        
        self.name = name
        self.mark_updated()
    
    def update_description(self, description: Optional[str]) -> None:
        """Update category description"""
        if description and len(description) > 200:
            raise DomainValidationError("Category description cannot exceed 200 characters")
        
        self.description = description
        self.mark_updated()
    
    def update_color(self, color: Optional[str]) -> None:
        """Update category color"""
        if color and not self._is_valid_color(color):
            raise DomainValidationError("Invalid color format. Use hex color (e.g., #FF5733)")
        
        self.color = color
        self.mark_updated()
    
    def deactivate(self) -> None:
        """Deactivate category"""
        self.is_active = False
        self.mark_updated()
    
    def activate(self) -> None:
        """Activate category"""
        self.is_active = True
        self.mark_updated()
    
    @classmethod
    def create(
        cls,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None
    ) -> "Category":
        """Create a new category"""
        return cls(
            user_id=user_id,
            name=name,
            description=description,
            color=color
        ) 