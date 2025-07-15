"""
User Controller

Clean architecture implementation of user API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

# Application layer
from ...application.dto.user_dto import UserDTO, CreateUserDTO, UpdateUserDTO
from ...application.use_cases.user_use_cases import (
    CreateUserUseCase, GetUserUseCase, UpdateUserUseCase,
    DeleteUserUseCase, AuthenticateUserUseCase
)

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container

# Presentation models
from ..models.user_models import CreateUserRequest, UpdateUserRequest, UserResponse


router = APIRouter()


# Dependency injection
def get_create_user_use_case(container: Container = Depends(get_container)) -> CreateUserUseCase:
    return container.create_user_use_case()


def get_get_user_use_case(container: Container = Depends(get_container)) -> GetUserUseCase:
    return container.get_user_use_case()


def get_update_user_use_case(container: Container = Depends(get_container)) -> UpdateUserUseCase:
    return container.update_user_use_case()


def get_delete_user_use_case(container: Container = Depends(get_container)) -> DeleteUserUseCase:
    return container.delete_user_use_case()


def get_authenticate_user_use_case(container: Container = Depends(get_container)) -> AuthenticateUserUseCase:
    return container.authenticate_user_use_case()


def _dto_to_response(dto: UserDTO) -> UserResponse:
    """Convert DTO to response model"""
    return UserResponse(
        id=dto.id,
        email=dto.email,
        name=dto.name,
        role=dto.role,
        is_active=dto.is_active,
        last_login=dto.last_login,
        created_at=dto.created_at,
        updated_at=dto.updated_at
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


@router.post("/users",
            response_model=UserResponse,
            summary="Create User",
            description="Create a new user.")
async def create_user(
    request: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
) -> UserResponse:
    """Create a new user"""
    try:
        # Convert request to DTO
        dto = CreateUserDTO(
            email=request.email,
            name=request.name,
            role=request.role
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


@router.get("/users/{user_id}",
           response_model=UserResponse,
           summary="Get User",
           description="Get user by ID.")
async def get_user(
    user_id: str,
    use_case: GetUserUseCase = Depends(get_get_user_use_case)
) -> UserResponse:
    """Get user by ID"""
    try:
        dto = await use_case.execute(user_id)
        return _dto_to_response(dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.put("/users/{user_id}",
           response_model=UserResponse,
           summary="Update User",
           description="Update user information.")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case)
) -> UserResponse:
    """Update user information"""
    try:
        # Convert request to DTO
        dto = UpdateUserDTO(
            name=request.name,
            role=request.role,
            is_active=request.is_active
        )
        
        # Execute use case
        result_dto = await use_case.execute(user_id, dto)
        
        # Convert to response
        return _dto_to_response(result_dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.delete("/users/{user_id}",
              summary="Delete User",
              description="Delete user by ID.")
async def delete_user(
    user_id: str,
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case)
) -> dict:
    """Delete user by ID"""
    try:
        success = await use_case.execute(user_id)
        return {"message": "User deleted successfully", "user_id": user_id}
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        ) 