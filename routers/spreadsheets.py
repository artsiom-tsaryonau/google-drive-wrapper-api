from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_sheets_service

# --- Pydantic Models ---

class SpreadsheetCreate(BaseModel):
    title: str

class SpreadsheetInfo(BaseModel):
    id: str
    name: str

class Sheet(BaseModel):
    title: str
    values: List[List[Any]] = []

class Spreadsheet(BaseModel):
    spreadsheet_id: str
    title: str
    sheets: List[Sheet]

class AppendDataPayload(BaseModel):
    values: List[List[Any]]

class AddSheetPayload(BaseModel):
    title: str

# --- Service Class for Business Logic ---

class SpreadsheetService:
    def __init__(self, drive_service: Resource = Depends(get_drive_service), sheets_service: Resource = Depends(get_sheets_service)):
        self.drive_service = drive_service
        self.sheets_service = sheets_service

    def create_spreadsheet(self, title: str) -> Dict[str, Any]:
        try:
            metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
            file = self.drive_service.files().create(body=metadata, fields='id, name').execute()
            return file
        except HttpError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating spreadsheet: {e}")

    def get_spreadsheet(self, spreadsheet_id: str) -> Spreadsheet:
        try:
            self._verify_is_spreadsheet(spreadsheet_id)
            sheet_metadata = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            
            sheets_data = []
            for s in sheet_metadata.get('sheets', []):
                title = s['properties']['title']
                result = self.sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=title).execute()
                sheets_data.append(Sheet(title=title, values=result.get('values', [])))

            return Spreadsheet(
                spreadsheet_id=sheet_metadata['spreadsheetId'],
                title=sheet_metadata['properties']['title'],
                sheets=sheets_data
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Spreadsheet '{spreadsheet_id}' not found.")
            raise HTTPException(e.resp.status, f"Error fetching spreadsheet: {e}")

    def append_data(self, spreadsheet_id: str, sheet_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        try:
            self._verify_is_spreadsheet(spreadsheet_id)
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=sheet_name,
                valueInputOption='USER_ENTERED', body=body
            ).execute()
            return result
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Spreadsheet '{spreadsheet_id}' not found.")
            if "Unable to parse range" in str(e):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Sheet '{sheet_name}' not found in spreadsheet.")
            raise HTTPException(e.resp.status, f"Error appending data: {e}")

    def add_sheet(self, spreadsheet_id: str, title: str) -> Dict[str, Any]:
        try:
            self._verify_is_spreadsheet(spreadsheet_id)
            requests = [{'addSheet': {'properties': {'title': title}}}]
            result = self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={'requests': requests}
            ).execute()
            return result['replies'][0]['addSheet']['properties']
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Spreadsheet '{spreadsheet_id}' not found.")
            raise HTTPException(e.resp.status, f"Error adding sheet: {e}")
            
    def clear_sheet(self, spreadsheet_id: str, sheet_name: str) -> Dict[str, str]:
        try:
            self._verify_is_spreadsheet(spreadsheet_id)
            self.sheets_service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id, range=sheet_name
            ).execute()
            return {"spreadsheetId": spreadsheet_id, "clearedRange": sheet_name}
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Spreadsheet '{spreadsheet_id}' not found.")
            if "Unable to parse range" in str(e):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Sheet '{sheet_name}' not found in spreadsheet.")
            raise HTTPException(e.resp.status, f"Error clearing sheet: {e}")

    def _verify_is_spreadsheet(self, file_id: str):
        metadata = self.drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if metadata.get('mimeType') != 'application/vnd.google-apps.spreadsheet':
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is not a Google Spreadsheet.")

# --- API Router ---

router = APIRouter(
    prefix="/drive/spreadsheets",
    tags=["Spreadsheets"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SpreadsheetInfo)
def create_spreadsheet(payload: SpreadsheetCreate, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Create a new empty Google Spreadsheet."""
    return service.create_spreadsheet(payload.title)

@router.get("/{spreadsheet_id}", response_model=Spreadsheet)
def get_spreadsheet(spreadsheet_id: str, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Get a Google Spreadsheet by its ID, including all sheets and values."""
    return service.get_spreadsheet(spreadsheet_id)

@router.post("/{spreadsheet_id}/sheets", response_model=Dict)
def add_sheet(spreadsheet_id: str, payload: AddSheetPayload, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Add a new sheet to an existing spreadsheet."""
    return service.add_sheet(spreadsheet_id, payload.title)

@router.post("/{spreadsheet_id}/sheets/{sheet_name}:append", response_model=Dict)
def append_data(spreadsheet_id: str, sheet_name: str, payload: AppendDataPayload, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Append data to a specific sheet in a spreadsheet."""
    return service.append_data(spreadsheet_id, sheet_name, payload.values)

@router.post("/{spreadsheet_id}/sheets/{sheet_name}:clear", response_model=Dict)
def clear_sheet(spreadsheet_id: str, sheet_name: str, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Clear all data from a specific sheet."""
    return service.clear_sheet(spreadsheet_id, sheet_name) 