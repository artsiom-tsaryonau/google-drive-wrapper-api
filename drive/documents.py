from fastapi import APIRouter, Depends, HTTPException, status, Query
from google_services import get_docs_service
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

# POST /drive/documents: Create new empty document, with optional parent id
@router.post("/drive/documents")
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

# GET /drive/documents/{document_id}: Return a specific document
@router.get("/drive/documents/{document_id}")
async def get_document(document_id: str, docs_service=Depends(get_docs_service)):
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /drive/documents/{document_id}/heading: Add a heading to the document
class HeadingRequest(BaseModel):
    text: str
    level: int  # 1 for h1, 2 for h2, etc.

@router.put("/drive/documents/{document_id}/heading")
async def add_heading(
    document_id: str,
    req: HeadingRequest,
    docs_service=Depends(get_docs_service)
):
    # Google Docs API: Insert text and apply heading style
    try:
        # Insert the heading text at the start of the document
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": req.text + "\n"
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": 1,
                        "endIndex": 1 + len(req.text) + 1
                    },
                    "paragraphStyle": {
                        "namedStyleType": f"HEADING_{req.level}"
                    },
                    "fields": "namedStyleType"
                }
            }
        ]
        result = docs_service.documents().batchUpdate(
            documentId=document_id,
            body={"requests": requests}
        ).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 