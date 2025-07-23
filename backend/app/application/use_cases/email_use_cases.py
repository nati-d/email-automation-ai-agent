"""
Email Use Cases

Business use cases for email operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.entities.email import Email, EmailStatus
from ...domain.repositories.email_repository import EmailRepository
from ...domain.value_objects.email_address import EmailAddress
from ...domain.exceptions.domain_exceptions import (
    DomainValidationError, 
    EntityNotFoundError,
    DomainException
)
from ...application.dto.email_dto import EmailDTO, CreateEmailDTO, UpdateEmailDTO, EmailListDTO
from ...infrastructure.external_services.llm_service import LLMService
import inspect
from ...domain.entities.email import EmailType


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
            metadata=email.metadata,
            # Account ownership fields
            account_owner=email.account_owner,
            email_holder=email.email_holder,
            # AI Summarization fields
            summary=email.summary,
            main_concept=email.main_concept,
            sentiment=email.sentiment,
            key_topics=email.key_topics,
            summarized_at=email.summarized_at,
            # Email categorization
            email_type=email.email_type.value,
            category=email.category,
            categorized_at=email.categorized_at
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
            metadata=dto.metadata,
            # Account ownership fields
            account_owner=dto.account_owner,
            email_holder=dto.email_holder
        )
        
        if dto.scheduled_at:
            email.schedule(dto.scheduled_at)
        
        return email


class CreateEmailUseCase(EmailUseCaseBase):
    """Use case for creating emails"""
    
    async def execute(self, dto: CreateEmailDTO) -> EmailDTO:
        """Create a new email"""
        email = self._dto_to_entity(dto)
        
        # Set account ownership if not provided
        if not email.account_owner:
            email.account_owner = dto.sender
        if not email.email_holder:
            email.email_holder = dto.sender
        
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
            subject=dto.subject if dto.subject is not None else email.subject,
            body=dto.body if dto.body is not None else email.body,
            html_body=dto.html_body if dto.html_body is not None else email.html_body
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
            html_body=html_body,
            # Account ownership fields
            account_owner=sender_email,  # The sender is the account owner
            email_holder=sender_email    # The sender's email account holds this email
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
        account_owner: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> EmailListDTO:
        """List emails with optional filters"""
        emails = []
        
        if account_owner:
            # Filter by account owner (logged-in user)
            emails = await self.email_repository.find_by_account_owner(account_owner, limit)
        elif recipient:
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
        gmail_service,
        llm_service: Optional[LLMService] = None,
        category_repository=None
    ):
        super().__init__(email_repository)
        self.gmail_service = gmail_service
        self.llm_service = llm_service
        self.category_repository = category_repository
    
    async def execute(self, oauth_token, user_email: str, limit: int = 10, account_owner: Optional[str] = None) -> Dict[str, Any]:
        """Fetch initial emails from Gmail and store them"""
        try:
            print(f"🔄 FetchInitialEmailsUseCase.execute called:")
            print(f"   - user_email: {user_email}")
            print(f"   - limit: {limit}")
            print(f"   - account_owner: {account_owner}")
            print(f"   - oauth_token type: {type(oauth_token).__name__}")
            print(f"   - gmail_service type: {type(self.gmail_service).__name__}")
            print(f"   - email_repository type: {type(self.email_repository).__name__}")
            
            # Use account_owner if provided, otherwise use user_email
            actual_account_owner = account_owner or user_email
            print(f"   - actual_account_owner: {actual_account_owner}")
            
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
            
            # Store emails in database
            print("🔄 Storing emails in database...")
            stored_emails = []
            for email in emails:
                try:
                    # Set account ownership
                    email.account_owner = actual_account_owner
                    email.email_holder = user_email
                    # Categorize email as 'inbox' or 'tasks' using LLM if available
                    if self.llm_service is not None and hasattr(self.llm_service, 'categorize_email') and callable(self.llm_service.categorize_email):
                        try:
                            category_result = self.llm_service.categorize_email(
                                email_content=email.body,
                                email_subject=email.subject,
                                sender=str(email.sender),
                                recipient=str(email.recipients[0]) if email.recipients else ""
                            )
                            # categorize_email is synchronous, do not await
                            category = category_result
                            if isinstance(category, str) and category.strip().lower() == 'tasks':
                                email.set_email_type(EmailType.TASKS)
                            else:
                                email.set_email_type(EmailType.INBOX)
                        except Exception as cat_err:
                            print(f"⚠️ Failed to categorize email: {cat_err}")
                            email.set_email_type(EmailType.INBOX)
                    else:
                        email.set_email_type(EmailType.INBOX)
                    # Store email
                    stored_email = await self.email_repository.save(email)
                    stored_emails.append(stored_email)
                    print(f"✅ Stored email: {stored_email.subject[:50]}...")
                except Exception as e:
                    print(f"⚠️ Failed to store email {email.subject[:50]}: {str(e)}")
                    continue
            
            print(f"✅ Successfully stored {len(stored_emails)} emails")
            
            # Summarize emails if LLM service is available
            summarized_count = 0
            if self.llm_service and stored_emails:
                print("🔄 Summarizing emails with LLM...")
                summarized_count = await self._summarize_emails(stored_emails)
                print(f"✅ Summarized {summarized_count} emails")
            
            return {
                "success": True,
                "emails_imported": len(stored_emails),
                "emails_summarized": summarized_count,
                "message": f"Successfully imported {len(stored_emails)} emails"
            }
            
        except Exception as e:
            print(f"❌ FetchInitialEmailsUseCase failed: {str(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to import emails: {str(e)}"
            }
    
    async def _summarize_emails(self, emails: List[Email]) -> int:
        """Summarize a list of emails using LLM service"""
        summarized_count = 0
        
        for email in emails:
            try:
                # Skip if already summarized
                if email.summary:
                    continue
                
                # Summarize email
                summary_data = {}
                if self.llm_service is not None and hasattr(self.llm_service, 'summarize_email') and callable(self.llm_service.summarize_email):
                    maybe_coro = self.llm_service.summarize_email(
                        email_content=email.body,
                        email_subject=email.subject,
                        sender=str(email.sender),
                        recipient=str(email.recipients[0]) if email.recipients else ""
                    )
                    # summarize_email is synchronous, do not await
                    if maybe_coro is not None and not isinstance(maybe_coro, dict):
                        summary_data = maybe_coro
                    elif isinstance(maybe_coro, dict):
                        summary_data = maybe_coro
                if not isinstance(summary_data, dict):
                    summary_data = {}
                
                # Update email with summary data
                email.summary = summary_data.get('summary')
                email.main_concept = summary_data.get('main_concept')
                email.sentiment = summary_data.get('sentiment')
                email.key_topics = summary_data.get('key_topics', [])
                email.summarized_at = datetime.utcnow()
                
                # Save updated email
                await self.email_repository.save(email)
                summarized_count += 1
                
            except Exception as e:
                print(f"⚠️ Failed to summarize email {email.subject[:50]}: {str(e)}")
                continue
        
        return summarized_count


class FetchStarredEmailsUseCase(EmailUseCaseBase):
    """Use case for fetching starred emails from Gmail"""
    
    def __init__(
        self, 
        email_repository: EmailRepository,
        gmail_service,
        llm_service: Optional[LLMService] = None
    ):
        super().__init__(email_repository)
        self.gmail_service = gmail_service
        self.llm_service = llm_service
    
    async def execute(self, oauth_token, user_email: str, limit: int = 10, account_owner: Optional[str] = None) -> Dict[str, Any]:
        """Fetch starred emails from Gmail and store them"""
        try:
            print(f"🔄 FetchStarredEmailsUseCase.execute called:")
            print(f"   - user_email: {user_email}")
            print(f"   - limit: {limit}")
            print(f"   - account_owner: {account_owner}")
            
            # Use account_owner if provided, otherwise use user_email
            actual_account_owner = account_owner or user_email
            
            # Fetch starred emails from Gmail
            print("🔄 Calling gmail_service.fetch_starred_emails...")
            emails = await self.gmail_service.fetch_starred_emails(oauth_token, user_email, limit)
            print(f"⭐ Gmail service returned {len(emails) if emails else 0} starred emails")
            
            if not emails:
                print("⚠️ No starred emails found to import")
                return {
                    "success": True,
                    "emails_imported": 0,
                    "message": "No starred emails found to import"
                }
            
            # Store emails in database
            print("🔄 Storing starred emails in database...")
            stored_emails = []
            for email in emails:
                try:
                    # Set account ownership
                    email.account_owner = actual_account_owner
                    email.email_holder = user_email
                    
                    # Store email
                    stored_email = await self.email_repository.save(email)
                    stored_emails.append(stored_email)
                    print(f"✅ Stored starred email: {stored_email.subject[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Failed to store starred email {email.subject[:50]}: {str(e)}")
                    continue
            
            print(f"✅ Successfully stored {len(stored_emails)} starred emails")
            
            # Summarize emails if LLM service is available
            summarized_count = 0
            if self.llm_service and stored_emails:
                print("🔄 Summarizing starred emails with LLM...")
                summarized_count = await self._summarize_emails(stored_emails)
                print(f"✅ Summarized {summarized_count} starred emails")
            
            return {
                "success": True,
                "emails_imported": len(stored_emails),
                "emails_summarized": summarized_count,
                "message": f"Successfully imported {len(stored_emails)} starred emails"
            }
            
        except Exception as e:
            print(f"❌ FetchStarredEmailsUseCase failed: {str(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to import starred emails: {str(e)}"
            }
    
    async def _summarize_emails(self, emails: List[Email]) -> int:
        """Summarize a list of emails using LLM service"""
        summarized_count = 0
        
        for email in emails:
            try:
                # Skip if already summarized
                if email.summary:
                    continue
                
                # Summarize email
                summary_data = {}
                if self.llm_service is not None and hasattr(self.llm_service, 'summarize_email') and callable(self.llm_service.summarize_email):
                    maybe_coro = self.llm_service.summarize_email(
                        email_content=email.body,
                        email_subject=email.subject,
                        sender=str(email.sender),
                        recipient=str(email.recipients[0]) if email.recipients else ""
                    )
                    # summarize_email is synchronous, do not await
                    if maybe_coro is not None and not isinstance(maybe_coro, dict):
                        summary_data = maybe_coro
                    elif isinstance(maybe_coro, dict):
                        summary_data = maybe_coro
                if not isinstance(summary_data, dict):
                    summary_data = {}
                
                # Update email with summary data
                email.summary = summary_data.get('summary')
                email.main_concept = summary_data.get('main_concept')
                email.sentiment = summary_data.get('sentiment')
                email.key_topics = summary_data.get('key_topics', [])
                email.summarized_at = datetime.utcnow()
                
                # Save updated email
                await self.email_repository.save(email)
                summarized_count += 1
                
            except Exception as e:
                print(f"⚠️ Failed to summarize starred email {email.subject[:50]}: {str(e)}")
                continue
        
        return summarized_count


class SummarizeEmailUseCase(EmailUseCaseBase):
    """Use case for summarizing email content using AI"""
    
    def __init__(
        self, 
        email_repository: EmailRepository,
        llm_service: LLMService
    ):
        super().__init__(email_repository)
        self.llm_service = llm_service
    
    async def execute(self, email_id: str) -> Dict[str, Any]:
        """Summarize an email using AI"""
        try:
            print(f"🔄 SummarizeEmailUseCase.execute called for email: {email_id}")
            
            # Get email from repository
            email = await self.email_repository.find_by_id(email_id)
            if not email:
                raise EntityNotFoundError("Email", email_id)
            
            print(f"✅ Found email: {email.subject}")
            
            # Check if already summarized
            if email.has_summarization():
                print("ℹ️ Email already has summarization")
                return {
                    "success": True,
                    "already_summarized": True,
                    "summarization": email.get_summarization_data(),
                    "message": "Email already summarized"
                }
            
            # Prepare content for summarization
            email_content = email.body
            if email.html_body:
                # Use HTML body if available, but strip HTML tags for better analysis
                import re
                email_content = re.sub(r'<[^>]+>', '', email.html_body)
            
            # Get context information
            sender = str(email.sender)
            recipient = str(email.recipients[0]) if email.recipients else ""
            
            print(f"🔄 Calling LLM service to summarize email...")
            print(f"   - Content length: {len(email_content)} chars")
            print(f"   - Subject: {email.subject}")
            print(f"   - Sender: {sender}")
            print(f"   - Recipient: {recipient}")
            
            # Call LLM service for summarization
            summarization_result = self.llm_service.summarize_email(
                email_content=email_content,
                email_subject=email.subject,
                sender=sender,
                recipient=recipient
            )
            
            print(f"✅ LLM summarization completed:")
            print(f"   - Summary: {summarization_result.get('summary', 'N/A')[:100]}...")
            print(f"   - Main concept: {summarization_result.get('main_concept', 'N/A')}")
            print(f"   - Sentiment: {summarization_result.get('sentiment', 'N/A')}")
            print(f"   - Key topics: {summarization_result.get('key_topics', [])}")
            
            # Set summarization data on email
            email.set_summarization(
                summary=summarization_result.get('summary', ''),
                main_concept=summarization_result.get('main_concept', ''),
                sentiment=summarization_result.get('sentiment', ''),
                key_topics=summarization_result.get('key_topics', [])
            )
            
            # Save updated email
            print("🔄 Saving email with summarization...")
            await self.email_repository.update(email)
            print("✅ Email saved with summarization")
            
            return {
                "success": True,
                "already_summarized": False,
                "summarization": email.get_summarization_data(),
                "message": "Email summarized successfully"
            }
            
        except Exception as e:
            print(f"❌ Failed to summarize email: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to summarize email"
            }


class SummarizeMultipleEmailsUseCase(EmailUseCaseBase):
    """Use case for summarizing multiple emails in batch"""
    
    def __init__(
        self, 
        email_repository: EmailRepository,
        llm_service: LLMService
    ):
        super().__init__(email_repository)
        self.llm_service = llm_service
    
    async def execute(self, email_ids: List[str], max_concurrent: int = 5) -> Dict[str, Any]:
        """Summarize multiple emails using AI"""
        try:
            print(f"🔄 SummarizeMultipleEmailsUseCase.execute called for {len(email_ids)} emails")
            
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            # Create summarization tasks
            tasks = []
            for email_id in email_ids:
                task = self._summarize_single_email(email_id)
                tasks.append(task)
            
            # Execute tasks with concurrency limit
            results = []
            for i in range(0, len(tasks), max_concurrent):
                batch = tasks[i:i + max_concurrent]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results.extend(batch_results)
            
            # Process results
            successful = 0
            failed = 0
            already_summarized = 0
            errors = []
            
            for result in results:
                if isinstance(result, Exception):
                    failed += 1
                    errors.append(str(result))
                elif result.get('success'):
                    successful += 1
                    if result.get('already_summarized'):
                        already_summarized += 1
                else:
                    failed += 1
                    errors.append(result.get('error', 'Unknown error'))
            
            print(f"✅ Batch summarization completed:")
            print(f"   - Successful: {successful}")
            print(f"   - Already summarized: {already_summarized}")
            print(f"   - Failed: {failed}")
            
            return {
                "success": True,
                "total_processed": len(email_ids),
                "successful": successful,
                "already_summarized": already_summarized,
                "failed": failed,
                "errors": errors[:10],  # Limit error list
                "message": f"Processed {len(email_ids)} emails"
            }
            
        except Exception as e:
            print(f"❌ Failed to summarize multiple emails: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to summarize emails"
            }
    
    async def _summarize_single_email(self, email_id: str) -> Dict[str, Any]:
        """Helper method to summarize a single email"""
        try:
            # Get email from repository
            email = await self.email_repository.find_by_id(email_id)
            if not email:
                return {
                    "success": False,
                    "error": f"Email {email_id} not found"
                }
            
            # Check if already summarized
            if email.has_summarization():
                return {
                    "success": True,
                    "already_summarized": True,
                    "email_id": email_id
                }
            
            # Prepare content for summarization
            email_content = email.body
            if email.html_body:
                import re
                email_content = re.sub(r'<[^>]+>', '', email.html_body)
            
            # Get context information
            sender = str(email.sender)
            recipient = str(email.recipients[0]) if email.recipients else ""
            
            # Call LLM service for summarization
            summarization_result = self.llm_service.summarize_email(
                email_content=email_content,
                email_subject=email.subject,
                sender=sender,
                recipient=recipient
            )
            
            # Set summarization data on email
            email.set_summarization(
                summary=summarization_result.get('summary', ''),
                main_concept=summarization_result.get('main_concept', ''),
                sentiment=summarization_result.get('sentiment', ''),
                key_topics=summarization_result.get('key_topics', [])
            )
            
            # Save updated email
            await self.email_repository.update(email)
            
            return {
                "success": True,
                "already_summarized": False,
                "email_id": email_id,
                "summarization": email.get_summarization_data()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "email_id": email_id
            } 


class FetchSentEmailsUseCase(EmailUseCaseBase):
    """Use case for fetching sent emails from Gmail and updating user profile"""
    
    def __init__(
        self, 
        email_repository: EmailRepository,
        gmail_service,
        llm_service: Optional[LLMService] = None,
        category_repository=None,
        user_profile_repository=None  # NEW: Inject user_profile_repository
    ):
        super().__init__(email_repository)
        self.gmail_service = gmail_service
        self.llm_service = llm_service
        self.category_repository = category_repository
        self.user_profile_repository = user_profile_repository
    
    async def execute(self, oauth_token, user_email: str, limit: int = 10, account_owner: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch sent emails from Gmail, store, summarize, and update user profile"""
        try:
            print(f"🔄 FetchSentEmailsUseCase.execute called:")
            print(f"   - user_email: {user_email}")
            print(f"   - limit: {limit}")
            print(f"   - account_owner: {account_owner}")
            print(f"   - oauth_token type: {type(oauth_token).__name__}")
            print(f"   - gmail_service type: {type(self.gmail_service).__name__}")
            print(f"   - email_repository type: {type(self.email_repository).__name__}")
            
            # Use account_owner if provided, otherwise use user_email
            actual_account_owner = account_owner or user_email
            print(f"   - actual_account_owner: {actual_account_owner}")
            
            # Fetch sent emails from Gmail
            print("🔄 Calling gmail_service.fetch_sent_emails...")
            emails = await self.gmail_service.fetch_sent_emails(oauth_token, user_email, limit)
            print(f"📧 Gmail service returned {len(emails) if emails else 0} sent emails")
            
            if not emails:
                print("⚠️ No sent emails found to import")
                return {
                    "success": True,
                    "emails_imported": 0,
                    "message": "No sent emails found to import"
                }
            
            # Store emails in database
            print("🔄 Storing sent emails in database...")
            stored_emails = []
            for email in emails:
                try:
                    # Set account ownership
                    email.account_owner = actual_account_owner
                    email.email_holder = user_email
                    # Set email type to SENT
                    email.set_email_type(EmailType.SENT)
                    # Store email
                    stored_email = await self.email_repository.save(email)
                    stored_emails.append(stored_email)
                    print(f"✅ Stored sent email: {stored_email.subject[:50]}...")
                except Exception as e:
                    print(f"⚠️ Failed to store sent email {email.subject[:50]}: {str(e)}")
                    continue
            
            print(f"✅ Successfully stored {len(stored_emails)} sent emails")
            
            # Summarize emails if LLM service is available
            summarized_count = 0
            if self.llm_service and stored_emails:
                print("🔄 Summarizing sent emails with LLM...")
                summarized_count = await self._summarize_emails(stored_emails)
                print(f"✅ Summarized {summarized_count} sent emails")
            
            # --- NEW: Aggregate all sent emails and update user profile using LLM ---
            if self.llm_service and (account_owner or user_id):
                print("🔄 Aggregating ALL sent emails for user profile generation...")
                # Fetch all sent emails for the user
                all_sent_emails = await self.email_repository.find_by_sender(user_email, email_type=EmailType.SENT)
                email_samples = []
                for email in all_sent_emails:
                    email_samples.append({
                        "subject": email.subject,
                        "body": email.body,
                        "summary": email.summary,
                        "sentiment": email.sentiment,
                        "main_concept": email.main_concept,
                        "key_topics": email.key_topics
                    })
                # Build prompt for LLM
                prompt = (
                    "Analyze the following list of sent emails and generate a JSON user profile that describes "
                    "the user's typical tone, writing style, common structures, and favorite phrases. "
                    "Be concise and helpful. Respond ONLY with valid JSON in this format: "
                    '{"dominant_tone": "string", "tone_distribution": {"tone": count, ...}, "common_structures": ["structure1", ...], "favorite_phrases": ["phrase1", ...], "summary": "A helpful summary of the user\'s email style."}'
                    "\n\nEmails: " + str(email_samples)
                )
                try:
                    llm_response = self.llm_service.generate_content(
                        system_instruction="You are an expert at analyzing email writing style and generating user profiles.",
                        query=prompt,
                        response_type="text/plain"
                    )
                    import json
                    profile_data = json.loads(llm_response)
                    print(f"[DEBUG] LLM profile_data to be saved: {profile_data}")
                    # Store in user document
                    from app.infrastructure.di.container import get_container
                    container = get_container()
                    user_repo = container.user_repository()
                    user = await user_repo.find_by_email(user_email)
                    if user:
                        user.user_profile = profile_data
                        print(f"[DEBUG] About to update user {user.email} with profile: {user.user_profile}")
                        await user_repo.update(user)
                        print(f"[DEBUG] User profile (LLM, all sent emails) updated for user: {user.email}")
                except Exception as e:
                    print(f"⚠️ Failed to generate user profile with LLM: {e}")
                    # Fallback: set a test profile to verify update
                    from app.infrastructure.di.container import get_container
                    container = get_container()
                    user_repo = container.user_repository()
                    user = await user_repo.find_by_email(user_email)
                    if user:
                        user.user_profile = {"test": "value", "error": str(e)}
                        print(f"[DEBUG] About to update user {user.email} with fallback profile: {user.user_profile}")
                        await user_repo.update(user)
                        print(f"[DEBUG] Fallback user_profile set for user: {user.email}")
            # --- END NEW ---
            
            return {
                "success": True,
                "emails_imported": len(stored_emails),
                "emails_summarized": summarized_count,
                "message": f"Successfully imported {len(stored_emails)} sent emails"
            }
            
        except Exception as e:
            print(f"❌ FetchSentEmailsUseCase failed: {str(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to import sent emails: {str(e)}"
            } 

    async def _summarize_emails(self, emails: list) -> int:
        """Summarize a list of emails using LLM service"""
        summarized_count = 0
        from datetime import datetime
        for email in emails:
            try:
                # Skip if already summarized
                if email.summary:
                    continue
                summary_data = {}
                if self.llm_service is not None and hasattr(self.llm_service, 'summarize_email') and callable(self.llm_service.summarize_email):
                    maybe_coro = self.llm_service.summarize_email(
                        email_content=email.body,
                        email_subject=email.subject,
                        sender=str(email.sender),
                        recipient=str(email.recipients[0]) if email.recipients else ""
                    )
                    # summarize_email is synchronous, do not await
                    if maybe_coro is not None and not isinstance(maybe_coro, dict):
                        summary_data = maybe_coro
                    elif isinstance(maybe_coro, dict):
                        summary_data = maybe_coro
                if not isinstance(summary_data, dict):
                    summary_data = {}
                # Update email with summary data
                email.summary = summary_data.get('summary')
                email.main_concept = summary_data.get('main_concept')
                email.sentiment = summary_data.get('sentiment')
                email.key_topics = summary_data.get('key_topics', [])
                email.summarized_at = datetime.utcnow()
                # Save updated email
                await self.email_repository.save(email)
                summarized_count += 1
            except Exception as e:
                print(f"⚠️ Failed to summarize email {email.subject[:50]}: {str(e)}")
                continue
        return summarized_count 