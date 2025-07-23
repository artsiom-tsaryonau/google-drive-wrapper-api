from fastapi import APIRouter, Depends, HTTPException
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_slides_service

router = APIRouter()

@router.get("/drive/slides/{file_id}")
async def get_google_slides(file_id: str, drive_service=Depends(get_drive_service), slides_service=Depends(get_slides_service)):
    try:
        file_metadata = drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if file_metadata.get('mimeType') != 'application/vnd.google-apps.presentation':
            raise HTTPException(status_code=400, detail="File is not a Google Slides presentation.")

        presentation = slides_service.presentations().get(presentationId=file_id).execute()
        return presentation
    except HttpError as error:
        raise HTTPException(status_code=error.resp.status, detail=f"An error occurred: {error}") 