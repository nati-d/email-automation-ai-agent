"""
Waitlist Use Cases

Business logic for waitlist operations.
"""

from typing import List
from datetime import datetime, timedelta
from collections import Counter

from ...domain.entities.waitlist import WaitlistEntry
from ...domain.repositories.waitlist_repository import WaitlistRepository
from ...domain.exceptions.domain_exceptions import DomainValidationError
from ..dto.waitlist_dto import CreateWaitlistDTO, WaitlistDTO, WaitlistListDTO


class WaitlistUseCaseBase:
    """Base class for waitlist use cases"""
    
    def __init__(self, waitlist_repository: WaitlistRepository):
        self.waitlist_repository = waitlist_repository
    
    def _entity_to_dto(self, waitlist_entry: WaitlistEntry) -> WaitlistDTO:
        """Convert waitlist entry entity to DTO"""
        return WaitlistDTO(
            id=waitlist_entry.id,
            email=waitlist_entry.email,
            name=waitlist_entry.name,
            use_case=waitlist_entry.use_case,
            referral_source=waitlist_entry.referral_source,
            created_at=waitlist_entry.created_at,
            updated_at=waitlist_entry.updated_at,
            is_notified=waitlist_entry.is_notified
        )


class JoinWaitlistUseCase(WaitlistUseCaseBase):
    """Use case for joining the waitlist"""
    
    async def execute(self, dto: CreateWaitlistDTO) -> WaitlistDTO:
        """Join the waitlist"""
        try:
            print(f"🔄 JoinWaitlistUseCase.execute called for email: {dto.email}")
            
            # Create new waitlist entry
            waitlist_entry = WaitlistEntry.create(
                email=dto.email,
                name=dto.name,
                use_case=dto.use_case,
                referral_source=dto.referral_source
            )
            
            # Save to repository (will check for duplicates)
            saved_entry = await self.waitlist_repository.save(waitlist_entry)
            
            print(f"✅ Successfully joined waitlist: {dto.email}")
            return self._entity_to_dto(saved_entry)
            
        except Exception as e:
            print(f"❌ Failed to join waitlist: {str(e)}")
            raise Exception(f"Failed to join waitlist: {str(e)}")



class ListWaitlistUseCase(WaitlistUseCaseBase):
    """Use case for listing waitlist entries"""
    
    async def execute(self, page: int = 1, page_size: int = 50) -> WaitlistListDTO:
        """List waitlist entries"""
        try:
            print(f"🔄 ListWaitlistUseCase.execute called - page: {page}, size: {page_size}")
            
            offset = (page - 1) * page_size
            entries = await self.waitlist_repository.find_all(limit=page_size, offset=offset)
            total_count = await self.waitlist_repository.count_total()
            
            entry_dtos = [self._entity_to_dto(entry) for entry in entries]
            
            result = WaitlistListDTO(
                entries=entry_dtos,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
            
            print(f"✅ Listed {len(entries)} waitlist entries")
            return result
            
        except Exception as e:
            print(f"❌ Failed to list waitlist entries: {str(e)}")
            raise Exception(f"Failed to list waitlist entries: {str(e)}")


class CheckWaitlistStatusUseCase(WaitlistUseCaseBase):
    """Use case for checking waitlist status"""
    
    async def execute(self, email: str) -> WaitlistDTO:
        """Check waitlist status for an email"""
        try:
            print(f"🔄 CheckWaitlistStatusUseCase.execute called for: {email}")
            
            entry = await self.waitlist_repository.find_by_email(email)
            if not entry:
                raise Exception("Email not found in waitlist")
            
            print(f"✅ Found waitlist entry for: {email}")
            return self._entity_to_dto(entry)
            
        except Exception as e:
            print(f"❌ Failed to check waitlist status: {str(e)}")
            raise Exception(f"Failed to check waitlist status: {str(e)}")