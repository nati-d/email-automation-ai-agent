"""
Draft Use Cases

Business logic for email draft operations.
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.email import Email, EmailStatus
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.email_repository import EmailRepository


class CreateDraftUseCase:
    """Use case for creating email drafts - local storage only"""
    
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
    
    async def execute(
        self, 
        sender_email: str,
        recipients: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> Email:
        """Create a new email draft (local storage only)"""
        try:
            print(f"🔄 CreateDraftUseCase.execute called:")
            print(f"   - sender_email: {sender_email}")
            print(f"   - recipients: {recipients}")
            print(f"   - subject: {subject}")
            
            # Create email entity
            sender = EmailAddress.create(sender_email)
            recipient_addresses = [EmailAddress.create(email) for email in recipients]
            
            email = Email(
                sender=sender,
                recipients=recipient_addresses,
                subject=subject,
                body=body,
                html_body=html_body,
                status=EmailStatus.DRAFT,
                account_owner=sender_email,
                email_holder=sender_email,
                metadata={'local_draft': True}
            )
            
            # Save draft locally only
            saved_email = await self.email_repository.save_draft(email)
            print(f"✅ Draft saved locally with ID: {saved_email.id}")
            
            return saved_email
            
        except Exception as e:
            print(f"❌ Failed to create draft: {str(e)}")
            raise Exception(f"Failed to create draft: {str(e)}")


class UpdateDraftUseCase:
    """Use case for updating email drafts - local storage only"""
    
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
    
    async def execute(
        self, 
        draft_id: str,
        sender_email: str,
        subject: Optional[str] = None, 
        body: Optional[str] = None, 
        html_body: Optional[str] = None,
        recipients: Optional[List[str]] = None
    ) -> Email:
        """Update an existing email draft (local storage only)"""
        try:
            print(f"🔄 UpdateDraftUseCase.execute called:")
            print(f"   - draft_id: {draft_id}")
            print(f"   - sender_email: {sender_email}")
            
            # Find existing draft
            existing_draft = await self.email_repository.find_draft_by_id(draft_id)
            if not existing_draft:
                raise Exception(f"Draft not found: {draft_id}")
            
            # Verify ownership
            if existing_draft.account_owner != sender_email:
                raise Exception("You don't have permission to update this draft")
            
            # Update draft content
            if subject is not None:
                existing_draft.subject = subject
            if body is not None:
                existing_draft.body = body
            if html_body is not None:
                existing_draft.html_body = html_body
            if recipients is not None:
                existing_draft.recipients = [EmailAddress.create(email) for email in recipients]
            
            existing_draft.mark_updated()
            
            # Save updated draft locally only
            updated_draft = await self.email_repository.update_draft(existing_draft)
            print(f"✅ Draft updated locally")
            
            return updated_draft
            
        except Exception as e:
            print(f"❌ Failed to update draft: {str(e)}")
            raise Exception(f"Failed to update draft: {str(e)}")


class DeleteDraftUseCase:
    """Use case for deleting email drafts - local storage only"""
    
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
    
    async def execute(self, draft_id: str, sender_email: str) -> bool:
        """Delete an email draft (local storage only)"""
        try:
            print(f"🔄 DeleteDraftUseCase.execute called:")
            print(f"   - draft_id: {draft_id}")
            print(f"   - sender_email: {sender_email}")
            
            # Find existing draft
            existing_draft = await self.email_repository.find_draft_by_id(draft_id)
            if not existing_draft:
                print(f"⚠️ Draft not found: {draft_id}")
                return False
            
            # Verify ownership
            if existing_draft.account_owner != sender_email:
                raise Exception("You don't have permission to delete this draft")
            
            # Delete draft locally only
            success = await self.email_repository.delete_draft(draft_id, sender_email)
            if success:
                print(f"✅ Draft deleted locally")
            else:
                print(f"⚠️ Failed to delete draft locally")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to delete draft: {str(e)}")
            raise Exception(f"Failed to delete draft: {str(e)}")


class ListDraftsUseCase:
    """Use case for listing email drafts"""
    
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
    
    async def execute(self, sender_email: str, limit: int = 50) -> List[Email]:
        """List email drafts for a user"""
        try:
            print(f"🔄 ListDraftsUseCase.execute called:")
            print(f"   - sender_email: {sender_email}")
            print(f"   - limit: {limit}")
            
            drafts = await self.email_repository.find_draft_emails(sender_email, limit)
            print(f"✅ Found {len(drafts)} drafts")
            
            return drafts
            
        except Exception as e:
            print(f"❌ Failed to list drafts: {str(e)}")
            raise Exception(f"Failed to list drafts: {str(e)}")


# Note: SendDraftUseCase removed - we'll use the existing sendEmail functionality
# Note: SyncDraftsWithGmailUseCase removed - drafts are local only