"""
Email Controller

API endpoints for email operations with clean architecture.
"""

from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request

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
    """Get sent emails for the current user from the 'sent_email' collection"""
    container = get_container()
    email_repository = container.email_repository()
    
    # Fetch sent emails directly from the 'sent_email' collection
    sent_emails = await email_repository.find_sent_emails(
        account_owner=current_user.email,
        limit=limit
    )
    
    emails = [
        EmailResponse(
            **{
                **email.__dict__,
                "sender": str(email.sender),
                "recipients": [str(recipient) for recipient in email.recipients]
            }
        )
        for email in sent_emails
        ]
    return EmailListResponse(
        emails=emails,
        total_count=len(sent_emails),
        page=1,
        page_size=limit,
        has_next=False,
        has_prev=False
    )


@router.get("/sent/{email_id}", response_model=EmailResponse)
async def get_sent_email(
    email_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> EmailResponse:
    """Get a specific sent email by ID from the 'sent_email' collection"""
    container = get_container()
    email_repository = container.email_repository()
    
    # Fetch sent emails and find the specific one
    sent_emails = await email_repository.find_sent_emails(
        account_owner=current_user.email,
        limit=1000  # Get all sent emails to find the specific one
    )
    
    # Find the specific email by ID
    target_email = None
    for email in sent_emails:
        if email.id == email_id:
            target_email = email
            break
    
    if not target_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sent email not found"
        )
    
    # Check if the user owns this email
    if target_email.account_owner != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this email"
        )
    
    return EmailResponse(
        **{
            **target_email.__dict__,
            "sender": str(target_email.sender),
            "recipients": [str(recipient) for recipient in target_email.recipients]
        }
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


@router.post(
    "/send",
    response_model=SendEmailResponse,
    summary="Send an Email",
    description="""
    Send a new email to one or more recipients.
    
    Supports both JSON and multipart/form-data requests.
    
    JSON body:
    - `recipients`: List of recipient email addresses
    - `subject`: Email subject
    - `body`: Email body text (plain text)
    - `html_body` (optional)
    
    multipart/form-data fields:
    - `recipients`: JSON-encoded list of recipient emails (e.g. ["a@ex.com"]) or comma-separated string
    - `subject`
    - `body`
    - `html_body` (optional)
    - `attachments`: one or more files
    """,
    response_description="Result of the send email operation",
    tags=["emails", "send"]
)
async def send_email(
    request: Request,
    # Form fields (will be None for JSON requests)
    recipients: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    body: Optional[str] = Form(None),
    html_body: Optional[str] = Form(None),
    attachments: Optional[Union[UploadFile, List[UploadFile]]] = File(None),
    current_user: UserDTO = Depends(get_current_user)
) -> SendEmailResponse:
    """Send a new email to one or more recipients. Accepts JSON or multipart/form-data with attachments."""
    container = get_container()
    use_case = container.send_new_email_use_case()

    content_type = request.headers.get("content-type", "").lower()

    recipients_list: List[str]
    subject_value: str
    body_value: str
    html_body_value: Optional[str] = None
    attachment_payloads: List[dict] = []

    if content_type.startswith("multipart/form-data"):
        # Parse recipients
        recipients_raw = (recipients or "").strip()
        if not recipients_raw:
            # Fallback: parse from request.form() if not bound
            try:
                form = await request.form()
                # Try various common shapes
                recipients_raw = (form.get("recipients") or form.get("recipients[]") or "").strip()
                if not subject:
                    subject = form.get("subject")
                if not body:
                    body = form.get("body")
                if not html_body:
                    html_body = form.get("html_body")
                # Attachments fallback
                if attachments is None:
                    files = form.getlist("attachments") if hasattr(form, 'getlist') else []
                    attachments = files  # type: ignore
            except Exception:
                recipients_raw = ""
        if recipients_raw.startswith("["):
            # JSON encoded array
            import json
            try:
                recipients_list = json.loads(recipients_raw)
            except Exception:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid recipients JSON")
        else:
            # comma or space separated
            recipients_list = [e.strip() for e in recipients_raw.replace(";", ",").replace("\n", ",").replace(" ", ",").split(",") if e.strip()]

        # If still empty, try getting as a list from the form (recipients[])
        if not recipients_list and 'form' in locals():
            try:
                lst = form.getlist('recipients') if hasattr(form, 'getlist') else []  # type: ignore[name-defined]
                if lst:
                    recipients_list = [str(x).strip() for x in lst if str(x).strip()]
            except Exception:
                pass

        subject_value = subject or ""
        body_value = body or ""
        html_body_value = html_body

        # Normalize attachments to a list
        files_list: List[UploadFile] = []
        if isinstance(attachments, list):
            files_list = attachments
        elif attachments is not None:
            files_list = [attachments]

        # Attachments
        if files_list:
            for f in files_list:
                try:
                    content = await f.read()
                finally:
                    await f.close()
                attachment_payloads.append({
                    "filename": f.filename or "attachment",
                    "content_type": f.content_type or "application/octet-stream",
                    "data": content,
                })
    else:
        # JSON body
        try:
            body_json = await request.json()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")

        # Validate with Pydantic model
        # Allow recipients to be provided as a JSON string as well
        if isinstance(body_json.get("recipients"), str):
            import json as _json
            try:
                body_json["recipients"] = _json.loads(body_json["recipients"])  # type: ignore
            except Exception:
                # Leave as-is; Pydantic will raise a proper validation error
                pass

        req = SendEmailRequest(**body_json)
        recipients_list = [str(r) for r in req.recipients]
        subject_value = req.subject
        body_value = req.body
        html_body_value = None

    if not recipients_list:
        print(f"❌ send_email validation: empty recipients. Parsed content_type={content_type}, subject={subject_value!r}, body_len={len(body_value or '')}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one recipient is required")
    if not subject_value or not body_value:
        print(f"❌ send_email validation: missing subject/body. subject={subject_value!r}, body_len={len(body_value or '')}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Subject and body are required")

    result = await use_case.execute(
        subject=subject_value,
        body=body_value,
        recipients=recipients_list,
        sender_email=current_user.email,
        html_body=html_body_value,
        attachments=attachment_payloads or None,
    )
    return SendEmailResponse(
        success=True,
        message="Email sent successfully",
        email_id=getattr(result, "id", None),
        sent_at=getattr(result, "sent_at", None)
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