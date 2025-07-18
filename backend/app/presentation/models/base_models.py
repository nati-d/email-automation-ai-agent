"""
Base Presentation Models

Common Pydantic models for API contracts.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()


class PaginationParams(BaseModel):
    """Pagination parameters model"""
    page: int = 1
    page_size: int = 50
    offset: int = 0


class PaginationResponse(BaseModel):
    """Pagination response model"""
    page: int
    page_size: int
    total_count: int
    has_next: bool
    has_prev: bool


class SuccessResponse(BaseModel):
    """Standard success response model"""
    message: str
    timestamp: datetime = datetime.utcnow()
    data: Optional[Dict[str, Any]] = None 