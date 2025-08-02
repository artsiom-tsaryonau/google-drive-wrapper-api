from fastapi import APIRouter, Depends, HTTPException, status, Query
from google_services import get_docs_service, get_drive_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# POST /drive/documents?parent=&title=: Create new empty document, with optional parent id parameter
@router.post("/drive/documents")
async def create_document(
    parent: Optional[str] = Query(None, description="Optional parent folder id"),
    title: str = Query(..., description="Document title"),
    docs_service=Depends(get_docs_service),
    drive_service=Depends(get_drive_service)
):
    """
    Create a new empty document with an optional parent folder.
    
    Example input request:
        POST /drive/documents?title=MyDocument&parent=1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7
    
    Google API request sent:
        First creates document via docs_service.documents().create()
        Then moves to parent folder via drive_service.files().update() if parent specified
    """
    try:
        # Create the document
        document = docs_service.documents().create(body={'title': title}).execute()
        
        # If parent is specified, move the document to that folder
        if parent:
            file_id = document['documentId']
            drive_service.files().update(
                fileId=file_id,
                addParents=parent,
                fields='id, name, parents'
            ).execute()
        
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /drive/documents/{document_id}: Return a specific document by id
@router.get("/drive/documents/{document_id}")
async def get_document(document_id: str, docs_service=Depends(get_docs_service)):
    """
    Get a document by its ID.
    
    Example input request:
        GET /drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo
    
    Google API request sent:
        docs_service.documents().get(documentId=document_id)
    """
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /drive/documents/{document_id}: Delete document by id
@router.delete("/drive/documents/{document_id}")
async def delete_document(document_id: str, drive_service=Depends(get_drive_service)):
    """
    Delete a document by its ID.
    
    Example input request:
        DELETE /drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo
    
    Google API request sent:
        drive_service.files().delete(fileId=document_id)
    """
    try:
        drive_service.files().delete(fileId=document_id).execute()
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 