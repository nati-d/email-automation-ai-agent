"""
Email Presentation Models

Pydantic models for email API contracts.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base_models import PaginationResponse


class CreateEmailRequest(BaseModel):
    """Request model for creating emails"""
    sender: EmailStr
    recipients: List[EmailStr] = Field(..., min_items=1, max_items=100)
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=50000)
    html_body: Optional[str] = Field(None, max_length=100000)
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender": "agent@example.com",
                "recipients": ["user@example.com", "admin@example.com"],
                "subject": "Welcome to Email Agent",
                "body": "Thank you for using our email agent service!",
                "html_body": "<h1>Welcome!</h1><p>Thank you for using our email agent service!</p>",
                "metadata": {"campaign": "welcome", "version": "1.0"}
            }
        }


class UpdateEmailRequest(BaseModel):
    """Request model for updating emails"""
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = Field(None, min_length=1, max_length=50000)
    html_body: Optional[str] = Field(None, max_length=100000)
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Updated Welcome Email",
                "body": "Updated content for the welcome email",
                "html_body": "<h1>Updated Welcome!</h1>",
                "metadata": {"updated": True}
            }
        }


class ScheduleEmailRequest(BaseModel):
    """Request model for scheduling emails"""
    scheduled_at: datetime = Field(..., description="When to send the email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheduled_at": "2024-01-20T10:00:00Z"
            }
        }


class EmailResponse(BaseModel):
    """Response model for email operations"""
    id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    # Account ownership fields
    account_owner: Optional[str] = None
    email_holder: Optional[str] = None
    # AI Summarization fields
    summary: Optional[str] = None
    main_concept: Optional[str] = None
    sentiment: Optional[str] = None
    key_topics: List[str] = []
    summarized_at: Optional[datetime] = None
    # Email categorization
    email_type: str = "inbox"
    category: Optional[str] = None
    categorized_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "email123",
                "sender": "agent@example.com",
                "recipients": ["user@example.com"],
                "subject": "Welcome to Email Agent",
                "body": "Thank you for using our service!",
                "html_body": "<h1>Welcome!</h1>",
                "status": "draft",
                "created_at": "2024-01-15T10:30:00Z",
                "metadata": {"campaign": "welcome"}
            }
        }


class EmailListResponse(PaginationResponse):
    """Response model for email list operations"""
    emails: List[EmailResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    {
                        "id": "email123",
                        "sender": "agent@example.com",
                        "recipients": ["user@example.com"],
                        "subject": "Welcome Email",
                        "body": "Welcome message",
                        "status": "sent",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total_count": 1,
                "page": 1,
                "page_size": 50,
                "has_next": False,
                "has_previous": False
            }
        }


class SendEmailRequest(BaseModel):
    """Request model for sending emails"""
    recipients: List[EmailStr] = Field(..., min_items=1, max_items=100, description="List of recipient email addresses")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, max_length=50000, description="Email body text")
    html_body: Optional[str] = Field(None, max_length=100000, description="HTML version of email body")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["user@example.com", "admin@example.com"],
                "subject": "Important Update",
                "body": "This is an important update about your account.",
                "html_body": "<h1>Important Update</h1><p>This is an important update about your account.</p>",
                "metadata": {"priority": "high", "category": "account"}
            }
        } 