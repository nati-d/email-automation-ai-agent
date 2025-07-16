"""
User Data Transfer Objects

DTOs for transferring user data between layers.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ...domain.entities.user import UserRole


@dataclass
class UserDTO:
    """User data transfer object"""
    
    id: str
    email: str
    name: str
    role: str = UserRole.USER.value
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # OAuth-related fields
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None
    oauth_provider: Optional[str] = None


@dataclass
class CreateUserDTO:
    """Create user data transfer object"""
    
    email: str
    name: str
    role: str = UserRole.USER.value


@dataclass
class UpdateUserDTO:
    """Update user data transfer object"""
    
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None 