from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from app.firebase_service import get_firestore_db
from pydantic import BaseModel
from typing import Dict, Any, Optional
import datetime

router = APIRouter()


class Document(BaseModel):
    """Model for creating documents in Firestore"""
    collection: str
    document_id: Optional[str] = None
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "collection": "users",
                "document_id": "user123",
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "admin"
                }
            }
        }


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    id: str
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user123",
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "admin"
                },
                "created_at": "2024-01-15T10:30:00.000Z",
                "updated_at": "2024-01-15T10:30:00.000Z"
            }
        }


class FirestoreTestResponse(BaseModel):
    """Response model for Firestore connection test"""
    status: str
    message: str
    collections: list
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Firestore connection successful",
                "collections": ["users", "emails", "logs"],
                "timestamp": "2024-01-15T10:30:00.000Z"
            }
        }


class CollectionResponse(BaseModel):
    """Response model for collection operations"""
    collection: str
    documents: list
    count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "collection": "users",
                "documents": [
                    {
                        "id": "user123",
                        "data": {"name": "John Doe", "email": "john@example.com"}
                    }
                ],
                "count": 1
            }
        }


@router.get("/firestore/test",
           response_model=FirestoreTestResponse,
           summary="Test Firestore Connection",
           description="Test the connection to Firebase Firestore database.")
async def test_firestore_connection(db: firestore.Client = Depends(get_firestore_db)):
    """
    ## Test Firestore Connection
    
    Verifies that the API can successfully connect to Firebase Firestore.
    This endpoint performs a connection test and returns:
    
    - Connection status
    - List of existing collections
    - Timestamp of the test
    
    ### Use Cases
    
    - Verify Firestore integration during setup
    - Troubleshoot database connectivity issues
    - Monitor database health
    
    ### Response
    
    Returns connection status and available collections.
    """
    try:
        # Try to access a collection (this doesn't create it if it doesn't exist)
        collections = db.collections()
        collection_list = [col.id for col in collections]
        
        return FirestoreTestResponse(
            status="success",
            message="Firestore connection successful",
            collections=collection_list,
            timestamp=datetime.datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firestore connection failed: {str(e)}")


@router.post("/firestore/document", 
            response_model=DocumentResponse,
            summary="Create Document",
            description="Create a new document in a Firestore collection.",
            responses={
                200: {
                    "description": "Document created successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "id": "user123",
                                "data": {"name": "John Doe", "email": "john@example.com"},
                                "created_at": "2024-01-15T10:30:00.000Z"
                            }
                        }
                    }
                },
                500: {"description": "Failed to create document"}
            })
async def create_document(
    document: Document, 
    db: firestore.Client = Depends(get_firestore_db)
):
    """
    ## Create Document
    
    Creates a new document in the specified Firestore collection.
    
    ### Parameters
    
    - **collection**: Name of the Firestore collection
    - **document_id**: Optional custom document ID (auto-generated if not provided)
    - **data**: Document data as key-value pairs
    
    ### Features
    
    - Automatic timestamp generation (created_at, updated_at)
    - Custom or auto-generated document IDs
    - Flexible data structure support
    
    ### Example Usage
    
    ```json
    {
        "collection": "users",
        "document_id": "user123",
        "data": {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin"
        }
    }
    ```
    """
    try:
        # Add timestamp
        doc_data = document.data.copy()
        doc_data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        # Create document
        if document.document_id:
            doc_ref = db.collection(document.collection).document(document.document_id)
            doc_ref.set(doc_data)
            doc_id = document.document_id
        else:
            doc_ref = db.collection(document.collection).add(doc_data)
            doc_id = doc_ref[1].id
        
        return DocumentResponse(
            id=doc_id,
            data=document.data,
            created_at=datetime.datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")


@router.get("/firestore/document/{collection}/{document_id}", response_model=DocumentResponse)
async def get_document(
    collection: str, 
    document_id: str, 
    db: firestore.Client = Depends(get_firestore_db)
):
    """Get a document from Firestore"""
    try:
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = doc.to_dict()
        return DocumentResponse(
            id=doc.id,
            data=doc_data,
            created_at=doc_data.get("created_at", "").isoformat() if doc_data.get("created_at") else None,
            updated_at=doc_data.get("updated_at", "").isoformat() if doc_data.get("updated_at") else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.get("/firestore/collection/{collection}",
           response_model=CollectionResponse,
           summary="Get Collection Documents",
           description="Retrieve documents from a Firestore collection with optional limit.")
async def get_collection(
    collection: str, 
    limit: int = 10,
    db: firestore.Client = Depends(get_firestore_db)
):
    """
    ## Get Collection Documents
    
    Retrieves documents from the specified Firestore collection.
    
    ### Parameters
    
    - **collection**: Name of the Firestore collection
    - **limit**: Maximum number of documents to return (default: 10, max: 50)
    
    ### Features
    
    - Pagination support via limit parameter
    - Returns document count
    - Includes all document data
    
    ### Use Cases
    
    - Browse collection contents
    - Data export operations
    - Administrative interfaces
    """
    try:
        docs = db.collection(collection).limit(limit).stream()
        
        documents = []
        for doc in docs:
            doc_data = doc.to_dict()
            documents.append({
                "id": doc.id,
                "data": doc_data
            })
        
        return CollectionResponse(
            collection=collection,
            documents=documents,
            count=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection: {str(e)}")


@router.delete("/firestore/document/{collection}/{document_id}")
async def delete_document(
    collection: str, 
    document_id: str, 
    db: firestore.Client = Depends(get_firestore_db)
):
    """Delete a document from Firestore"""
    try:
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_ref.delete()
        
        return {
            "status": "success",
            "message": f"Document {document_id} deleted from {collection}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")