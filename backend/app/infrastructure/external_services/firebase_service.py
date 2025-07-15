"""
Firebase Service

Clean implementation of Firebase service with proper dependency management.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
import os

from ..config.settings import Settings


class FirebaseService:
    """Firebase service implementation with clean architecture principles"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._db: Optional[firestore.Client] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize Firebase Admin SDK and Firestore client"""
        if self._initialized:
            return
            
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Initialize Firebase Admin SDK
                cred_path = self.settings.firebase_credentials_path
                
                # Check if credentials file exists
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")
                
                cred = credentials.Certificate(cred_path)
                
                # Initialize with project ID if provided
                app_config = {}
                if self.settings.firebase_project_id:
                    app_config["projectId"] = self.settings.firebase_project_id
                
                firebase_admin.initialize_app(cred, app_config)
                print("✅ Firebase Admin SDK initialized successfully")
            
            # Initialize Firestore client
            self._db = firestore.client()
            self._initialized = True
            print("✅ Firestore client initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            raise e
    
    def get_firestore_client(self) -> firestore.Client:
        """Get Firestore database client"""
        if not self._initialized or self._db is None:
            self.initialize()
        return self._db
    
    def close(self) -> None:
        """Clean up Firebase resources"""
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
            self._initialized = False
            self._db = None
            print("🛑 Firebase resources cleaned up")
    
    def is_initialized(self) -> bool:
        """Check if Firebase service is initialized"""
        return self._initialized 