"""
Firestore Waitlist Repository

Concrete implementation of waitlist repository using Firestore.
"""

from typing import List, Optional
from datetime import datetime
from google.cloud import firestore

from ...domain.entities.waitlist import WaitlistEntry
from ...domain.repositories.waitlist_repository import WaitlistRepository


class FirestoreWaitlistRepository(WaitlistRepository):
    """Firestore implementation of waitlist repository"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "waitlist"
    
    def _entity_to_dict(self, waitlist_entry: WaitlistEntry) -> dict:
        """Convert waitlist entry entity to Firestore document"""
        return {
            "email": waitlist_entry.email,
            "name": waitlist_entry.name,
            "use_case": waitlist_entry.use_case,
            "referral_source": waitlist_entry.referral_source,
            "created_at": waitlist_entry.created_at,
            "updated_at": waitlist_entry.updated_at,
            "is_notified": waitlist_entry.is_notified
        }
    
    def _dict_to_entity(self, doc_data: dict, doc_id: str) -> WaitlistEntry:
        """Convert Firestore document to waitlist entry entity"""
        return WaitlistEntry(
            id=doc_id,
            email=doc_data.get("email", ""),
            name=doc_data.get("name"),
            use_case=doc_data.get("use_case"),
            referral_source=doc_data.get("referral_source"),
            created_at=doc_data.get("created_at", datetime.utcnow()),
            updated_at=doc_data.get("updated_at", datetime.utcnow()),
            is_notified=doc_data.get("is_notified", False)
        )
    
    async def save(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        """Save a waitlist entry"""
        try:
            print(f"🔄 Saving waitlist entry for email: {waitlist_entry.email}")
            
            doc_data = self._entity_to_dict(waitlist_entry)
            
            # Use email as document ID for easy lookup and prevent duplicates
            doc_id = waitlist_entry.email.replace(".", "_").replace("@", "_at_")
            doc_ref = self.db.collection(self.collection_name).document(doc_id)
            
            # Check if document already exists to prevent duplicates
            existing_doc = doc_ref.get()
            if existing_doc.exists:
                print(f"⚠️ Email already exists in waitlist: {waitlist_entry.email}")
                raise Exception("Email already registered in waitlist")
            
            doc_ref.set(doc_data)
            
            waitlist_entry.id = doc_id
            print(f"✅ Waitlist entry saved with ID: {doc_id}")
            
            return waitlist_entry
            
        except Exception as e:
            print(f"❌ Failed to save waitlist entry: {str(e)}")
            raise Exception(f"Failed to save waitlist entry: {str(e)}")
    
    async def find_by_email(self, email: str) -> Optional[WaitlistEntry]:
        """Find waitlist entry by email"""
        try:
            doc_id = email.lower().replace(".", "_").replace("@", "_at_")
            doc_ref = self.db.collection(self.collection_name).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return self._dict_to_entity(doc.to_dict(), doc.id)
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to find waitlist entry by email: {str(e)}")
            return None
    
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[WaitlistEntry]:
        """Find all waitlist entries with pagination"""
        try:
            query = (self.db.collection(self.collection_name)
                    .order_by("created_at", direction=firestore.Query.DESCENDING)
                    .limit(limit)
                    .offset(offset))
            
            docs = query.stream()
            
            waitlist_entries = []
            for doc in docs:
                waitlist_entry = self._dict_to_entity(doc.to_dict(), doc.id)
                waitlist_entries.append(waitlist_entry)
            
            return waitlist_entries
            
        except Exception as e:
            print(f"❌ Failed to find waitlist entries: {str(e)}")
            return []
    
    async def count_total(self) -> int:
        """Count total waitlist entries"""
        try:
            docs = self.db.collection(self.collection_name).stream()
            return len(list(docs))
            
        except Exception as e:
            print(f"❌ Failed to count waitlist entries: {str(e)}")
            return 0
    

    
    async def update(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        """Update a waitlist entry"""
        try:
            if not waitlist_entry.id:
                raise Exception("Waitlist entry ID is required for update")
            
            waitlist_entry.updated_at = datetime.utcnow()
            doc_data = self._entity_to_dict(waitlist_entry)
            
            doc_ref = self.db.collection(self.collection_name).document(waitlist_entry.id)
            doc_ref.update(doc_data)
            
            print(f"✅ Waitlist entry updated: {waitlist_entry.id}")
            return waitlist_entry
            
        except Exception as e:
            print(f"❌ Failed to update waitlist entry: {str(e)}")
            raise Exception(f"Failed to update waitlist entry: {str(e)}")
    
    async def delete_by_email(self, email: str) -> bool:
        """Delete waitlist entry by email"""
        try:
            doc_id = email.lower().replace(".", "_").replace("@", "_at_")
            doc_ref = self.db.collection(self.collection_name).document(doc_id)
            
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.delete()
                print(f"✅ Waitlist entry deleted: {email}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to delete waitlist entry: {str(e)}")
            return False