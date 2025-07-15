"""
Email Controller

Clean architecture implementation of email API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime

# Application layer
from ...application.dto.email_dto import EmailDTO, CreateEmailDTO, UpdateEmailDTO, EmailListDTO
from ...application.use_cases.email_use_cases import (
    CreateEmailUseCase, GetEmailUseCase, UpdateEmailUseCase,
    DeleteEmailUseCase, SendEmailUseCase, ScheduleEmailUseCase,
    ListEmailsUseCase
)

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container

# Presentation models
from ..models.email_models import (
    CreateEmailRequest, UpdateEmailRequest, EmailResponse,
    EmailListResponse, ScheduleEmailRequest
)
from ..models.base_models import ErrorResponse


router = APIRouter()


# Dependency injection
def get_create_email_use_case(container: Container = Depends(get_container)) -> CreateEmailUseCase:
    return container.create_email_use_case()


def get_get_email_use_case(container: Container = Depends(get_container)) -> GetEmailUseCase:
    return container.get_email_use_case()


def get_update_email_use_case(container: Container = Depends(get_container)) -> UpdateEmailUseCase:
    return container.update_email_use_case()


def get_delete_email_use_case(container: Container = Depends(get_container)) -> DeleteEmailUseCase:
    return container.delete_email_use_case()


def get_send_email_use_case(container: Container = Depends(get_container)) -> SendEmailUseCase:
    return container.send_email_use_case()


def get_schedule_email_use_case(container: Container = Depends(get_container)) -> ScheduleEmailUseCase:
    return container.schedule_email_use_case()


def get_list_emails_use_case(container: Container = Depends(get_container)) -> ListEmailsUseCase:
    return container.list_emails_use_case()


def _dto_to_response(dto: EmailDTO) -> EmailResponse:
    """Convert DTO to response model"""
    return EmailResponse(
        id=dto.id,
        sender=dto.sender,
        recipients=dto.recipients,
        subject=dto.subject,
        body=dto.body,
        html_body=dto.html_body,
        status=dto.status,
        scheduled_at=dto.scheduled_at,
        sent_at=dto.sent_at,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        metadata=dto.metadata
    )


def _handle_domain_exception(e: DomainException) -> HTTPException:
    """Convert domain exception to HTTP exception"""
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


@router.post("/emails", 
            response_model=EmailResponse,
            summary="Create Email",
            description="Create a new email message.")
async def create_email(
    request: CreateEmailRequest,
    use_case: CreateEmailUseCase = Depends(get_create_email_use_case)
) -> EmailResponse:
    """Create a new email"""
    try:
        # Convert request to DTO
        dto = CreateEmailDTO(
            sender=request.sender,
            recipients=request.recipients,
            subject=request.subject,
            body=request.body,
            html_body=request.html_body,
            scheduled_at=request.scheduled_at,
            metadata=request.metadata or {}
        )
        
        # Execute use case
        result_dto = await use_case.execute(dto)
        
        # Convert to response
        return _dto_to_response(result_dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/emails/{email_id}",
           response_model=EmailResponse,
           summary="Get Email",
           description="Get email by ID.")
async def get_email(
    email_id: str,
    use_case: GetEmailUseCase = Depends(get_get_email_use_case)
) -> EmailResponse:
    """Get email by ID"""
    try:
        dto = await use_case.execute(email_id)
        return _dto_to_response(dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.put("/emails/{email_id}",
           response_model=EmailResponse,
           summary="Update Email",
           description="Update email content.")
async def update_email(
    email_id: str,
    request: UpdateEmailRequest,
    use_case: UpdateEmailUseCase = Depends(get_update_email_use_case)
) -> EmailResponse:
    """Update email content"""
    try:
        # Convert request to DTO
        dto = UpdateEmailDTO(
            subject=request.subject,
            body=request.body,
            html_body=request.html_body,
            scheduled_at=request.scheduled_at,
            metadata=request.metadata or {}
        )
        
        # Execute use case
        result_dto = await use_case.execute(email_id, dto)
        
        # Convert to response
        return _dto_to_response(result_dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.delete("/emails/{email_id}",
              summary="Delete Email",
              description="Delete email by ID.")
async def delete_email(
    email_id: str,
    use_case: DeleteEmailUseCase = Depends(get_delete_email_use_case)
) -> dict:
    """Delete email by ID"""
    try:
        success = await use_case.execute(email_id)
        return {"message": "Email deleted successfully", "email_id": email_id}
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/emails/{email_id}/send",
            response_model=EmailResponse,
            summary="Send Email",
            description="Send email by ID.")
async def send_email(
    email_id: str,
    use_case: SendEmailUseCase = Depends(get_send_email_use_case)
) -> EmailResponse:
    """Send email by ID"""
    try:
        dto = await use_case.execute(email_id)
        return _dto_to_response(dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/emails/{email_id}/schedule",
            response_model=EmailResponse,
            summary="Schedule Email",
            description="Schedule email for future sending.")
async def schedule_email(
    email_id: str,
    request: ScheduleEmailRequest,
    use_case: ScheduleEmailUseCase = Depends(get_schedule_email_use_case)
) -> EmailResponse:
    """Schedule email for future sending"""
    try:
        dto = await use_case.execute(email_id, request.scheduled_at)
        return _dto_to_response(dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/emails",
           response_model=EmailListResponse,
           summary="List Emails",
           description="List emails with optional filters.")
async def list_emails(
    sender: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    use_case: ListEmailsUseCase = Depends(get_list_emails_use_case)
) -> EmailListResponse:
    """List emails with optional filters"""
    try:
        dto = await use_case.execute(sender=sender, status=status, limit=limit)
        
        # Convert to response
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