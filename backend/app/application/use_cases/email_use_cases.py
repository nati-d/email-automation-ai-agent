"""
Email Use Cases

Business use cases for email operations.
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.email import Email, EmailStatus
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.email_repository import EmailRepository
from ...domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError

from ..dto.email_dto import EmailDTO, CreateEmailDTO, UpdateEmailDTO, EmailListDTO


class EmailUseCaseBase:
    """Base class for email use cases"""
    
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
    
    def _entity_to_dto(self, email: Email) -> EmailDTO:
        """Convert email entity to DTO"""
        return EmailDTO(
            id=email.id,
            sender=str(email.sender),
            recipients=[str(recipient) for recipient in email.recipients],
            subject=email.subject,
            body=email.body,
            html_body=email.html_body,
            status=email.status.value,
            scheduled_at=email.scheduled_at,
            sent_at=email.sent_at,
            created_at=email.created_at,
            updated_at=email.updated_at,
            metadata=email.metadata
        )
    
    def _dto_to_entity(self, dto: CreateEmailDTO) -> Email:
        """Convert create DTO to email entity"""
        sender = EmailAddress.create(dto.sender)
        recipients = [EmailAddress.create(recipient) for recipient in dto.recipients]
        
        email = Email(
            sender=sender,
            recipients=recipients,
            subject=dto.subject,
            body=dto.body,
            html_body=dto.html_body,
            metadata=dto.metadata
        )
        
        if dto.scheduled_at:
            email.schedule(dto.scheduled_at)
        
        return email


class CreateEmailUseCase(EmailUseCaseBase):
    """Use case for creating emails"""
    
    async def execute(self, dto: CreateEmailDTO) -> EmailDTO:
        """Create a new email"""
        email = self._dto_to_entity(dto)
        saved_email = await self.email_repository.save(email)
        return self._entity_to_dto(saved_email)


class GetEmailUseCase(EmailUseCaseBase):
    """Use case for getting emails"""
    
    async def execute(self, email_id: str) -> EmailDTO:
        """Get email by ID"""
        email = await self.email_repository.find_by_id(email_id)
        if not email:
            raise EntityNotFoundError("Email", email_id)
        return self._entity_to_dto(email)


class UpdateEmailUseCase(EmailUseCaseBase):
    """Use case for updating emails"""
    
    async def execute(self, email_id: str, dto: UpdateEmailDTO) -> EmailDTO:
        """Update email content"""
        email = await self.email_repository.find_by_id(email_id)
        if not email:
            raise EntityNotFoundError("Email", email_id)
        
        # Update email content
        email.update_content(
            subject=dto.subject,
            body=dto.body,
            html_body=dto.html_body
        )
        
        # Update scheduling if provided
        if dto.scheduled_at:
            email.schedule(dto.scheduled_at)
        
        # Update metadata
        if dto.metadata:
            email.metadata.update(dto.metadata)
            email.mark_updated()
        
        updated_email = await self.email_repository.update(email)
        return self._entity_to_dto(updated_email)


class DeleteEmailUseCase(EmailUseCaseBase):
    """Use case for deleting emails"""
    
    async def execute(self, email_id: str) -> bool:
        """Delete email by ID"""
        email = await self.email_repository.find_by_id(email_id)
        if not email:
            raise EntityNotFoundError("Email", email_id)
        
        return await self.email_repository.delete(email_id)


class SendEmailUseCase(EmailUseCaseBase):
    """Use case for sending emails"""
    
    async def execute(self, email_id: str) -> EmailDTO:
        """Send email by ID"""
        email = await self.email_repository.find_by_id(email_id)
        if not email:
            raise EntityNotFoundError("Email", email_id)
        
        # Mark as sending
        email.mark_as_sending()
        await self.email_repository.update(email)
        
        try:
            # TODO: Integrate with actual email service
            # For now, just mark as sent
            email.mark_as_sent()
            updated_email = await self.email_repository.update(email)
            return self._entity_to_dto(updated_email)
        
        except Exception as e:
            # Mark as failed
            email.mark_as_failed(str(e))
            await self.email_repository.update(email)
            raise


class ScheduleEmailUseCase(EmailUseCaseBase):
    """Use case for scheduling emails"""
    
    async def execute(self, email_id: str, scheduled_at: datetime) -> EmailDTO:
        """Schedule email for future sending"""
        email = await self.email_repository.find_by_id(email_id)
        if not email:
            raise EntityNotFoundError("Email", email_id)
        
        email.schedule(scheduled_at)
        updated_email = await self.email_repository.update(email)
        return self._entity_to_dto(updated_email)


class ListEmailsUseCase(EmailUseCaseBase):
    """Use case for listing emails"""
    
    async def execute(
        self, 
        sender: Optional[str] = None, 
        status: Optional[str] = None,
        limit: int = 50
    ) -> EmailListDTO:
        """List emails with optional filters"""
        emails = []
        
        if sender:
            sender_email = EmailAddress.create(sender)
            emails = await self.email_repository.find_by_sender(sender_email, limit)
        elif status:
            email_status = EmailStatus(status)
            emails = await self.email_repository.find_by_status(email_status, limit)
        else:
            emails = await self.email_repository.find_recent_emails(limit)
        
        email_dtos = [self._entity_to_dto(email) for email in emails]
        
        return EmailListDTO(
            emails=email_dtos,
            total_count=len(email_dtos),
            page=1,
            page_size=limit
        ) 