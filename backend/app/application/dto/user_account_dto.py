"""
User Account DTOs

Data Transfer Objects for user account operations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class UserAccountDTO:
    """User account DTO"""
    id: str
    user_id: str
    email: str
    account_name: Optional[str] = None
    provider: str = "google"
    is_primary: bool = False
    is_active: bool = True
    last_sync: Optional[datetime] = None
    sync_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateUserAccountDTO:
    """DTO for creating a user account"""
    user_id: str
    email: str
    account_name: Optional[str] = None
    provider: str = "google"
    is_primary: bool = False


@dataclass
class UpdateUserAccountDTO:
    """DTO for updating a user account"""
    account_name: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    sync_enabled: Optional[bool] = None


@dataclass
class UserAccountListDTO:
    """DTO for list of user accounts"""
    accounts: List[UserAccountDTO]
    total_count: int
    page: int
    page_size: int 