"""
Category Data Transfer Objects

DTOs for transferring category data between layers.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class CategoryDTO:
    """Category data transfer object"""
    
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateCategoryDTO:
    """Create category data transfer object"""
    
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


@dataclass
class UpdateCategoryDTO:
    """Update category data transfer object"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class CategoryListDTO:
    """Category list data transfer object"""
    
    categories: List[CategoryDTO]
    total_count: int 