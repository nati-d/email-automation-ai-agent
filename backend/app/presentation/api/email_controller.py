"""
Email Controller

API endpoints for email operations with clean architecture.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ...application.dto.email_dto import EmailDTO, CreateEmailDTO, UpdateEmailDTO
from ...application.dto.user_dto import UserDTO
from ...application.use_cases.email_use_cases import (
    CreateEmailUseCase, GetEmailUseCase, UpdateEmailUseCase, DeleteEmailUseCase,
    SendNewEmailUseCase, ListEmailsUseCase, FetchInitialEmailsUseCase,
    SummarizeEmailUseCase, SummarizeMultipleEmailsUseCase
)
from ..models.email_models import (
    EmailResponse, CreateEmailRequest, UpdateEmailRequest, EmailListResponse,
    SendEmailRequest, SendEmailResponse, EmailSummaryResponse, FetchEmailsByAccountRequest
)

from ..middleware.auth_middleware import get_current_user, get_current_user_with_session_id
from ...infrastructure.di.container import get_container
from ...domain.value_objects.email_address import EmailAddress


router = APIRouter(prefix="/emails", tags=["emails"])


def _dto_to_response(dto: EmailDTO) -> dict:
    """Convert DTO to response dict"""
    return {
        "id": dto.id,
        "subject": dto.subject,
        "sender": dto.sender,
        "recipients": dto.recipients,
        "cc": dto.cc,
        "bcc": dto.bcc,
        "content": dto.content,
        "content_type": dto.content_type,
        "status": dto.status,
        "priority": dto.priority,
        "category": dto.category,
        "sent_at": dto.sent_at,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at,
        "metadata": dto.metadata,
        "account_owner": dto.account_owner,
        "email_holder": dto.email_holder,
        "summary": dto.summary,
        "sentiment": dto.sentiment,
        "key_points": dto.key_points,
        "action_items": dto.action_items,
        "summary_generated_at": dto.summary_generated_at
    }


@router.get("/", response_model=EmailListResponse)
async def get_my_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in subject and content")
) -> EmailListResponse:
    """Get emails for the current user with filtering and pagination"""
    container = get_container()
    use_case = container.list_emails_use_case()
    
    # Get emails filtered by account owner (current user's email)
    result = await use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    
    emails = [EmailResponse(**{**email.__dict__}) for email in result.emails]
    
    return EmailListResponse(
        emails=emails,
        total_count=result.total_count,
        page=result.page,
        page_size=result.page_size,
        has_next=False,  # Simple pagination for now
        has_prev=False
    )


@router.post("/fetch-by-account", response_model=EmailListResponse)
async def get_emails_by_account(
    request: FetchEmailsByAccountRequest,
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in subject and content")
) -> EmailListResponse:
    """
    Get emails for a specific account if the current user owns it.
    
    This endpoint requires authorization and only returns emails if:
    1. The authenticated user owns the account (account_owner matches current user's email)
    2. The requested email matches the email_holder field
    """
    # Extract email from request payload
    email = request.email
    
    # Validate email format
    try:
        EmailAddress.create(email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email format: {str(e)}"
        )
    
    container = get_container()
    use_case = container.list_emails_use_case()
    
    # First, get emails filtered by account owner (current user's email)
    # This ensures the user can only access emails they own
    result = await use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    
    # Filter emails to only include those where email_holder matches the requested email
    filtered_emails = []
    for email_dto in result.emails:
        if email_dto.email_holder == email:
            filtered_emails.append(email_dto)
    
    # Convert to response format
    emails = [EmailResponse(**{**email.__dict__}) for email in filtered_emails]
    
    return EmailListResponse(
        emails=emails,
        total_count=len(filtered_emails),
        page=1,
        page_size=len(filtered_emails),
        has_next=False,
        has_prev=False
    )


@router.post("/fetch-starred", response_model=SendEmailResponse)
async def fetch_starred_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of starred emails to fetch")
) -> SendEmailResponse:
    """
    Fetch starred emails from Gmail and store them in the database.
    
    This endpoint will:
    1. Connect to Gmail using the user's OAuth token
    2. Fetch starred emails using the 'is:starred' query
    3. Store them in the database with is_starred flag
    4. Optionally summarize them using AI
    """
    try:
        container = get_container()
        use_case = container.fetch_starred_emails_use_case()
        
        # Get OAuth token for the current user
        # This would need to be implemented based on your OAuth session management
        # For now, we'll need to get the OAuth token from the user's session
        
        # TODO: Get OAuth token from user session
        # oauth_token = get_user_oauth_token(current_user.id)
        
        # For now, return a placeholder response
        return SendEmailResponse(
            success=True,
            message="Starred emails fetch endpoint created. OAuth token integration needed.",
            email_id=None,
            sent_at=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch starred emails: {str(e)}"
        )


@router.get("/tasks", response_model=EmailListResponse)
async def get_task_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip")
) -> EmailListResponse:
    """Get task-related emails for the current user"""
    container = get_container()
    use_case = container.list_emails_use_case()
    
    result = await use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    
    # Filter for task emails using email_type
    task_emails = [email for email in result.emails if getattr(email, 'email_type', None) == 'tasks']
    
    emails = [EmailResponse(**{**email.__dict__}) for email in task_emails]
    
    return EmailListResponse(
        emails=emails,
        total_count=len(task_emails),
        page=1,
        page_size=len(task_emails),
        has_next=False,
        has_prev=False
    )


@router.get("/inbox", response_model=EmailListResponse)
async def get_inbox_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip")
) -> EmailListResponse:
    """Get inbox emails for the current user"""
    container = get_container()
    use_case = container.list_emails_use_case()
    
    result = await use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    
    # Filter for inbox emails using email_type
    inbox_emails = [email for email in result.emails if getattr(email, 'email_type', None) == 'inbox']
    
    emails = [EmailResponse(**{**email.__dict__}) for email in inbox_emails]
    
    return EmailListResponse(
        emails=emails,
        total_count=len(inbox_emails),
        page=1,
        page_size=len(inbox_emails),
        has_next=False,
        has_prev=False
    )


@router.get("/starred", response_model=EmailListResponse)
async def get_starred_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip")
) -> EmailListResponse:
    """Get starred emails for the current user"""
    container = get_container()
    use_case = container.list_emails_use_case()
    
    result = await use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    
    # Filter for starred emails (check metadata for is_starred flag)
    starred_emails = []
    for email in result.emails:
        if hasattr(email, 'metadata') and email.metadata and email.metadata.get('is_starred'):
            starred_emails.append(email)
    
    emails = [EmailResponse(**{**email.__dict__}) for email in starred_emails]
    
    return EmailListResponse(
        emails=emails,
        total_count=len(starred_emails),
        page=1,
        page_size=len(starred_emails),
        has_next=False,
        has_prev=False
    )


@router.get("/category/{category_name}", response_model=EmailListResponse)
async def get_emails_by_category(
    category_name: str,
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip")
) -> EmailListResponse:
    """Get emails by category for the current user"""
    container = get_container()
    use_case = container.list_emails_use_case()
    
    result = await use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    
    # Filter for category
    category_emails = [email for email in result.emails if email.category == category_name]
    
    emails = [EmailResponse(**{**email.__dict__}) for email in category_emails]
    
    return EmailListResponse(
        emails=emails,
        total_count=len(category_emails),
        page=1,
        page_size=len(category_emails),
        has_next=False,
        has_prev=False
    )


@router.get("/sent", response_model=EmailListResponse)
async def get_sent_emails(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of sent emails to return"),
    offset: int = Query(0, ge=0, description="Number of sent emails to skip")
) -> EmailListResponse:
    """Get sent emails for the current user (database only)"""
    container = get_container()
    list_emails_use_case = container.list_emails_use_case()
    emails_result = await list_emails_use_case.execute(
        account_owner=current_user.email,
        limit=limit
    )
    sent_emails = [email for email in emails_result.emails if getattr(email, 'email_type', None) == 'sent']
    emails = [EmailResponse(**{**email.__dict__}) for email in sent_emails]
    return EmailListResponse(
        emails=emails,
        total_count=len(sent_emails),
        page=1,
        page_size=limit,
        has_next=False,
        has_prev=False
    )


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> EmailResponse:
    """Get a specific email by ID"""
    container = get_container()
    use_case = container.get_email_use_case()
    
    email = await use_case.execute(email_id)
    
    # Check if the user owns this email
    if email.account_owner != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this email"
        )
    
    return EmailResponse(**{**email.__dict__})


@router.post("/", response_model=EmailResponse)
async def create_email(
    request: CreateEmailRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> EmailResponse:
    """Create a new email"""
    container = get_container()
    use_case = container.create_email_use_case()
    
    dto = CreateEmailDTO(
        subject=request.subject,
        sender=request.sender,
        recipients=request.recipients,
        cc=request.cc,
        bcc=request.bcc,
        content=request.content,
        content_type=request.content_type,
        status=request.status,
        priority=request.priority,
        category=request.category,
        metadata=request.metadata,
        account_owner=current_user.email,  # Set current user as account owner
        email_holder=current_user.email    # Set current user as email holder for outgoing emails
    )
    
    email = await use_case.execute(dto)
    
    return EmailResponse(**{**email.__dict__})


@router.put("/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: str,
    request: UpdateEmailRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> EmailResponse:
    """Update an email"""
    container = get_container()
    use_case = container.update_email_use_case()
    
    # First get the email to check ownership
    get_use_case = container.get_email_use_case()
    existing_email = await get_use_case.execute(email_id)
    
    if existing_email.account_owner != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this email"
        )
    
    dto = UpdateEmailDTO(
        subject=request.subject,
        recipients=request.recipients,
        cc=request.cc,
        bcc=request.bcc,
        content=request.content,
        content_type=request.content_type,
        status=request.status,
        priority=request.priority,
        category=request.category,
        metadata=request.metadata
    )
    
    email = await use_case.execute(email_id, dto)
    
    return EmailResponse(**{**email.__dict__})


@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> dict:
    """Delete an email"""
    container = get_container()
    use_case = container.delete_email_use_case()
    
    # First get the email to check ownership
    get_use_case = container.get_email_use_case()
    existing_email = await get_use_case.execute(email_id)
    
    if existing_email.account_owner != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this email"
        )
    
    success = await use_case.execute(email_id)
    
    if success:
        return {"success": True, "message": "Email deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )


@router.post("/send", response_model=SendEmailResponse)
async def send_email(
    request: SendEmailRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> SendEmailResponse:
    """Send a new email"""
    container = get_container()
    use_case = container.send_new_email_use_case()
    
    result = await use_case.execute(
        subject=request.subject,
        content=request.content,
        recipients=request.recipients,
        cc=request.cc,
        bcc=request.bcc,
        sender_email=current_user.email,  # Use current user's email as sender
        content_type=request.content_type,
        priority=request.priority
    )
    
    return SendEmailResponse(
        success=result["success"],
        message=result["message"],
        email_id=result.get("email_id"),
        sent_at=result.get("sent_at")
    )


@router.post("/{email_id}/summarize", response_model=EmailSummaryResponse)
async def summarize_email(
    email_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> EmailSummaryResponse:
    """Summarize a specific email"""
    container = get_container()
    use_case = container.summarize_email_use_case()
    
    # First get the email to check ownership
    get_use_case = container.get_email_use_case()
    existing_email = await get_use_case.execute(email_id)
    
    if existing_email.account_owner != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to summarize this email"
        )
    
    result = await use_case.execute(email_id)
    
    return EmailSummaryResponse(
        success=result["success"],
        message=result["message"],
        summary=result.get("summary"),
        sentiment=result.get("sentiment"),
        key_points=result.get("key_points"),
        action_items=result.get("action_items")
    )


@router.post("/summarize-multiple", response_model=List[EmailSummaryResponse])
async def summarize_multiple_emails(
    email_ids: List[str],
    current_user: UserDTO = Depends(get_current_user)
) -> List[EmailSummaryResponse]:
    """Summarize multiple emails"""
    container = get_container()
    use_case = container.summarize_multiple_emails_use_case()
    
    # Check ownership for all emails
    get_use_case = container.get_email_use_case()
    for email_id in email_ids:
        existing_email = await get_use_case.execute(email_id)
        if existing_email.account_owner != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to summarize email {email_id}"
            )
    
    results = await use_case.execute(email_ids)
    
    return [
        EmailSummaryResponse(
            success=result["success"],
            message=result["message"],
            summary=result.get("summary"),
            sentiment=result.get("sentiment"),
            key_points=result.get("key_points"),
            action_items=result.get("action_items")
        )
        for result in results
    ]