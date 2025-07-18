"""
User Account Use Cases

Business logic for managing user accounts.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.entities.user_account import UserAccount
from ...domain.repositories.user_account_repository import UserAccountRepository
from ...domain.value_objects.email_address import EmailAddress
from ...domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError
from ..dto.user_account_dto import UserAccountDTO, CreateUserAccountDTO, UpdateUserAccountDTO, UserAccountListDTO


class UserAccountUseCaseBase:
    """Base class for user account use cases"""
    
    def __init__(self, user_account_repository: UserAccountRepository):
        self.user_account_repository = user_account_repository
    
    def _entity_to_dto(self, user_account: UserAccount) -> UserAccountDTO:
        """Convert entity to DTO"""
        return UserAccountDTO(
            id=user_account.id,
            user_id=user_account.user_id,
            email=str(user_account.email),
            account_name=user_account.account_name,
            provider=user_account.provider,
            is_primary=user_account.is_primary,
            is_active=user_account.is_active,
            last_sync=user_account.last_sync,
            sync_enabled=user_account.sync_enabled,
            created_at=user_account.created_at,
            updated_at=user_account.updated_at
        )
    
    def _dto_to_entity(self, dto: CreateUserAccountDTO) -> UserAccount:
        """Convert DTO to entity"""
        return UserAccount(
            user_id=dto.user_id,
            email=EmailAddress.create(dto.email),
            account_name=dto.account_name,
            provider=dto.provider,
            is_primary=dto.is_primary
        )


class CreateUserAccountUseCase(UserAccountUseCaseBase):
    """Use case for creating a user account"""
    
    async def execute(self, dto: CreateUserAccountDTO) -> UserAccountDTO:
        """Create a new user account"""
        # Check if account already exists for this user
        existing_account = await self.user_account_repository.find_by_user_and_email(
            dto.user_id, EmailAddress.create(dto.email)
        )
        
        if existing_account:
            raise DomainValidationError(f"Account {dto.email} already exists for this user")
        
        # Create user account entity
        user_account = self._dto_to_entity(dto)
        
        # Save to repository
        saved_account = await self.user_account_repository.save(user_account)
        
        return self._entity_to_dto(saved_account)


class GetUserAccountsUseCase(UserAccountUseCaseBase):
    """Use case for getting user accounts"""
    
    async def execute(self, user_id: str) -> UserAccountListDTO:
        """Get all accounts for a user"""
        accounts = await self.user_account_repository.find_by_user_id(user_id)
        
        account_dtos = [self._entity_to_dto(account) for account in accounts]
        
        return UserAccountListDTO(
            accounts=account_dtos,
            total_count=len(account_dtos),
            page=1,
            page_size=len(account_dtos)
        )


class GetActiveUserAccountsUseCase(UserAccountUseCaseBase):
    """Use case for getting active user accounts"""
    
    async def execute(self, user_id: str) -> UserAccountListDTO:
        """Get all active accounts for a user"""
        accounts = await self.user_account_repository.find_active_accounts(user_id)
        
        account_dtos = [self._entity_to_dto(account) for account in accounts]
        
        return UserAccountListDTO(
            accounts=account_dtos,
            total_count=len(account_dtos),
            page=1,
            page_size=len(account_dtos)
        )


class UpdateUserAccountUseCase(UserAccountUseCaseBase):
    """Use case for updating a user account"""
    
    async def execute(self, account_id: str, dto: UpdateUserAccountDTO) -> UserAccountDTO:
        """Update a user account"""
        # Find existing account
        user_account = await self.user_account_repository.find_by_id(account_id)
        if not user_account:
            raise EntityNotFoundError("User account", account_id)
        
        # Update fields
        if dto.account_name is not None:
            user_account.account_name = dto.account_name
        
        if dto.is_primary is not None:
            if dto.is_primary:
                user_account.set_as_primary()
            else:
                user_account.set_as_secondary()
        
        if dto.is_active is not None:
            if dto.is_active:
                user_account.activate()
            else:
                user_account.deactivate()
        
        if dto.sync_enabled is not None:
            if dto.sync_enabled:
                user_account.enable_sync()
            else:
                user_account.disable_sync()
        
        # Save updated account
        updated_account = await self.user_account_repository.update(user_account)
        
        return self._entity_to_dto(updated_account)


class DeleteUserAccountUseCase(UserAccountUseCaseBase):
    """Use case for deleting a user account"""
    
    async def execute(self, account_id: str) -> bool:
        """Delete a user account"""
        # Check if account exists
        user_account = await self.user_account_repository.find_by_id(account_id)
        if not user_account:
            raise EntityNotFoundError("User account", account_id)
        
        # Delete account
        return await self.user_account_repository.delete(account_id)


class CheckAccountExistsUseCase(UserAccountUseCaseBase):
    """Use case for checking if an account exists for a user"""
    
    async def execute(self, user_id: str, email: str) -> bool:
        """Check if an account exists for a user"""
        existing_account = await self.user_account_repository.find_by_user_and_email(
            user_id, EmailAddress.create(email)
        )
        return existing_account is not None


class AddAccountIfNotExistsUseCase(UserAccountUseCaseBase):
    """Use case for adding an account if it doesn't exist"""
    
    async def execute(self, user_id: str, email: str, account_name: Optional[str] = None, is_primary: bool = False) -> Dict[str, Any]:
        """Add an account if it doesn't already exist for the user"""
        # Check if account already exists
        existing_account = await self.user_account_repository.find_by_user_and_email(
            user_id, EmailAddress.create(email)
        )
        
        if existing_account:
            return {
                "account_added": False,
                "account_exists": True,
                "account": self._entity_to_dto(existing_account),
                "message": f"Account {email} already exists for this user"
            }
        
        # Create new account
        create_dto = CreateUserAccountDTO(
            user_id=user_id,
            email=email,
            account_name=account_name or f"Account {email}",
            is_primary=is_primary
        )
        
        new_account = await self.user_account_repository.save(self._dto_to_entity(create_dto))
        
        return {
            "account_added": True,
            "account_exists": False,
            "account": self._entity_to_dto(new_account),
            "message": f"Successfully added account {email}"
        } 