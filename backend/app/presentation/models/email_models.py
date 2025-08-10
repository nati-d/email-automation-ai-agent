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
    """Request model for sending emails (minimal)"""
    recipients: List[EmailStr] = Field(..., min_items=1, max_items=100, description="List of recipient email addresses")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, max_length=50000, description="Email body text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["user@example.com", "admin@example.com"],
                "subject": "Important Update",
                "body": "This is an important update about your account."
            }
        }


class FetchEmailsByAccountRequest(BaseModel):
    """Request model for fetching emails by account"""
    email: str = Field(..., description="Email address of the account to fetch emails from")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "work@example.com"
            }
        }


class SendEmailResponse(BaseModel):
    """Response model for send email operations"""
    success: bool
    message: str
    email_id: Optional[str] = None
    sent_at: Optional[datetime] = None


class EmailSummaryResponse(BaseModel):
    """Response model for email summarization"""
    success: bool
    message: str
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    key_points: Optional[List[str]] = None
    action_items: Optional[List[str]] = None


class CreateDraftRequest(BaseModel):
    """Request model for creating email drafts"""
    recipients: List[EmailStr] = Field(..., min_items=1, max_items=100, description="List of recipient email addresses")
    subject: str = Field("", max_length=200, description="Email subject (can be empty for drafts)")
    body: str = Field("", max_length=50000, description="Email body text (can be empty for drafts)")
    html_body: Optional[str] = Field(None, max_length=100000, description="Email HTML body")
    sync_with_gmail: bool = Field(False, description="Whether to sync with Gmail")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["user@example.com"],
                "subject": "Draft Email Subject",
                "body": "This is a draft email body.",
                "html_body": "<p>This is a draft email body.</p>",
                "sync_with_gmail": True
            }
        }


class UpdateDraftRequest(BaseModel):
    """Request model for updating email drafts"""
    recipients: Optional[List[EmailStr]] = Field(None, max_items=100, description="List of recipient email addresses")
    subject: Optional[str] = Field(None, max_length=200, description="Email subject (can be empty for drafts)")
    body: Optional[str] = Field(None, max_length=50000, description="Email body text (can be empty for drafts)")
    html_body: Optional[str] = Field(None, max_length=100000, description="Email HTML body")
    sync_with_gmail: bool = Field(False, description="Whether to sync with Gmail")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Updated Draft Subject",
                "body": "Updated draft body content.",
                "sync_with_gmail": True
            }
        }


class DraftResponse(BaseModel):
    """Response model for draft operations"""
    id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    account_owner: Optional[str] = None
    gmail_draft_id: Optional[str] = None
    synced_with_gmail: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "draft123",
                "sender": "user@example.com",
                "recipients": ["recipient@example.com"],
                "subject": "Draft Email",
                "body": "Draft content",
                "status": "draft",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:35:00Z",
                "synced_with_gmail": True
            }
        }


class DraftListResponse(PaginationResponse):
    """Response model for draft list operations"""
    drafts: List[DraftResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "drafts": [
                    {
                        "id": "draft123",
                        "sender": "user@example.com",
                        "recipients": ["recipient@example.com"],
                        "subject": "Draft Email",
                        "body": "Draft content",
                        "status": "draft",
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


class DraftActionResponse(BaseModel):
    """Response model for draft actions (send, delete, etc.)"""
    success: bool
    message: str
    draft_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Draft sent successfully",
                "draft_id": "draft123"
            }
        } 