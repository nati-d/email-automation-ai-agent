"""
Category Controller

Clean architecture implementation of category API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer

# Application layer
from ...application.dto.category_dto import CategoryDTO, CreateCategoryDTO, UpdateCategoryDTO, CategoryListDTO
from ...application.dto.user_dto import UserDTO
from ...application.use_cases.category_use_cases import (
    CreateCategoryUseCase, GetCategoryUseCase, UpdateCategoryUseCase,
    DeleteCategoryUseCase, ListCategoriesUseCase, RecategorizeEmailsUseCase
)

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container

# Presentation models
from ..models.category_models import (
    CreateCategoryRequest, UpdateCategoryRequest, CategoryResponse,
    CategoryListResponse, RecategorizeEmailsResponse
)

# Middleware
from ..middleware.auth_middleware import get_current_user

# Security scheme
security = HTTPBearer()

router = APIRouter()


# Dependency injection
def get_create_category_use_case(container: Container = Depends(get_container)) -> CreateCategoryUseCase:
    print(f"🔧 DEBUG: [CategoryController] get_create_category_use_case called")
    use_case = container.create_category_use_case()
    print(f"🔧 DEBUG: [CategoryController] CreateCategoryUseCase type: {type(use_case).__name__}")
    return use_case


def get_get_category_use_case(container: Container = Depends(get_container)) -> GetCategoryUseCase:
    return container.get_category_use_case()


def get_update_category_use_case(container: Container = Depends(get_container)) -> UpdateCategoryUseCase:
    return container.update_category_use_case()


def get_delete_category_use_case(container: Container = Depends(get_container)) -> DeleteCategoryUseCase:
    return container.delete_category_use_case()


def get_list_categories_use_case(container: Container = Depends(get_container)) -> ListCategoriesUseCase:
    print(f"🔧 DEBUG: [CategoryController] get_list_categories_use_case called")
    use_case = container.list_categories_use_case()
    print(f"🔧 DEBUG: [CategoryController] Use case type: {type(use_case).__name__}")
    return use_case


def get_recategorize_emails_use_case(container: Container = Depends(get_container)) -> RecategorizeEmailsUseCase:
    return container.recategorize_emails_use_case()


# Helper functions
def _dto_to_response(dto: CategoryDTO) -> CategoryResponse:
    """Convert DTO to response model"""
    return CategoryResponse(
        id=dto.id,
        user_id=dto.user_id,
        name=dto.name,
        description=dto.description,
        color=dto.color,
        is_active=dto.is_active,
        created_at=dto.created_at,
        updated_at=dto.updated_at
    )


def _list_dto_to_response(dto: CategoryListDTO) -> CategoryListResponse:
    """Convert list DTO to response model"""
    categories = [_dto_to_response(cat_dto) for cat_dto in dto.categories]
    return CategoryListResponse(
        categories=categories,
        total_count=dto.total_count
    )


def _handle_domain_exception(e: DomainException) -> HTTPException:
    """Handle domain exceptions and convert to HTTP exceptions"""
    if isinstance(e, EntityNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": str(e)}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "VALIDATION_ERROR", "message": str(e)}
        )


# API Endpoints
@router.post("/categories",
            response_model=CategoryResponse,
            summary="Create Category",
            description="Create a new email category for the authenticated user.",
            dependencies=[Depends(security)])
async def create_category(
    request: CreateCategoryRequest,
    current_user: UserDTO = Depends(get_current_user),
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case)
) -> CategoryResponse:
    """Create a new category"""
    print(f"🔧 DEBUG: [CategoryController] create_category called")
    print(f"🔧 DEBUG: [CategoryController] request: {request}")
    print(f"🔧 DEBUG: [CategoryController] current_user: {current_user}")
    
    try:
        # Convert request to DTO
        print(f"🔧 DEBUG: [CategoryController] Creating CreateCategoryDTO")
        dto = CreateCategoryDTO(
            user_id=current_user.id,
            name=request.name,
            description=request.description if request.description else None,
            color=request.color if request.color else None
        )
        print(f"🔧 DEBUG: [CategoryController] DTO created: {dto}")
        
        # Execute use case
        print(f"🔧 DEBUG: [CategoryController] Executing use case")
        result_dto = await use_case.execute(dto)
        print(f"🔧 DEBUG: [CategoryController] Use case returned: {result_dto}")
        
        # Convert to response
        print(f"🔧 DEBUG: [CategoryController] Converting to response")
        response = _dto_to_response(result_dto)
        print(f"🔧 DEBUG: [CategoryController] Response created: {response}")
        
        return response
        
    except DomainException as e:
        print(f"🔧 DEBUG: [CategoryController] DomainException: {e}")
        raise _handle_domain_exception(e)
    except Exception as e:
        print(f"🔧 DEBUG: [CategoryController] Exception: {e}")
        print(f"🔧 DEBUG: [CategoryController] Exception type: {type(e).__name__}")
        import traceback
        print(f"🔧 DEBUG: [CategoryController] Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/categories/{category_id}",
           response_model=CategoryResponse,
           summary="Get Category",
           description="Get a specific category by ID.",
           dependencies=[Depends(security)])
async def get_category(
    category_id: str,
    current_user: UserDTO = Depends(get_current_user),
    use_case: GetCategoryUseCase = Depends(get_get_category_use_case)
) -> CategoryResponse:
    """Get a category by ID"""
    try:
        result_dto = await use_case.execute(category_id)
        
        # Verify the category belongs to the user
        if result_dto.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "FORBIDDEN", "message": "Access denied to this category"}
            )
        
        return _dto_to_response(result_dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.put("/categories/{category_id}",
           response_model=CategoryResponse,
           summary="Update Category",
           description="Update a category's information.",
           dependencies=[Depends(security)])
async def update_category(
    category_id: str,
    request: UpdateCategoryRequest,
    current_user: UserDTO = Depends(get_current_user),
    use_case: UpdateCategoryUseCase = Depends(get_update_category_use_case)
) -> CategoryResponse:
    """Update category information"""
    try:
        # First get the category to verify ownership
        get_use_case = GetCategoryUseCase(use_case.category_repository)
        existing_dto = await get_use_case.execute(category_id)
        
        if existing_dto.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "FORBIDDEN", "message": "Access denied to this category"}
            )
        
        # Convert request to DTO
        dto = UpdateCategoryDTO(
            name=request.name,
            description=request.description,
            color=request.color,
            is_active=request.is_active
        )
        
        # Execute use case
        result_dto = await use_case.execute(category_id, dto)
        
        # Convert to response
        return _dto_to_response(result_dto)
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.delete("/categories/{category_id}",
              summary="Delete Category",
              description="Delete a category and re-categorize affected emails.",
              dependencies=[Depends(security)])
async def delete_category(
    category_id: str,
    current_user: UserDTO = Depends(get_current_user),
    use_case: DeleteCategoryUseCase = Depends(get_delete_category_use_case)
) -> dict:
    """Delete a category"""
    try:
        # First get the category to verify ownership
        get_use_case = GetCategoryUseCase(use_case.category_repository)
        existing_dto = await get_use_case.execute(category_id)
        
        if existing_dto.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "FORBIDDEN", "message": "Access denied to this category"}
            )
        
        # Execute use case
        await use_case.execute(category_id)
        
        return {
            "message": "Category deleted successfully",
            "category_id": category_id
        }
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/categories",
           response_model=CategoryListResponse,
           summary="List Categories",
           description="Get all categories for the authenticated user.",
           dependencies=[Depends(security)])
async def list_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    current_user: UserDTO = Depends(get_current_user),
    use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case)
) -> CategoryListResponse:
    print("[DEBUG] list_categories endpoint called")
    print(f"[DEBUG] include_inactive: {include_inactive}")
    print(f"[DEBUG] current_user: {current_user}")
    if hasattr(current_user, 'id'):
        print(f"[DEBUG] current_user.id: {current_user.id}")
    else:
        print("[DEBUG] current_user has no 'id' attribute")
    if hasattr(current_user, 'email'):
        print(f"[DEBUG] current_user.email: {current_user.email}")
    else:
        print("[DEBUG] current_user has no 'email' attribute")
    print(f"[DEBUG] use_case: {use_case}")
    try:
        print("[DEBUG] Calling use_case.execute...")
        result_dto = await use_case.execute(current_user.id, include_inactive)
        print(f"[DEBUG] use_case.execute returned: {result_dto}")
        response = _list_dto_to_response(result_dto)
        print(f"[DEBUG] Converted result to response: {response}")
        return response
    except DomainException as e:
        print(f"[DEBUG] DomainException: {e}")
        raise _handle_domain_exception(e)
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        print(f"[DEBUG] Exception type: {type(e).__name__}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/categories/recategorize-emails",
            response_model=RecategorizeEmailsResponse,
            summary="Re-categorize Emails",
            description="Re-categorize all inbox emails based on current categories.",
            dependencies=[Depends(security)])
async def recategorize_emails(
    current_user: UserDTO = Depends(get_current_user),
    use_case: RecategorizeEmailsUseCase = Depends(get_recategorize_emails_use_case)
) -> RecategorizeEmailsResponse:
    """Re-categorize emails based on current categories"""
    try:
        recategorized_count = await use_case.execute(current_user.id)
        
        return RecategorizeEmailsResponse(
            recategorized_count=recategorized_count,
            message=f"Successfully re-categorized {recategorized_count} emails"
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        ) 