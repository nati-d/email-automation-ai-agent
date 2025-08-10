"""
Draft Controller

API endpoints for email draft operations with Gmail integration.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ...application.dto.user_dto import UserDTO
from ...application.use_cases.draft_use_cases import (
    CreateDraftUseCase, UpdateDraftUseCase, DeleteDraftUseCase,
    ListDraftsUseCase
)
from ..models.email_models import (
    CreateDraftRequest, UpdateDraftRequest, DraftResponse, 
    DraftListResponse, DraftActionResponse
)
from ..middleware.auth_middleware import get_current_user
from ...infrastructure.di.container import get_container


router = APIRouter(prefix="/drafts", tags=["drafts"])


def _email_to_draft_response(email) -> DraftResponse:
    """Convert Email entity to DraftResponse"""
    return DraftResponse(
        id=email.id,
        sender=str(email.sender),
        recipients=[str(recipient) for recipient in email.recipients],
        subject=email.subject,
        body=email.body,
        html_body=email.html_body,
        status=email.status.value,
        created_at=email.created_at,
        updated_at=email.updated_at,
        metadata=email.metadata,
        account_owner=email.account_owner,
        gmail_draft_id=email.metadata.get('gmail_draft_id'),
        synced_with_gmail=email.metadata.get('synced_with_gmail', False)
    )


@router.post("/", response_model=DraftResponse)
async def create_draft(
    request: CreateDraftRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> DraftResponse:
    """Create a new email draft"""
    try:
        print(f"🔄 Creating draft for user: {current_user.email}")
        print(f"   - Recipients: {request.recipients}")
        print(f"   - Subject: '{request.subject}'")
        print(f"   - Body length: {len(request.body)} chars")
        print(f"   - Local storage only")
        
        # Validate recipients
        if not request.recipients or len(request.recipients) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one recipient is required"
            )
        
        container = get_container()
        use_case = CreateDraftUseCase(
            email_repository=container.email_repository()
        )
        
        draft = await use_case.execute(
            sender_email=current_user.email,
            recipients=request.recipients,
            subject=request.subject or "No Subject",  # Provide default if empty
            body=request.body or "",  # Provide default if empty
            html_body=request.html_body
        )
        
        response = _email_to_draft_response(draft)
        print(f"✅ Draft created successfully: {response.id}")
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except RuntimeError as e:
        print(f"❌ Runtime error creating draft: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please check Firebase configuration."
        )
    except Exception as e:
        print(f"❌ Failed to create draft: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create draft: {str(e)}"
        )


@router.get("/", response_model=DraftListResponse)
async def list_drafts(
    current_user: UserDTO = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of drafts to return")
) -> DraftListResponse:
    """List email drafts for the current user"""
    try:
        print(f"🔄 Listing drafts for user: {current_user.email}")
        
        container = get_container()
        use_case = ListDraftsUseCase(
            email_repository=container.email_repository()
        )
        
        drafts = await use_case.execute(
            sender_email=current_user.email,
            limit=limit
        )
        
        print(f"✅ Found {len(drafts)} drafts, converting to responses...")
        
        draft_responses = []
        for draft in drafts:
            try:
                response = _email_to_draft_response(draft)
                draft_responses.append(response)
            except Exception as convert_error:
                print(f"⚠️ Failed to convert draft {draft.id} to response: {str(convert_error)}")
                continue
        
        print(f"✅ Successfully converted {len(draft_responses)} drafts to responses")
        
        return DraftListResponse(
            drafts=draft_responses,
            total_count=len(draft_responses),
            page=1,
            page_size=limit,
            has_next=False,
            has_prev=False
        )
        
    except RuntimeError as e:
        print(f"❌ Runtime error listing drafts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please check Firebase configuration."
        )
    except Exception as e:
        print(f"❌ Failed to list drafts: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list drafts: {str(e)}"
        )


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> DraftResponse:
    """Get a specific draft by ID"""
    try:
        print(f"🔄 Getting draft: {draft_id} for user: {current_user.email}")
        
        container = get_container()
        email_repository = container.email_repository()
        
        # Use the specific draft method to find in drafts collection
        draft = await email_repository.find_draft_by_id(draft_id)
        if not draft:
            print(f"❌ Draft not found: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
        
        # Check ownership
        if draft.account_owner != current_user.email:
            print(f"❌ Permission denied for draft: {draft_id}, owner: {draft.account_owner}, user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this draft"
            )
        
        print(f"✅ Draft found: {draft_id}")
        return _email_to_draft_response(draft)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get draft: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get draft: {str(e)}"
        )


@router.put("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    request: UpdateDraftRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> DraftResponse:
    """Update an existing email draft"""
    try:
        container = get_container()
        use_case = UpdateDraftUseCase(
            email_repository=container.email_repository()
        )
        
        updated_draft = await use_case.execute(
            draft_id=draft_id,
            sender_email=current_user.email,
            subject=request.subject,
            body=request.body,
            html_body=request.html_body,
            recipients=request.recipients
        )
        
        return _email_to_draft_response(updated_draft)
        
    except Exception as e:
        print(f"❌ Failed to update draft: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
        elif "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this draft"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update draft: {str(e)}"
            )


@router.delete("/{draft_id}", response_model=DraftActionResponse)
async def delete_draft(
    draft_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> DraftActionResponse:
    """Delete an email draft"""
    try:
        container = get_container()
        use_case = DeleteDraftUseCase(
            email_repository=container.email_repository()
        )
        
        success = await use_case.execute(
            draft_id=draft_id,
            sender_email=current_user.email
        )
        
        if success:
            return DraftActionResponse(
                success=True,
                message="Draft deleted successfully",
                draft_id=draft_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to delete draft: {str(e)}")
        if "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this draft"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete draft: {str(e)}"
            )


# Removed send_draft endpoint - use the existing sendEmail functionality instead


# Removed sync_drafts_with_gmail endpoint - drafts are local only now