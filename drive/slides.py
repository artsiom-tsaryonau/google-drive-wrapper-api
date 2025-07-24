from fastapi import APIRouter, Depends, HTTPException, status, Query
from google_services import get_slides_service
from typing import Optional

router = APIRouter()

# POST /drive/slides: Create new empty presentation, with optional parent id
@router.post("/drive/slides")
async def create_presentation(
    parent: Optional[str] = Query(None, description="Optional parent folder id"),
    slides_service=Depends(get_slides_service)
):
    body = {"title": "New Presentation"}
    if parent:
        body["parents"] = [parent]
    try:
        presentation = slides_service.presentations().create(body=body).execute()
        return presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /drive/slides/{slides_id}: Return a specific presentation
@router.get("/drive/slides/{slides_id}")
async def get_presentation(slides_id: str, slides_service=Depends(get_slides_service)):
    try:
        presentation = slides_service.presentations().get(presentationId=slides_id).execute()
        return presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 