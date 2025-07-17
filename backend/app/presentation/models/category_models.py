"""
Category Presentation Models

Pydantic models for category API contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CreateCategoryRequest(BaseModel):
    """Request model for creating categories"""
    name: str = Field(..., min_length=1, max_length=50, description="Category name")
    description: Optional[str] = Field(None, max_length=200, description="Category description (optional)")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code (optional, e.g., #FF5733)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Work"
            }
        }


class UpdateCategoryRequest(BaseModel):
    """Request model for updating categories"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Category name")
    description: Optional[str] = Field(None, max_length=200, description="Category description")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code (e.g., #FF5733)")
    is_active: Optional[bool] = Field(None, description="Whether the category is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Work Projects",
                "description": "Project-related work emails",
                "color": "#33FF57",
                "is_active": True
            }
        }


class CategoryResponse(BaseModel):
    """Response model for category data"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "category_123",
                "user_id": "user_456",
                "name": "Work",
                "description": "Work-related emails",
                "color": "#FF5733",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class CategoryListResponse(BaseModel):
    """Response model for category list"""
    categories: List[CategoryResponse]
    total_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": [
                    {
                        "id": "category_123",
                        "user_id": "user_456",
                        "name": "Work",
                        "description": "Work-related emails",
                        "color": "#FF5733",
                        "is_active": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total_count": 1
            }
        }


class RecategorizeEmailsResponse(BaseModel):
    """Response model for email re-categorization"""
    recategorized_count: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "recategorized_count": 15,
                "message": "Successfully re-categorized 15 emails"
            }
        } 