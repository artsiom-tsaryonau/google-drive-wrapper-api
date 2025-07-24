from fastapi import APIRouter, Depends, HTTPException, status, Query
from google_services import get_docs_service
from typing import Optional

router = APIRouter()

# POST /drive/document: Create new empty document, with optional parent id
@router.post("/drive/document")
async def create_document(
    parent: Optional[str] = Query(None, description="Optional parent folder id"),
    docs_service=Depends(get_docs_service)
):
    body = {"title": "New Document"}
    if parent:
        body["parents"] = [parent]
    try:
        document = docs_service.documents().create(body=body).execute()
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /drive/document/{document_id}: Return a specific document
@router.get("/drive/document/{document_id}")
async def get_document(document_id: str, docs_service=Depends(get_docs_service)):
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 