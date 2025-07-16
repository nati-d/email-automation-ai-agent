"""
Email Controller

Only authenticated users can access their emails via GET /emails.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional

# Application layer
from ...application.dto.email_dto import EmailDTO, EmailListDTO, SendEmailDTO
from ...application.dto.user_dto import UserDTO
from ...application.use_cases.email_use_cases import (
    ListEmailsUseCase, 
    SendNewEmailUseCase,
    SummarizeEmailUseCase,
    SummarizeMultipleEmailsUseCase
)

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container

# Presentation models
from ..models.email_models import EmailListResponse, SendEmailRequest

# Middleware
from ..middleware.auth_middleware import get_current_user

# Security scheme
security = HTTPBearer()

router = APIRouter()


def get_list_emails_use_case(container: Container = Depends(get_container)) -> ListEmailsUseCase:
    return container.list_emails_use_case()


def get_send_new_email_use_case(container: Container = Depends(get_container)) -> SendNewEmailUseCase:
    return container.send_new_email_use_case()


def get_summarize_email_use_case(container: Container = Depends(get_container)) -> SummarizeEmailUseCase:
    return container.summarize_email_use_case()


def get_summarize_multiple_emails_use_case(container: Container = Depends(get_container)) -> SummarizeMultipleEmailsUseCase:
    return container.summarize_multiple_emails_use_case()


def _dto_to_response(dto: EmailDTO) -> dict:
    return {
        "id": dto.id,
        "sender": dto.sender,
        "recipients": dto.recipients,
        "subject": dto.subject,
        "body": dto.body,
        "html_body": dto.html_body,
        "status": dto.status,
        "scheduled_at": dto.scheduled_at,
        "sent_at": dto.sent_at,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at,
        "metadata": dto.metadata,
        # AI Summarization fields
        "summary": dto.summary,
        "main_concept": dto.main_concept,
        "sentiment": dto.sentiment,
        "key_topics": dto.key_topics,
        "summarized_at": dto.summarized_at.isoformat() if dto.summarized_at else None,
        # Email categorization
        "email_type": dto.email_type,
        "categorized_at": dto.categorized_at.isoformat() if dto.categorized_at else None
    }


def _handle_domain_exception(e: DomainException) -> HTTPException:
    if isinstance(e, EntityNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message}
        )


@router.get("/emails",
           response_model=EmailListResponse,
           summary="Get My Emails",
           description="Get emails for the currently authenticated user.",
           dependencies=[Depends(security)])
async def get_my_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = 50,
    use_case: ListEmailsUseCase = Depends(get_list_emails_use_case)
) -> EmailListResponse:
    """
    Get emails for the currently authenticated user.
    Requires a valid session ID in either:
    - X-Session-ID header
    - session_id query parameter
    """
    try:
        dto = await use_case.execute(recipient=current_user.email, limit=limit)
        email_responses = [_dto_to_response(email_dto) for email_dto in dto.emails]
        return EmailListResponse(
            emails=email_responses,
            total_count=dto.total_count,
            page=dto.page,
            page_size=dto.page_size,
            has_next=dto.has_next,
            has_previous=dto.has_previous
        )
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/emails/send",
           response_model=dict,
           summary="Send Email",
           description="Send a new email using the authenticated user as sender.",
           dependencies=[Depends(security)])
async def send_email(
    request: SendEmailRequest,
    current_user: UserDTO = Depends(get_current_user),
    use_case: SendNewEmailUseCase = Depends(get_send_new_email_use_case)
) -> dict:
    """
    Send a new email using the authenticated user as the sender.
    
    The sender will automatically be set to the authenticated user's email address.
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        print(f"🔍 DEBUG: EmailController.send_email() called")
        print(f"   👤 Current user: {current_user.email}")
        print(f"   📧 Request details:")
        print(f"      recipients: {request.recipients}")
        print(f"      subject: {request.subject}")
        print(f"      body length: {len(request.body)} chars")
        print(f"      html_body: {'provided' if request.html_body else 'None'}")
        
        # Convert recipients to strings
        recipients = [str(recipient) for recipient in request.recipients]
        print(f"🔍 DEBUG: Converted recipients: {recipients}")
        
        print(f"🔍 DEBUG: About to execute use case")
        # Execute use case with authenticated user as sender
        email_dto = await use_case.execute(
            sender_email=current_user.email,
            recipients=recipients,
            subject=request.subject,
            body=request.body,
            html_body=request.html_body
        )
        print(f"🔍 DEBUG: Use case executed successfully, email_dto.id: {email_dto.id}")
        
        response_data = {
            "message": "Email sent successfully",
            "email": _dto_to_response(email_dto),
            "sender": current_user.email,
            "recipients": recipients
        }
        print(f"🔍 DEBUG: Returning response with email status: {email_dto.status}")
        return response_data
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/emails/{email_id}/summarize",
           response_model=dict,
           summary="Summarize Email",
           description="Summarize an email using AI to extract key information.",
           dependencies=[Depends(security)])
