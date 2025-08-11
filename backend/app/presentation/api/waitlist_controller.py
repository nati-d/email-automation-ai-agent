"""
Waitlist Controller

API endpoints for waitlist operations.
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional

from ...application.dto.waitlist_dto import CreateWaitlistDTO
from ...application.use_cases.waitlist_use_cases import (
    JoinWaitlistUseCase, ListWaitlistUseCase, CheckWaitlistStatusUseCase
)
from ..models.waitlist_models import (
    JoinWaitlistRequest, WaitlistJoinResponse, WaitlistListResponse, WaitlistResponse
)
from ...infrastructure.di.container import get_container


router = APIRouter(prefix="/waitlist", tags=["waitlist"])


def get_join_waitlist_use_case() -> JoinWaitlistUseCase:
    """Get join waitlist use case"""
    container = get_container()
    return JoinWaitlistUseCase(container.waitlist_repository())



def get_list_waitlist_use_case() -> ListWaitlistUseCase:
    """Get list waitlist use case"""
    container = get_container()
    return ListWaitlistUseCase(container.waitlist_repository())


def get_check_waitlist_status_use_case() -> CheckWaitlistStatusUseCase:
    """Get check waitlist status use case"""
    container = get_container()
    return CheckWaitlistStatusUseCase(container.waitlist_repository())


@router.post("/join", 
            response_model=WaitlistJoinResponse,
            summary="Join Waitlist",
            description="Join the EmailAI waitlist to get early access.")
async def join_waitlist(
    request: JoinWaitlistRequest,
    use_case: JoinWaitlistUseCase = Depends(get_join_waitlist_use_case)
) -> WaitlistJoinResponse:
    """Join the waitlist"""
    try:
        print(f"🔄 Waitlist join request for: {request.email}")
        
        # Convert request to DTO
        dto = CreateWaitlistDTO(
            email=request.email,
            name=request.name,
            use_case=request.use_case,
            referral_source=request.referral_source
        )
        
        # Execute use case
        waitlist_entry = await use_case.execute(dto)
        
        # Get total count
        list_use_case = get_list_waitlist_use_case()
        all_entries = await list_use_case.execute(page_size=10000)
        
        # Create response
        entry_response = WaitlistResponse(
            id=waitlist_entry.id,
            email=waitlist_entry.email,
            name=waitlist_entry.name,
            use_case=waitlist_entry.use_case,
            referral_source=waitlist_entry.referral_source,
            created_at=waitlist_entry.created_at,
            updated_at=waitlist_entry.updated_at,
            is_notified=waitlist_entry.is_notified
        )
        
        response = WaitlistJoinResponse(
            success=True,
            message="Successfully joined the waitlist! We'll notify you when early access is available.",
            entry=entry_response,
            total_entries=all_entries.total_count
        )
        
        print(f"✅ Successfully joined waitlist: {request.email}")
        return response
        
    except Exception as e:
        print(f"❌ Failed to join waitlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join waitlist: {str(e)}"
        )



@router.get("/check/{email}",
           response_model=WaitlistResponse,
           summary="Check Waitlist Status",
           description="Check the status of an email in the waitlist.")
async def check_waitlist_status(
    email: str,
    use_case: CheckWaitlistStatusUseCase = Depends(get_check_waitlist_status_use_case)
) -> WaitlistResponse:
    """Check waitlist status for an email"""
    try:
        print(f"🔄 Checking waitlist status for: {email}")
        
        waitlist_entry = await use_case.execute(email)
        
        response = WaitlistResponse(
            id=waitlist_entry.id,
            email=waitlist_entry.email,
            name=waitlist_entry.name,
            use_case=waitlist_entry.use_case,
            referral_source=waitlist_entry.referral_source,
            created_at=waitlist_entry.created_at,
            updated_at=waitlist_entry.updated_at,
            is_notified=waitlist_entry.is_notified
        )
        
        print(f"✅ Waitlist status retrieved for: {email}")
        return response
        
    except Exception as e:
        print(f"❌ Failed to check waitlist status: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found in waitlist"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check waitlist status: {str(e)}"
            )


@router.get("/",
           response_model=WaitlistListResponse,
           summary="List Waitlist Entries",
           description="List waitlist entries with pagination (admin only).")
async def list_waitlist_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    use_case: ListWaitlistUseCase = Depends(get_list_waitlist_use_case)
) -> WaitlistListResponse:
    """List waitlist entries (admin endpoint)"""
    try:
        print(f"🔄 Listing waitlist entries - page: {page}, size: {page_size}")
        
        result = await use_case.execute(page=page, page_size=page_size)
        
        # Convert entries to response format
        entries_with_position = []
        for i, entry in enumerate(result.entries):
            entry_response = WaitlistResponse(
                id=entry.id,
                email=entry.email,
                name=entry.name,
                use_case=entry.use_case,
                referral_source=entry.referral_source,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
                is_notified=entry.is_notified,
                position=((page - 1) * page_size) + i + 1
            )
            entries_with_position.append(entry_response)
        
        response = WaitlistListResponse(
            entries=entries_with_position,
            total_count=result.total_count,
            page=result.page,
            page_size=result.page_size,
            has_next=(page * page_size) < result.total_count,
            has_prev=page > 1
        )
        
        print(f"✅ Listed {len(result.entries)} waitlist entries")
        return response
        
    except Exception as e:
        print(f"❌ Failed to list waitlist entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list waitlist entries: {str(e)}"
        )