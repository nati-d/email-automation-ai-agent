"""
User Account Controller

API endpoints for managing user accounts.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ...application.dto.user_dto import UserDTO
from ...application.dto.user_account_dto import CreateUserAccountDTO, UpdateUserAccountDTO
from ...application.use_cases.user_account_use_cases import (
    CreateUserAccountUseCase, GetUserAccountsUseCase, GetActiveUserAccountsUseCase,
    UpdateUserAccountUseCase, DeleteUserAccountUseCase, CheckAccountExistsUseCase,
    AddAccountIfNotExistsUseCase
)
from ..models.user_account_models import (
    UserAccountResponse, CreateUserAccountRequest, UpdateUserAccountRequest,
    UserAccountListResponse, UserAccountOperationResponse
)
from ..middleware.auth_middleware import get_current_user
from ...infrastructure.di.container import get_container


router = APIRouter(prefix="/user-accounts", tags=["User Accounts"])


def _dto_to_response(dto) -> dict:
    """Convert DTO to response dict"""
    return {
        "id": dto.id,
        "user_id": dto.user_id,
        "email": dto.email,
        "account_name": dto.account_name,
        "provider": dto.provider,
        "is_primary": dto.is_primary,
        "is_active": dto.is_active,
        "last_sync": dto.last_sync,
        "sync_enabled": dto.sync_enabled,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at
    }


@router.get("/", response_model=UserAccountListResponse)
async def get_my_accounts(
    current_user: UserDTO = Depends(get_current_user)
) -> UserAccountListResponse:
    """Get all accounts for the current user"""
    container = get_container()
    use_case = container.get_user_accounts_use_case()
    
    result = await use_case.execute(current_user.id)
    
    accounts = [UserAccountResponse(**{**account.__dict__}) for account in result.accounts]
    
    return UserAccountListResponse(
        accounts=accounts,
        total_count=result.total_count,
        page=result.page,
        page_size=result.page_size
    )


@router.get("/active", response_model=UserAccountListResponse)
async def get_my_active_accounts(
    current_user: UserDTO = Depends(get_current_user)
) -> UserAccountListResponse:
    """Get all active accounts for the current user"""
    container = get_container()
    use_case = container.get_active_user_accounts_use_case()
    
    result = await use_case.execute(current_user.id)
    
    accounts = [UserAccountResponse(**{**account.__dict__}) for account in result.accounts]
    
    return UserAccountListResponse(
        accounts=accounts,
        total_count=result.total_count,
        page=result.page,
        page_size=result.page_size
    )


@router.post("/", response_model=UserAccountResponse)
async def create_user_account(
    request: CreateUserAccountRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> UserAccountResponse:
    """Create a new account for the current user"""
    container = get_container()
    use_case = container.create_user_account_use_case()
    
    dto = CreateUserAccountDTO(
        user_id=current_user.id,
        email=request.email,
        account_name=request.account_name,
        provider=request.provider,
        is_primary=request.is_primary
    )
    
    result = await use_case.execute(dto)
    
    return UserAccountResponse(**{**result.__dict__})


@router.put("/{account_id}", response_model=UserAccountResponse)
async def update_user_account(
    account_id: str,
    request: UpdateUserAccountRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> UserAccountResponse:
    """Update a user account"""
    container = get_container()
    use_case = container.update_user_account_use_case()
    
    dto = UpdateUserAccountDTO(
        account_name=request.account_name,
        is_primary=request.is_primary,
        is_active=request.is_active,
        sync_enabled=request.sync_enabled
    )
    
    result = await use_case.execute(account_id, dto)
    
    return UserAccountResponse(**{**result.__dict__})


@router.delete("/{account_id}")
async def delete_user_account(
    account_id: str,
    current_user: UserDTO = Depends(get_current_user)
) -> dict:
    """Delete a user account"""
    container = get_container()
    use_case = container.delete_user_account_use_case()
    
    success = await use_case.execute(account_id)
    
    if success:
        return {"success": True, "message": "Account deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )


@router.get("/check/{email}")
async def check_account_exists(
    email: str,
    current_user: UserDTO = Depends(get_current_user)
) -> dict:
    """Check if an account exists for the current user"""
    container = get_container()
    use_case = container.check_account_exists_use_case()
    
    exists = await use_case.execute(current_user.id, email)
    
    return {
        "exists": exists,
        "email": email,
        "user_id": current_user.id
    }


@router.post("/add-if-not-exists", response_model=UserAccountOperationResponse)
async def add_account_if_not_exists(
    request: CreateUserAccountRequest,
    current_user: UserDTO = Depends(get_current_user)
) -> UserAccountOperationResponse:
    """Add an account if it doesn't already exist for the current user"""
    container = get_container()
    use_case = container.add_account_if_not_exists_use_case()
    
    result = await use_case.execute(
        user_id=current_user.id,
        email=request.email,
        account_name=request.account_name,
        is_primary=request.is_primary
    )
    
    account_response = None
    if result["account"]:
        account_response = UserAccountResponse(**{**result["account"].__dict__})
    
    return UserAccountOperationResponse(
        success=result["account_added"],
        message=result["message"],
        account=account_response
    ) 