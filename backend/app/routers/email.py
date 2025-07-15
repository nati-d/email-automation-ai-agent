from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from app.models.email_model import EmailMessage, EmailService, email_service
import datetime


class EmailCreateRequest(BaseModel):
    """Request model for creating emails"""
    sender: EmailStr
    recipients: List[EmailStr]
    subject: str
    body: str
    html_body: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender": "agent@example.com",
                "recipients": ["user@example.com", "admin@example.com"],
                "subject": "Welcome to Email Agent",
                "body": "Thank you for using our email agent service!",
                "html_body": "<h1>Welcome!</h1><p>Thank you for using our email agent service!</p>"
            }
        }


class EmailResponse(BaseModel):
    """Response model for email operations"""
    id: str
    sender: EmailStr
    recipients: List[EmailStr]
    subject: str
    body: str
    html_body: Optional[str] = None
    status: str
    timestamp: Optional[str] = None
    
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
                "timestamp": "2024-01-15T10:30:00.000Z"
            }
        }


class EmailListResponse(BaseModel):
    """Response model for email list operations"""
    emails: List[EmailResponse]
    count: int
    sender: Optional[str] = None
    
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
                        "timestamp": "2024-01-15T10:30:00.000Z"
                    }
                ],
                "count": 1,
                "sender": "agent@example.com"
            }
        }


class EmailStatusUpdate(BaseModel):
    """Model for updating email status"""
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "sent"
            }
        }


router = APIRouter()


@router.post("/emails",
            response_model=EmailResponse,
            summary="Create Email",
            description="Create and save a new email message to Firestore.",
            responses={
                200: {
                    "description": "Email created successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "id": "email123",
                                "sender": "agent@example.com",
                                "recipients": ["user@example.com"],
                                "subject": "Welcome to Email Agent",
                                "body": "Thank you for using our service!",
                                "status": "draft",
                                "timestamp": "2024-01-15T10:30:00.000Z"
                            }
                        }
                    }
                },
                400: {"description": "Invalid email data"},
                500: {"description": "Failed to create email"}
            })
async def create_email(email_request: EmailCreateRequest):
    """
    ## Create Email
    
    Creates a new email message and saves it to Firestore.
    
    ### Features
    
    - Supports both plain text and HTML content
    - Multiple recipients support
    - Email validation for sender and recipients
    - Automatic timestamp generation
    - Default status: "draft"
    
    ### Parameters
    
    - **sender**: Valid email address of the sender
    - **recipients**: List of valid recipient email addresses
    - **subject**: Email subject line
    - **body**: Plain text email content
    - **html_body**: Optional HTML version of the email content
    
    ### Email Status Values
    
    - `draft`: Email created but not sent
    - `sent`: Email successfully sent
    - `failed`: Email sending failed
    - `scheduled`: Email scheduled for future sending
    
    ### Use Cases
    
    - Creating email drafts
    - Preparing emails for batch sending
    - Email template management
    """
    try:
        # Create EmailMessage instance
        email = EmailMessage(
            sender=email_request.sender,
            recipients=email_request.recipients,
            subject=email_request.subject,
            body=email_request.body,
            html_body=email_request.html_body,
            timestamp=datetime.datetime.utcnow(),
            status="draft"
        )
        
        # Save to Firestore
        email_id = await email_service.save_email(email)
        
        # Return response
        return EmailResponse(
            id=email_id,
            sender=email.sender,
            recipients=email.recipients,
            subject=email.subject,
            body=email.body,
            html_body=email.html_body,
            status=email.status,
            timestamp=email.timestamp.isoformat() if email.timestamp else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create email: {str(e)}")


@router.get("/emails/{email_id}",
           response_model=EmailResponse,
           summary="Get Email",
           description="Retrieve a specific email by its ID.")
async def get_email(email_id: str):
    """
    ## Get Email by ID
    
    Retrieves a specific email message from Firestore using its document ID.
    
    ### Parameters
    
    - **email_id**: Unique identifier of the email document
    
    ### Response
    
    Returns complete email information including:
    - Sender and recipient details
    - Subject and content (both text and HTML)
    - Current status and timestamps
    
    ### Error Handling
    
    - Returns 404 if email not found
    - Returns 500 for database errors
    """
    try:
        email = await email_service.get_email(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return EmailResponse(
            id=email_id,
            sender=email.sender,
            recipients=email.recipients,
            subject=email.subject,
            body=email.body,
            html_body=email.html_body,
            status=email.status,
            timestamp=email.timestamp.isoformat() if email.timestamp else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email: {str(e)}")


@router.get("/emails",
           response_model=EmailListResponse,
           summary="List Emails",
           description="Get emails by sender with optional filtering and pagination.")
async def list_emails(
    sender: Optional[str] = None,
    limit: int = 50
):
    """
    ## List Emails
    
    Retrieves a list of emails with optional filtering by sender.
    
    ### Parameters
    
    - **sender**: Optional filter by sender email address
    - **limit**: Maximum number of emails to return (default: 50, max: 100)
    
    ### Features
    
    - Filter by sender email
    - Pagination support
    - Ordered by timestamp (newest first)
    - Returns email count
    
    ### Use Cases
    
    - Email management dashboards
    - Sender-specific email lists
    - Email audit trails
    - Bulk operations preparation
    """
    try:
        if sender:
            emails = await email_service.get_emails_by_sender(sender, limit)
        else:
            # For now, return empty list if no sender specified
            # In a real implementation, you might want to get all emails
            emails = []
        
        email_responses = []
        for email in emails:
            email_responses.append(EmailResponse(
                id=email.id or "",
                sender=email.sender,
                recipients=email.recipients,
                subject=email.subject,
                body=email.body,
                html_body=email.html_body,
                status=email.status,
                timestamp=email.timestamp.isoformat() if email.timestamp else None
            ))
        
        return EmailListResponse(
            emails=email_responses,
            count=len(email_responses),
            sender=sender
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list emails: {str(e)}")


@router.patch("/emails/{email_id}/status",
             summary="Update Email Status",
             description="Update the status of an existing email.")
async def update_email_status(email_id: str, status_update: EmailStatusUpdate):
    """
    ## Update Email Status
    
    Updates the status of an existing email message.
    
    ### Parameters
    
    - **email_id**: Unique identifier of the email document
    - **status**: New status value for the email
    
    ### Valid Status Values
    
    - `draft`: Email created but not sent
    - `sent`: Email successfully sent
    - `failed`: Email sending failed
    - `scheduled`: Email scheduled for future sending
    - `cancelled`: Email sending cancelled
    
    ### Use Cases
    
    - Mark emails as sent after successful delivery
    - Track failed email attempts
    - Update email workflow status
    """
    try:
        success = await email_service.update_email_status(email_id, status_update.status)
        if not success:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return {
            "message": f"Email status updated to {status_update.status}",
            "email_id": email_id,
            "status": status_update.status,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update email status: {str(e)}")


@router.delete("/emails/{email_id}",
              summary="Delete Email",
              description="Delete an email from Firestore.")
async def delete_email(email_id: str):
    """
    ## Delete Email
    
    Permanently deletes an email message from Firestore.
    
    ### Parameters
    
    - **email_id**: Unique identifier of the email document
    
    ### Warning
    
    This operation is irreversible. Once deleted, the email cannot be recovered.
    
    ### Use Cases
    
    - Clean up draft emails
    - Remove sensitive content
    - Email lifecycle management
    """
    try:
        success = await email_service.delete_email(email_id)
        if not success:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return {
            "message": "Email deleted successfully",
            "email_id": email_id,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {str(e)}") 