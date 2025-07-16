"""
Email Use Cases

Business use cases for email operations.
"""

from typing import List, Optional, Dict, Any
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


class SendNewEmailUseCase(EmailUseCaseBase):
    """Use case for creating and sending a new email"""
    
    def __init__(self, email_repository: EmailRepository, email_service=None):
        super().__init__(email_repository)
        self.email_service = email_service
    
    async def execute(self, sender_email: str, recipients: List[str], subject: str, body: str, html_body: Optional[str] = None) -> EmailDTO:
        """Create and send a new email"""
        
        # Create email entity
        sender = EmailAddress.create(sender_email)
        recipient_addresses = [EmailAddress.create(recipient) for recipient in recipients]
        
        email = Email(
            sender=sender,
            recipients=recipient_addresses,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        # Save email first
        saved_email = await self.email_repository.save(email)
        
        # Mark as sending
        saved_email.mark_as_sending()
        await self.email_repository.update(saved_email)
        
        try:
            print(f"🔍 DEBUG: SendNewEmailUseCase - About to send email")
            print(f"   📧 Email details:")
            print(f"      sender: {sender_email}")
            print(f"      recipients: {recipients}")
            print(f"      subject: {subject}")
            print(f"      body length: {len(body)} chars")
            print(f"      html_body: {'provided' if html_body else 'None'}")
            
            # Send email using email service if available
            if self.email_service:
                print(f"🔍 DEBUG: Email service is available, calling send_email()")
                print(f"   🔧 Email service type: {type(self.email_service).__name__}")
                
                try:
                    success = await self.email_service.send_email(
                        sender=sender_email,
                        recipients=recipients,
                        subject=subject,
                        body=body,
                        html_body=html_body
                    )
                    print(f"🔍 DEBUG: Email service send_email() returned: {success}")
                    
                    if not success:
                        print(f"🔍 DEBUG: Email service returned False, marking as failed")
                        # Email service failed to send
                        saved_email.mark_as_failed("Email service failed to send email")
                        await self.email_repository.update(saved_email)
                        raise DomainValidationError("Failed to send email: Email service returned failure")
                    else:
                        print(f"🔍 DEBUG: Email service returned True, proceeding to mark as sent")
                        
                except Exception as email_service_error:
                    print(f"🔍 DEBUG: Email service threw exception: {email_service_error}")
                    print(f"🔍 DEBUG: Exception type: {type(email_service_error).__name__}")
                    import traceback
                    print(f"🔍 DEBUG: Email service exception traceback: {traceback.format_exc()}")
                    raise email_service_error
                    
            else:
                print(f"🔍 DEBUG: No email service available")
                # No email service available
                saved_email.mark_as_failed("No email service configured")
                await self.email_repository.update(saved_email)
                raise DomainValidationError("Failed to send email: No email service configured")
            
            # Mark as sent
            saved_email.mark_as_sent()
            updated_email = await self.email_repository.update(saved_email)
            return self._entity_to_dto(updated_email)
        
        except DomainValidationError:
            # Re-raise domain validation errors
            raise
        except Exception as e:
            # Mark as failed
            saved_email.mark_as_failed(str(e))
            await self.email_repository.update(saved_email)
            raise DomainValidationError(f"Failed to send email: {str(e)}")


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
        recipient: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> EmailListDTO:
        """List emails with optional filters"""
        emails = []
        
        if recipient:
            recipient_email = EmailAddress.create(recipient)
            emails = await self.email_repository.find_by_recipient(recipient_email, limit)
        elif sender:
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


class FetchInitialEmailsUseCase(EmailUseCaseBase):
    """Use case for fetching initial emails for new users"""
    
    def __init__(
        self, 
        email_repository: EmailRepository,
        gmail_service
    ):
        super().__init__(email_repository)
        self.gmail_service = gmail_service
    
    async def execute(self, oauth_token, user_email: str, limit: int = 50) -> Dict[str, Any]:
        """Fetch initial emails from Gmail and store them"""
        try:
            print(f"🔄 FetchInitialEmailsUseCase.execute called:")
            print(f"   - user_email: {user_email}")
            print(f"   - limit: {limit}")
            print(f"   - oauth_token type: {type(oauth_token).__name__}")
            print(f"   - gmail_service type: {type(self.gmail_service).__name__}")
            print(f"   - email_repository type: {type(self.email_repository).__name__}")
            
            # Fetch emails from Gmail
            print("🔄 Calling gmail_service.fetch_recent_emails...")
            emails = await self.gmail_service.fetch_recent_emails(oauth_token, user_email, limit)
            print(f"📧 Gmail service returned {len(emails) if emails else 0} emails")
            
            if not emails:
                print("⚠️ No emails found to import")
                return {
                    "success": True,
                    "emails_imported": 0,
                    "message": "No emails found to import"
                }
            
            # Store emails in repository
            stored_count = 0
            failed_count = 0
            for i, email in enumerate(emails):
                try:
                    print(f"🔄 Storing email {i+1}/{len(emails)}: {email.subject[:50]}...")
                    saved_email = await self.email_repository.save(email)
                    print(f"✅ Stored email with ID: {saved_email.id}")
                    stored_count += 1
                except Exception as e:
                    print(f"⚠️ Failed to store email {email.subject}: {str(e)}")
                    print(f"⚠️ Storage error type: {type(e).__name__}")
                    failed_count += 1
                    continue
            
            print(f"✅ Email import complete:")
            print(f"   - Successfully imported: {stored_count}")
            print(f"   - Failed to import: {failed_count}")
            print(f"   - Total processed: {len(emails)}")
            
            return {
                "success": True,
                "emails_imported": stored_count,
                "emails_failed": failed_count,
                "total_found": len(emails),
                "message": f"Successfully imported {stored_count} emails"
            }
            
        except Exception as e:
            print(f"❌ Failed to fetch initial emails: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "emails_imported": 0,
                "error": str(e),
                "message": "Failed to import emails"
            } 