from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from google_services import get_sheets_service

router = APIRouter()

class SheetModel(BaseModel):
    name: str
    table: List[List[Any]]
    rows: Optional[int] = None
    columns: Optional[int] = None

class SpreadsheetModel(BaseModel):
    title: str
    sheets: List[SheetModel]

@router.post("/drive/spreadsheets", response_model=SpreadsheetModel, status_code=status.HTTP_201_CREATED)
async def create_spreadsheet(
    payload: SpreadsheetModel = Body(...),
    sheets_service=Depends(get_sheets_service)
) -> SpreadsheetModel:
    """Create a new spreadsheet based on payload."""
    try:
        spreadsheet_body = {
            "properties": {"title": payload.title},
            "sheets": [
                {"properties": {"title": sheet.name}} for sheet in payload.sheets
            ]
        }
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = spreadsheet["spreadsheetId"]
        # Optionally populate data for each sheet
        for sheet in payload.sheets:
            if sheet.table:
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet.name}",
                    valueInputOption="RAW",
                    body={"values": sheet.table}
                ).execute()
        # Fetch the created spreadsheet for response
        return await get_spreadsheet(spreadsheet_id, sheets_service)
    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets API error: {e}")

@router.get("/drive/spreadsheets/{spreadsheet_id}", response_model=SpreadsheetModel)
async def get_spreadsheet(
    spreadsheet_id: str,
    sheets_service=Depends(get_sheets_service)
) -> SpreadsheetModel:
    """Return a specific spreadsheet."""
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        title = spreadsheet["properties"]["title"]
        sheets = []
        for sheet in spreadsheet["sheets"]:
            name = sheet["properties"]["title"]
            # Get values
            values_resp = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=name).execute()
            table = values_resp.get("values", [])
            rows = len(table)
            columns = max((len(row) for row in table), default=0)
            sheets.append(SheetModel(name=name, table=table, rows=rows, columns=columns))
        return SpreadsheetModel(title=title, sheets=sheets)
    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets API error: {e}")

@router.post("/drive/spreadsheets/{spreadsheet_id}/sheets", response_model=SheetModel, status_code=status.HTTP_201_CREATED)
async def add_sheet(
    spreadsheet_id: str,
    sheet: SheetModel = Body(...),
    sheets_service=Depends(get_sheets_service)
) -> SheetModel:
    """Add a new sheet to an existing spreadsheet."""
    try:
        add_sheet_request = {
            "requests": [{
                "addSheet": {"properties": {"title": sheet.name}}
            }]
        }
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=add_sheet_request
        ).execute()
        # Optionally populate data
        if sheet.table:
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=sheet.name,
                valueInputOption="RAW",
                body={"values": sheet.table}
            ).execute()
        # Fetch the created sheet for response
        return await get_sheet(spreadsheet_id, sheet.name, sheets_service)
    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets API error: {e}")

@router.get("/drive/spreadsheets/{spreadsheet_id}/sheets/{name}", response_model=SheetModel)
async def get_sheet(
    spreadsheet_id: str,
    name: str,
    sheets_service=Depends(get_sheets_service)
) -> SheetModel:
    """Return a specific sheet from the existing spreadsheet."""
    try:
        values_resp = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=name).execute()
        table = values_resp.get("values", [])
        rows = len(table)
        columns = max((len(row) for row in table), default=0)
        return SheetModel(name=name, table=table, rows=rows, columns=columns)
    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets API error: {e}") 