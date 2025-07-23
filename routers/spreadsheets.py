from fastapi import APIRouter, Depends, HTTPException
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_sheets_service

router = APIRouter()

@router.get("/drive/spreadsheet/{file_id}")
async def get_google_spreadsheet(file_id: str, drive_service=Depends(get_drive_service), sheets_service=Depends(get_sheets_service)):
    try:
        file_metadata = drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if file_metadata.get('mimeType') != 'application/vnd.google-apps.spreadsheet':
            raise HTTPException(status_code=400, detail="File is not a Google Spreadsheet.")

        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
        if not spreadsheet.get('sheets'):
            return {"values": []}

        sheet_title = spreadsheet['sheets'][0]['properties']['title']
        range_name = f"'{sheet_title}'"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=file_id,
            range=range_name
        ).execute()
        return result
    except HttpError as error:
        raise HTTPException(status_code=error.resp.status, detail=f"An error occurred: {error}") 