"""
User Account API Models

Pydantic models for user account API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserAccountResponse(BaseModel):
    """User account response model"""
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


class CreateUserAccountRequest(BaseModel):
    """Create user account request model"""
    email: str = Field(..., description="Email address of the account")
    account_name: Optional[str] = Field(None, description="Optional name for the account")
    provider: str = Field("google", description="OAuth provider")
    is_primary: bool = Field(False, description="Whether this is the primary account")


class UpdateUserAccountRequest(BaseModel):
    """Update user account request model"""
    account_name: Optional[str] = Field(None, description="Optional name for the account")
    is_primary: Optional[bool] = Field(None, description="Whether this is the primary account")
    is_active: Optional[bool] = Field(None, description="Whether this account is active")
    sync_enabled: Optional[bool] = Field(None, description="Whether automatic sync is enabled")


class UserAccountListResponse(BaseModel):
    """User account list response model"""
    accounts: List[UserAccountResponse]
    total_count: int
    page: int
    page_size: int


class UserAccountOperationResponse(BaseModel):
    """User account operation response model"""
    success: bool
    message: str
    account: Optional[UserAccountResponse] = None 