async def summarize_email(
    email_id: str,
    current_user: UserDTO = Depends(get_current_user),
    use_case: SummarizeEmailUseCase = Depends(get_summarize_email_use_case)
) -> dict:
    """
    Summarize an email using AI to extract key information including:
    - Summary of content
    - Main concept/purpose
    - Sentiment analysis
    - Key topics
    
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        print(f"🔍 DEBUG: EmailController.summarize_email() called")
        print(f"   👤 Current user: {current_user.email}")
        print(f"   📧 Email ID: {email_id}")
        
        result = await use_case.execute(email_id)
        
        return {
            "message": result.get("message", "Email summarization completed"),
            "success": result.get("success", False),
            "already_summarized": result.get("already_summarized", False),
            "summarization": result.get("summarization", {})
        }
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/emails/summarize-batch",
           response_model=dict,
           summary="Summarize Multiple Emails",
           description="Summarize multiple emails in batch using AI.",
           dependencies=[Depends(security)])
async def summarize_multiple_emails(
    email_ids: list[str],
    current_user: UserDTO = Depends(get_current_user),
    use_case: SummarizeMultipleEmailsUseCase = Depends(get_summarize_multiple_emails_use_case)
) -> dict:
    """
    Summarize multiple emails in batch using AI.
    
    Args:
        email_ids: List of email IDs to summarize
        
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        print(f"🔍 DEBUG: EmailController.summarize_multiple_emails() called")
        print(f"   👤 Current user: {current_user.email}")
        print(f"   📧 Email IDs: {email_ids}")
        
        if not email_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_REQUEST", "message": "email_ids list cannot be empty"}
            )
        
        if len(email_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_REQUEST", "message": "Cannot summarize more than 50 emails at once"}
            )
        
        result = await use_case.execute(email_ids)
        
        return {
            "message": result.get("message", "Batch summarization completed"),
            "success": result.get("success", False),
            "total_processed": result.get("total_processed", 0),
            "successful": result.get("successful", 0),
            "already_summarized": result.get("already_summarized", 0),
            "failed": result.get("failed", 0),
            "errors": result.get("errors", [])
        }
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/emails/tasks",
           response_model=EmailListResponse,
           summary="Get Task Emails",
           description="Get emails categorized as tasks for the currently authenticated user.",
           dependencies=[Depends(security)])
async def get_task_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = 50,
    use_case: ListEmailsUseCase = Depends(get_list_emails_use_case)
) -> EmailListResponse:
    """
    Get emails categorized as tasks for the currently authenticated user.
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        # For now, we'll filter by email_type in the response
        # In the future, we can add a specific use case for task emails
        dto = await use_case.execute(recipient=current_user.email, limit=limit)
        
        # Filter for task emails
        task_emails = [email_dto for email_dto in dto.emails if email_dto.email_type == "tasks"]
        email_responses = [_dto_to_response(email_dto) for email_dto in task_emails]
        
        return EmailListResponse(
            emails=email_responses,
            total_count=len(task_emails),
            page=dto.page,
            page_size=dto.page_size,
            has_next=dto.has_next,
            has_previous=dto.has_previous
        )
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/emails/inbox",
           response_model=EmailListResponse,
           summary="Get Inbox Emails",
           description="Get emails categorized as inbox for the currently authenticated user.",
           dependencies=[Depends(security)])
async def get_inbox_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = 50,
    use_case: ListEmailsUseCase = Depends(get_list_emails_use_case)
) -> EmailListResponse:
    """
    Get emails categorized as inbox for the currently authenticated user.
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        # For now, we'll filter by email_type in the response
        # In the future, we can add a specific use case for inbox emails
        dto = await use_case.execute(recipient=current_user.email, limit=limit)
        
        # Filter for inbox emails
        inbox_emails = [email_dto for email_dto in dto.emails if email_dto.email_type == "inbox"]
        email_responses = [_dto_to_response(email_dto) for email_dto in inbox_emails]
        
        return EmailListResponse(
            emails=email_responses,
            total_count=len(inbox_emails),
            page=dto.page,
            page_size=dto.page_size,
            has_next=dto.has_next,
            has_previous=dto.has_previous
        )
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )