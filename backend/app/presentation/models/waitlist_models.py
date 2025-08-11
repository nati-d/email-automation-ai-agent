"""
Waitlist Presentation Models

Pydantic models for waitlist API contracts.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class JoinWaitlistRequest(BaseModel):
    """Request model for joining waitlist"""
    email: EmailStr = Field(..., description="Email address")
    name: Optional[str] = Field(None, max_length=100, description="Full name")
    use_case: Optional[str] = Field(None, max_length=500, description="How you plan to use EmailAI")
    referral_source: Optional[str] = Field(None, max_length=100, description="How did you hear about us?")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "name": "John Doe",
                "use_case": "Managing team emails and automating responses",
                "referral_source": "Twitter"
            }
        }


class WaitlistResponse(BaseModel):
    """Response model for waitlist entry"""
    id: Optional[str] = None
    email: str
    name: Optional[str] = None
    use_case: Optional[str] = None
    referral_source: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_notified: bool = False
    position: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "john_at_example_com",
                "email": "john@example.com",
                "name": "John Doe",
                "use_case": "Managing team emails",
                "referral_source": "Twitter",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "is_notified": False,
                "position": 42
            }
        }


class WaitlistJoinResponse(BaseModel):
    """Response model for joining waitlist"""
    success: bool = True
    message: str
    entry: WaitlistResponse
    total_entries: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully joined the waitlist!",
                "entry": {
                    "email": "john@example.com",
                    "name": "John Doe"
                },
                "total_entries": 1247
            }
        }


class WaitlistListResponse(BaseModel):
    """Response model for waitlist list"""
    entries: List[WaitlistResponse]
    total_count: int
    page: int = 1
    page_size: int = 50
    has_next: bool = False
    has_prev: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "entries": [
                    {
                        "email": "john@example.com",
                        "name": "John Doe",
                        "company": "Acme Corp",
                        "priority_score": 85,
                        "position": 42
                    }
                ],
                "total_count": 1247,
                "page": 1,
                "page_size": 50,
                "has_next": True,
                "has_prev": False
            }
        }


