from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
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

class Color(BaseModel):
    red: float = Field(0.0, ge=0, le=1)
    green: float = Field(0.0, ge=0, le=1)
    blue: float = Field(0.0, ge=0, le=1)

class TextFormat(BaseModel):
    foregroundColor: Optional[Color] = None
    fontFamily: Optional[str] = None
    fontSize: Optional[int] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    strikethrough: Optional[bool] = None
    underline: Optional[bool] = None

class CellFormat(BaseModel):
    textFormat: Optional[TextFormat] = None

class CellData(BaseModel):
    value: Any
    format: Optional[CellFormat] = None

class AppendDataPayload(BaseModel):
    values: List[List[Any]]
    
class AppendFormattedDataPayload(BaseModel):
    values: List[List[CellData]]

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

    def append_formatted_data(self, spreadsheet_id: str, sheet_name: str, data: AppendFormattedDataPayload) -> Dict[str, Any]:
        try:
            self._verify_is_spreadsheet(spreadsheet_id)

            # 1. Get sheet ID
            spreadsheet_meta = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_id = None
            for sheet in spreadsheet_meta.get('sheets', []):
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            if sheet_id is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Sheet '{sheet_name}' not found.")

            # 2. Get current number of rows to append after
            sheet_values = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=f"'{sheet_name}'!A:A"
            ).execute()
            start_row = len(sheet_values.get('values', []))

            # 3. Build requests
            requests = self._build_format_requests(sheet_id, start_row, data)

            if requests:
                self.sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, body={'requests': requests}
                ).execute()

            return {"status": "success", "message": f"Appended formatted data to {sheet_name}"}

        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Spreadsheet '{spreadsheet_id}' not found.")
            raise HTTPException(e.resp.status, f"Error appending formatted data: {e}")

    def _build_format_requests(self, sheet_id: int, start_row: int, data: AppendFormattedDataPayload) -> List[Dict[str, Any]]:
        requests = []
        rows_data = []
        for r, row in enumerate(data.values):
            row_data = {'values': []}
            for c, cell in enumerate(row):
                cell_data = {'userEnteredValue': self._get_user_entered_value(cell.value)}
                if cell.format and cell.format.textFormat:
                    cell_data['userEnteredFormat'] = {'textFormat': cell.format.textFormat.dict(exclude_none=True)}
                row_data['values'].append(cell_data)

                # This is an alternative way to format cells, but it's more verbose
                # if cell.format:
                #     requests.append({
                #         'repeatCell': {
                #             'range': {
                #                 'sheetId': sheet_id,
                #                 'startRowIndex': start_row + r,
                #                 'endRowIndex': start_row + r + 1,
                #                 'startColumnIndex': c,
                #                 'endColumnIndex': c + 1
                #             },
                #             'cell': {'userEnteredFormat': cell.format.dict(exclude_none=True)},
                #             'fields': 'userEnteredFormat(textFormat)'
                #         }
                #     })
            rows_data.append(row_data)

        if rows_data:
            requests.append({
                'appendCells': {
                    'sheetId': sheet_id,
                    'rows': rows_data,
                    'fields': '*'
                }
            })
        return requests

    def _get_user_entered_value(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, bool):
            return {'boolValue': value}
        if isinstance(value, (int, float)):
            return {'numberValue': value}
        return {'stringValue': str(value)}

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
    prefix="/spreadsheets",
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

@router.post("/{spreadsheet_id}/sheets/{sheet_name}:appendFormatted", response_model=Dict)
def append_formatted_data(spreadsheet_id: str, sheet_name: str, payload: AppendFormattedDataPayload, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Append data with cell-level formatting to a specific sheet."""
    return service.append_formatted_data(spreadsheet_id, sheet_name, payload)

@router.post("/{spreadsheet_id}/sheets/{sheet_name}:clear", response_model=Dict)
def clear_sheet(spreadsheet_id: str, sheet_name: str, service: SpreadsheetService = Depends(SpreadsheetService)):
    """Clear all data from a specific sheet."""
    return service.clear_sheet(spreadsheet_id, sheet_name) 