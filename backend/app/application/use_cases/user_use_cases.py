"""
User Use Cases

Business use cases for user operations.
"""

from typing import Optional

from ...domain.entities.user import User, UserRole
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.user_repository import UserRepository
from ...domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError

from ..dto.user_dto import UserDTO, CreateUserDTO, UpdateUserDTO


class UserUseCaseBase:
    """Base class for user use cases"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def _entity_to_dto(self, user: User) -> UserDTO:
        """Convert user entity to DTO"""
        return UserDTO(
            id=user.id,
            email=str(user.email),
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def _dto_to_entity(self, dto: CreateUserDTO) -> User:
        """Convert create DTO to user entity"""
        email = EmailAddress.create(dto.email)
        role = UserRole(dto.role)
        
        return User(
            email=email,
            name=dto.name,
            role=role
        )


class CreateUserUseCase(UserUseCaseBase):
    """Use case for creating users"""
    
    async def execute(self, dto: CreateUserDTO) -> UserDTO:
        """Create a new user"""
        # Check if user already exists
        email = EmailAddress.create(dto.email)
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            raise DomainValidationError(f"User with email {dto.email} already exists")
        
        user = self._dto_to_entity(dto)
        saved_user = await self.user_repository.save(user)
        return self._entity_to_dto(saved_user)


class GetUserUseCase(UserUseCaseBase):
    """Use case for getting users"""
    
    async def execute(self, user_id: str) -> UserDTO:
        """Get user by ID"""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return self._entity_to_dto(user)
    
    async def execute_by_email(self, email: str) -> UserDTO:
        """Get user by email"""
        email_address = EmailAddress.create(email)
        user = await self.user_repository.find_by_email(email_address)
        if not user:
            raise EntityNotFoundError("User", email)
        return self._entity_to_dto(user)


class UpdateUserUseCase(UserUseCaseBase):
    """Use case for updating users"""
    
    async def execute(self, user_id: str, dto: UpdateUserDTO) -> UserDTO:
        """Update user information"""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        
        # Update user properties
        if dto.name is not None:
            user.update_name(dto.name)
        
        if dto.role is not None:
            new_role = UserRole(dto.role)
            user.change_role(new_role)
        
        if dto.is_active is not None:
            if dto.is_active:
                user.activate()
            else:
                user.deactivate()
        
        updated_user = await self.user_repository.update(user)
        return self._entity_to_dto(updated_user)


class DeleteUserUseCase(UserUseCaseBase):
    """Use case for deleting users"""
    
    async def execute(self, user_id: str) -> bool:
        """Delete user by ID"""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        
        return await self.user_repository.delete(user_id)


class AuthenticateUserUseCase(UserUseCaseBase):
    """Use case for user authentication"""
    
    async def execute(self, email: str) -> UserDTO:
        """Authenticate user by email"""
        email_address = EmailAddress.create(email)
        user = await self.user_repository.find_by_email(email_address)
        
        if not user:
            raise EntityNotFoundError("User", email)
        
        if not user.is_active:
            raise DomainValidationError("User account is deactivated")
        
        # Update last login
        user.update_last_login()
        await self.user_repository.update(user)
        
        return self._entity_to_dto(user) 