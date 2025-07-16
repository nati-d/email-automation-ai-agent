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
            # AI Summarization fields
            summary=email.summary,
            main_concept=email.main_concept,
            sentiment=email.sentiment,
            key_topics=email.key_topics,
            summarized_at=email.summarized_at,
            # Email categorization
            email_type=email.email_type.value,
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
        gmail_service,
        llm_service: Optional[LLMService] = None
    ):
        super().__init__(email_repository)
        self.gmail_service = gmail_service
        self.llm_service = llm_service
    
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
            
            # Store emails in repository and summarize them
            stored_count = 0
            failed_count = 0
            summarized_count = 0
            
            for i, email in enumerate(emails):
                try:
                    print(f"🔄 Storing email {i+1}/{len(emails)}: {email.subject[:50]}...")
                    saved_email = await self.email_repository.save(email)
                    print(f"✅ Stored email with ID: {saved_email.id}")
                    stored_count += 1
                    
                    # Process email with AI (summarization and categorization) if LLM service is available
                    if self.llm_service:
                        try:
                            print(f"🔄 Processing email {saved_email.id} with AI...")
                            print(f"🔧 DEBUG: LLM service type: {type(self.llm_service).__name__}")
                            print(f"🔧 DEBUG: Email subject: {saved_email.subject}")
                            print(f"🔧 DEBUG: Email body length: {len(saved_email.body)} chars")
                            print(f"🔧 DEBUG: Has HTML body: {saved_email.html_body is not None}")
                            
                            # Prepare content for AI processing
                            email_content = saved_email.body
                            if saved_email.html_body:
                                import re
                                print(f"🔧 DEBUG: HTML body length: {len(saved_email.html_body)} chars")
                                email_content = re.sub(r'<[^>]+>', '', saved_email.html_body)
                                print(f"🔧 DEBUG: Cleaned HTML content length: {len(email_content)} chars")
                            
                            # Get context information
                            sender = str(saved_email.sender)
                            recipient = str(saved_email.recipients[0]) if saved_email.recipients else ""
                            print(f"🔧 DEBUG: Sender: {sender}")
                            print(f"🔧 DEBUG: Recipient: {recipient}")
                            print(f"🔧 DEBUG: Content to process: {email_content[:200]}...")
                            
                            # Step 1: Categorize email
                            print(f"🔧 DEBUG: Calling LLM service.categorize_email...")
                            category = self.llm_service.categorize_email(
                                email_content=email_content,
                                email_subject=saved_email.subject,
                                sender=sender,
                                recipient=recipient
                            )
                            print(f"🔧 DEBUG: Email categorized as: {category}")
                            
                            # Set email type based on categorization
                            from ...domain.entities.email import EmailType
                            email_type = EmailType.TASKS if category == 'tasks' else EmailType.INBOX
                            saved_email.set_email_type(email_type)
                            print(f"🔧 DEBUG: Email type set to: {email_type.value}")
                            
                            # Step 2: Summarize email
                            print(f"🔧 DEBUG: Calling LLM service.summarize_email...")
                            summarization_result = self.llm_service.summarize_email(
                                email_content=email_content,
                                email_subject=saved_email.subject,
                                sender=sender,
                                recipient=recipient
                            )
                            print(f"🔧 DEBUG: LLM service returned: {summarization_result}")
                            
                            # Validate summarization result
                            if not summarization_result:
                                print(f"⚠️ LLM service returned None or empty result")
                                continue
                            
                            summary = summarization_result.get('summary', '')
                            main_concept = summarization_result.get('main_concept', '')
                            sentiment = summarization_result.get('sentiment', '')
                            key_topics = summarization_result.get('key_topics', [])
                            
                            print(f"🔧 DEBUG: Extracted summary: {summary[:100]}...")
                            print(f"🔧 DEBUG: Extracted main_concept: {main_concept}")
                            print(f"🔧 DEBUG: Extracted sentiment: {sentiment}")
                            print(f"🔧 DEBUG: Extracted key_topics: {key_topics}")
                            
                            # Set summarization data on email
                            print(f"🔧 DEBUG: Setting summarization on email...")
                            saved_email.set_summarization(
                                summary=summary,
                                main_concept=main_concept,
                                sentiment=sentiment,
                                key_topics=key_topics
                            )
                            print(f"🔧 DEBUG: Summarization set successfully")
                            
                            # Save updated email with both categorization and summarization
                            print(f"🔧 DEBUG: Saving email with AI processing...")
                            await self.email_repository.update(saved_email)
                            print(f"✅ Email processed successfully (Type: {category}, Summarized: Yes)")
                            summarized_count += 1
                            
                        except Exception as ai_error:
                            print(f"⚠️ Failed to process email {saved_email.id} with AI: {str(ai_error)}")
                            print(f"🔧 DEBUG: AI processing error type: {type(ai_error).__name__}")
                            import traceback
                            print(f"🔧 DEBUG: AI processing error traceback: {traceback.format_exc()}")
                            # Continue with next email even if AI processing fails
                            continue
                    else:
                        print(f"⚠️ LLM service is None - skipping AI processing for email {saved_email.id}")
                    
                except Exception as e:
                    print(f"⚠️ Failed to store email {email.subject}: {str(e)}")
                    print(f"⚠️ Storage error type: {type(e).__name__}")
                    failed_count += 1
                    continue
            
            print(f"✅ Email import complete:")
            print(f"   - Successfully imported: {stored_count}")
            print(f"   - Failed to import: {failed_count}")
            print(f"   - Summarized: {summarized_count}")
            print(f"   - Total processed: {len(emails)}")
            
            return {
                "success": True,
                "emails_imported": stored_count,
                "emails_failed": failed_count,
                "emails_summarized": summarized_count,
                "total_found": len(emails),
                "message": f"Successfully imported {stored_count} emails (summarized: {summarized_count})"
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