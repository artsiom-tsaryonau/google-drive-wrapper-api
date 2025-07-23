from fastapi import APIRouter, Depends, HTTPException
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_docs_service

router = APIRouter()

@router.get("/drive/document/{file_id}")
async def get_google_document(file_id: str, drive_service=Depends(get_drive_service), docs_service=Depends(get_docs_service)):
    try:
        file_metadata = drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if file_metadata.get('mimeType') != 'application/vnd.google-apps.document':
            raise HTTPException(status_code=400, detail="File is not a Google Document.")

        document = docs_service.documents().get(documentId=file_id).execute()
        return document
    except HttpError as error:
        raise HTTPException(status_code=error.resp.status, detail=f"An error occurred: {error}") 