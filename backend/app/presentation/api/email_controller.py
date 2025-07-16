"""
Email Controller

Only authenticated users can access their emails via GET /emails.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

# Application layer
from ...application.dto.email_dto import EmailDTO, EmailListDTO
from ...application.dto.user_dto import UserDTO
from ...application.use_cases.email_use_cases import ListEmailsUseCase

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container

# Presentation models
from ..models.email_models import EmailListResponse

# Middleware
from ..middleware.auth_middleware import get_current_user

router = APIRouter()


def get_list_emails_use_case(container: Container = Depends(get_container)) -> ListEmailsUseCase:
    return container.list_emails_use_case()


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
        "metadata": dto.metadata
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
           description="Get emails for the currently authenticated user.")
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