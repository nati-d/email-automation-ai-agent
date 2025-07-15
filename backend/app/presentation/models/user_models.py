"""
User Presentation Models

Pydantic models for user API contracts.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateUserRequest(BaseModel):
    """Request model for creating users"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="user", pattern="^(admin|user|agent)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "role": "user"
            }
        }


class UpdateUserRequest(BaseModel):
    """Request model for updating users"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|user|agent)$")
    is_active: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "role": "admin",
                "is_active": True
            }
        }


class UserResponse(BaseModel):
    """Response model for user operations"""
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user123",
                "email": "user@example.com",
                "name": "John Doe",
                "role": "user",
                "is_active": True,
                "last_login": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-10T09:00:00Z"
            }
        } 