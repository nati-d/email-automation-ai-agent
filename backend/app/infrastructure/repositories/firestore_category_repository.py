"""
Firestore Category Repository Implementation

Concrete implementation of category repository using Firestore.
"""

from typing import List, Optional
from firebase_admin import firestore

from ...domain.entities.category import Category
from ...domain.repositories.category_repository import CategoryRepository


class FirestoreCategoryRepository(CategoryRepository):
    """Firestore implementation of category repository"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "categories"
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] Initialized with collection: {self.collection_name}")
    
    def _entity_to_doc(self, category: Category) -> dict:
        """Convert category entity to Firestore document"""
        doc_data = {
            "user_id": category.user_id,
            "name": category.name,
            "description": category.description,
            "color": category.color,
            "is_active": category.is_active,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] _entity_to_doc: {doc_data}")
        return doc_data
    
    def _doc_to_entity(self, doc_id: str, doc_data: dict) -> Category:
        """Convert Firestore document to category entity"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] _doc_to_entity - doc_id: {doc_id}, doc_data: {doc_data}")
        
        # Create the category entity first
        category = Category(
            user_id=doc_data.get("user_id", ""),
            name=doc_data.get("name", ""),
            description=doc_data.get("description"),
            color=doc_data.get("color"),
            is_active=doc_data.get("is_active", True)
        )
        
        # Set the ID and timestamps from the document
        category.id = doc_id
        category.created_at = doc_data.get("created_at")
        category.updated_at = doc_data.get("updated_at")
        
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] Created category entity: {category}")
        return category
    
    async def save(self, category: Category) -> Category:
        """Save a category"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] save called for category: {category.id}")
        doc_data = self._entity_to_doc(category)
        
        if category.id:
            # Check if the document exists first
            doc_ref = self.db.collection(self.collection_name).document(category.id)
            doc = doc_ref.get()  # Synchronous
            
            if doc.exists:
                # Update existing category
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Updating existing category: {category.id}")
                doc_ref.update(doc_data)  # Synchronous
                return category
            else:
                # Document doesn't exist, create it with the provided ID
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Document doesn't exist, creating with ID: {category.id}")
                doc_ref.set(doc_data)  # Synchronous
                return category
        else:
            # Create new category with auto-generated ID
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Creating new category with auto-generated ID")
            doc_ref = self.db.collection(self.collection_name).document()
            category.id = doc_ref.id
            doc_data = self._entity_to_doc(category)
            doc_ref.set(doc_data)  # Synchronous
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Category created with ID: {category.id}")
            return category
    
    async def find_by_id(self, category_id: str) -> Optional[Category]:
        """Find category by ID"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_by_id called for: {category_id}")
        try:
            doc_ref = self.db.collection(self.collection_name).document(category_id)
            doc = doc_ref.get()  # Synchronous
            
            if doc.exists:
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Found category: {doc.id}")
                return self._doc_to_entity(doc.id, doc.to_dict())
            else:
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Category not found: {category_id}")
                return None
        except Exception as e:
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_by_id error: {e}")
            raise
    
    async def find_by_user_id(self, user_id: str) -> List[Category]:
        """Find categories by user ID"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_by_user_id called for user: {user_id}")
        try:
            query = self.db.collection(self.collection_name).where("user_id", "==", user_id)
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Executing query for user_id: {user_id}")
            
            # Get the query results
            query_snapshot = query.get()  # Synchronous
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Query snapshot type: {type(query_snapshot)}")
            
            categories = []
            for doc in query_snapshot:
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Processing doc: {doc.id}")
                categories.append(self._doc_to_entity(doc.id, doc.to_dict()))
            
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Found {len(categories)} categories for user: {user_id}")
            return categories
        except Exception as e:
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_by_user_id error: {e}")
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Full traceback: {traceback.format_exc()}")
            raise
    
    async def find_active_by_user_id(self, user_id: str) -> List[Category]:
        """Find active categories by user ID"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_active_by_user_id called for user: {user_id}")
        try:
            query = (
                self.db.collection(self.collection_name)
                .where("user_id", "==", user_id)
                .where("is_active", "==", True)
            )
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Executing active query for user_id: {user_id}")
            
            # Get the query results
            query_snapshot = query.get()  # Synchronous
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Active query snapshot type: {type(query_snapshot)}")
            
            categories = []
            for doc in query_snapshot:
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Processing active doc: {doc.id}")
                categories.append(self._doc_to_entity(doc.id, doc.to_dict()))
            
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Found {len(categories)} active categories for user: {user_id}")
            return categories
        except Exception as e:
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_active_by_user_id error: {e}")
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Full traceback: {traceback.format_exc()}")
            raise
    
    async def find_by_name_and_user(self, name: str, user_id: str) -> Optional[Category]:
        """Find category by name and user ID"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_by_name_and_user called for name: {name}, user: {user_id}")
        try:
            query = (
                self.db.collection(self.collection_name)
                .where("user_id", "==", user_id)
                .where("name", "==", name)
            )
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Executing name query for name: {name}, user_id: {user_id}")
            
            # Get the query results
            query_snapshot = query.get()  # Synchronous
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Name query snapshot type: {type(query_snapshot)}")
            
            if query_snapshot:
                doc = query_snapshot[0]
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] Found category by name: {doc.id}")
                return self._doc_to_entity(doc.id, doc.to_dict())
            else:
                print(f"🔧 DEBUG: [FirestoreCategoryRepository] No category found for name: {name}, user: {user_id}")
                return None
        except Exception as e:
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] find_by_name_and_user error: {e}")
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Full traceback: {traceback.format_exc()}")
            raise
    
    async def update(self, category: Category) -> Category:
        """Update a category"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] update called for category: {category.id}")
        return await self.save(category)
    
    async def delete(self, category_id: str) -> bool:
        """Delete a category"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] delete called for category: {category_id}")
        try:
            doc_ref = self.db.collection(self.collection_name).document(category_id)
            doc_ref.delete()  # Synchronous
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Category deleted: {category_id}")
            return True
        except Exception as e:
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] delete error: {e}")
            raise
    
    async def exists_by_name_and_user(self, name: str, user_id: str) -> bool:
        """Check if category exists by name and user ID"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] exists_by_name_and_user called for name: {name}, user: {user_id}")
        category = await self.find_by_name_and_user(name, user_id)
        exists = category is not None
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] Category exists: {exists}")
        return exists
    
    async def count_by_user_id(self, user_id: str) -> int:
        """Count categories by user ID"""
        print(f"🔧 DEBUG: [FirestoreCategoryRepository] count_by_user_id called for user: {user_id}")
        try:
            query = self.db.collection(self.collection_name).where("user_id", "==", user_id)
            query_snapshot = query.get()  # Synchronous
            count = len(query_snapshot)
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] Count for user {user_id}: {count}")
            return count
        except Exception as e:
            print(f"🔧 DEBUG: [FirestoreCategoryRepository] count_by_user_id error: {e}")
            raise 