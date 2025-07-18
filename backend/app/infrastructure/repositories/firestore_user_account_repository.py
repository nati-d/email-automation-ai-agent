"""
Firestore User Account Repository

Firestore implementation of user account repository.
"""

from typing import List, Optional
from google.cloud import firestore

from ...domain.entities.user_account import UserAccount
from ...domain.repositories.user_account_repository import UserAccountRepository
from ...domain.value_objects.email_address import EmailAddress
from ...domain.exceptions.domain_exceptions import EntityNotFoundError


class FirestoreUserAccountRepository(UserAccountRepository):
    """Firestore implementation of user account repository"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "user_accounts"
    
    async def save(self, user_account: UserAccount) -> UserAccount:
        """Save a user account"""
        doc_data = self._entity_to_doc(user_account)
        
        if user_account.id:
            # Update existing
            doc_ref = self.db.collection(self.collection_name).document(user_account.id)
            doc_ref.update(doc_data)
            return user_account
        else:
            # Create new
            doc_ref = self.db.collection(self.collection_name).document()
            doc_data["id"] = doc_ref.id
            doc_ref.set(doc_data)
            
            # Return updated entity with ID
            user_account.id = doc_ref.id
            return user_account
    
    async def find_by_id(self, user_account_id: str) -> Optional[UserAccount]:
        """Find user account by ID"""
        doc_ref = self.db.collection(self.collection_name).document(user_account_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return self._doc_to_entity(doc.id, doc.to_dict())
        return None
    
    async def find_by_user_id(self, user_id: str) -> List[UserAccount]:
        """Find all accounts for a user"""
        query = self.db.collection(self.collection_name)\
            .where("user_id", "==", user_id)\
            .order_by("created_at", direction=firestore.Query.DESCENDING)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def find_by_user_and_email(self, user_id: str, email: EmailAddress) -> Optional[UserAccount]:
        """Find a specific account for a user by email"""
        query = self.db.collection(self.collection_name)\
            .where("user_id", "==", user_id)\
            .where("email", "==", str(email))
        
        docs = query.stream()
        for doc in docs:
            return self._doc_to_entity(doc.id, doc.to_dict())
        return None
    
    async def find_primary_account(self, user_id: str) -> Optional[UserAccount]:
        """Find the primary account for a user"""
        query = self.db.collection(self.collection_name)\
            .where("user_id", "==", user_id)\
            .where("is_primary", "==", True)\
            .limit(1)
        
        docs = query.stream()
        for doc in docs:
            return self._doc_to_entity(doc.id, doc.to_dict())
        return None
    
    async def find_active_accounts(self, user_id: str) -> List[UserAccount]:
        """Find all active accounts for a user"""
        query = self.db.collection(self.collection_name)\
            .where("user_id", "==", user_id)\
            .where("is_active", "==", True)\
            .order_by("created_at", direction=firestore.Query.DESCENDING)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def update(self, user_account: UserAccount) -> UserAccount:
        """Update a user account"""
        if not user_account.id:
            raise ValueError("Cannot update user account without ID")
        
        doc_data = self._entity_to_doc(user_account)
        doc_ref = self.db.collection(self.collection_name).document(user_account.id)
        doc_ref.update(doc_data)
        
        return user_account
    
    async def delete(self, user_account_id: str) -> bool:
        """Delete a user account"""
        doc_ref = self.db.collection(self.collection_name).document(user_account_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.delete()
            return True
        return False
    
    async def deactivate_account(self, user_id: str, email: EmailAddress) -> bool:
        """Deactivate a specific account for a user"""
        user_account = await self.find_by_user_and_email(user_id, email)
        if user_account:
            user_account.deactivate()
            await self.update(user_account)
            return True
        return False
    
    async def activate_account(self, user_id: str, email: EmailAddress) -> bool:
        """Activate a specific account for a user"""
        user_account = await self.find_by_user_and_email(user_id, email)
        if user_account:
            user_account.activate()
            await self.update(user_account)
            return True
        return False
    
    def _entity_to_doc(self, user_account: UserAccount) -> dict:
        """Convert entity to Firestore document"""
        return {
            "user_id": user_account.user_id,
            "email": str(user_account.email),
            "account_name": user_account.account_name,
            "provider": user_account.provider,
            "is_primary": user_account.is_primary,
            "is_active": user_account.is_active,
            "last_sync": user_account.last_sync,
            "sync_enabled": user_account.sync_enabled,
            "created_at": user_account.created_at,
            "updated_at": user_account.updated_at
        }
    
    def _doc_to_entity(self, doc_id: str, doc_data: dict) -> UserAccount:
        """Convert Firestore document to entity"""
        return UserAccount(
            id=doc_id,
            user_id=doc_data["user_id"],
            email=EmailAddress.create(doc_data["email"]),
            account_name=doc_data.get("account_name"),
            provider=doc_data.get("provider", "google"),
            is_primary=doc_data.get("is_primary", False),
            is_active=doc_data.get("is_active", True),
            last_sync=doc_data.get("last_sync"),
            sync_enabled=doc_data.get("sync_enabled", True),
            created_at=doc_data.get("created_at"),
            updated_at=doc_data.get("updated_at")
        ) 