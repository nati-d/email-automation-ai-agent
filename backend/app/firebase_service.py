import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings
import os
from typing import Optional


class FirebaseService:
    _instance: Optional['FirebaseService'] = None
    _db: Optional[firestore.Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
    
    def initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK and Firestore client"""
        if self.initialized:
            return
            
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Initialize Firebase Admin SDK
                cred_path = settings.firebase_credentials_path
                
                # Check if credentials file exists
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK initialized successfully")
            
            # Initialize Firestore client
            self._db = firestore.client()
            self.initialized = True
            print("✅ Firestore client initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            raise e
    
    def get_db(self) -> firestore.Client:
        """Get Firestore database client"""
        if not self.initialized or self._db is None:
            self.initialize_firebase()
        return self._db
    
    def close(self) -> None:
        """Clean up Firebase resources"""
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
            self.initialized = False
            self._db = None
            print("🛑 Firebase resources cleaned up")


# Create global instance
firebase_service = FirebaseService()


def get_firestore_db() -> firestore.Client:
    """Dependency function to get Firestore database client"""
    return firebase_service.get_db() 