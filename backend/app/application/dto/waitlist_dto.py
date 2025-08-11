"""
Waitlist DTOs

Data Transfer Objects for waitlist operations.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class CreateWaitlistDTO(BaseModel):
    """DTO for creating waitlist entry"""
    email: EmailStr
    name: Optional[str] = None
    use_case: Optional[str] = None
    referral_source: Optional[str] = None


class WaitlistDTO(BaseModel):
    """DTO for waitlist entry data"""
    id: Optional[str] = None
    email: str
    name: Optional[str] = None
    use_case: Optional[str] = None
    referral_source: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_notified: bool = False


class WaitlistListDTO(BaseModel):
    """DTO for waitlist list response"""
    entries: List[WaitlistDTO]
    total_count: int
    page: int = 1
    page_size: int = 50


