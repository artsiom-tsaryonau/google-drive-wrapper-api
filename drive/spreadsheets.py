from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from google_services import get_sheets_service
from pydantic import BaseModel
from typing import Any, Optional

router = APIRouter()

# POST /drive/spreadsheets: Create new empty spreadsheet, with optional parent id
@router.post("/drive/spreadsheets")
async def create_spreadsheet(
    parent: Optional[str] = Query(None, description="Optional parent folder id"),
    sheets_service=Depends(get_sheets_service)
):
    body = {"properties": {"title": "New Spreadsheet"}}
    if parent:
        body["parents"] = [parent]
    try:
        spreadsheet = sheets_service.spreadsheets().create(body=body).execute()
        return spreadsheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /drive/spreadsheets/{spreadsheet_id}: Return a spreadsheet by id
@router.get("/drive/spreadsheets/{spreadsheet_id}")
async def get_spreadsheet(spreadsheet_id: str, sheets_service=Depends(get_sheets_service)):
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return spreadsheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /drive/spreadsheets/{spreadsheet_id}/sheets: Create new empty sheet within spreadsheet
class NewSheetRequest(BaseModel):
    name: str

@router.post("/drive/spreadsheets/{spreadsheet_id}/sheets")
async def create_sheet(spreadsheet_id: str, req: NewSheetRequest, sheets_service=Depends(get_sheets_service)):
    body = {
        "requests": [
            {"addSheet": {"properties": {"title": req.name}}}
        ]
    }
    try:
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /drive/spreadsheets/{spreadsheet_id}/sheets/{name}: Return a specific sheet by name
@router.get("/drive/spreadsheets/{spreadsheet_id}/sheets/{name}")
async def get_sheet(spreadsheet_id: str, name: str, sheets_service=Depends(get_sheets_service)):
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get("sheets", [])
        for sheet in sheets:
            if sheet["properties"]["title"] == name:
                return sheet
        raise HTTPException(status_code=404, detail=f"Sheet '{name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range: Returns the range based on A1 notation provided in 'a1' query parameter
@router.get("/drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range")
async def get_sheet_range(
    spreadsheet_id: str,
    name: str,
    a1: str = Query(..., description="A1 notation range, e.g. 'A1:B2'"),
    sheets_service=Depends(get_sheets_service)
):
    try:
        # Find the sheet ID by name
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get("sheets", [])
        sheet_id = None
        for sheet in sheets:
            if sheet["properties"]["title"] == name:
                sheet_id = sheet["properties"]["sheetId"]
                break
        if sheet_id is None:
            raise HTTPException(status_code=404, detail=f"Sheet '{name}' not found.")
        # Compose the full range as 'SheetName!A1:B2'
        full_range = f"{name}!{a1}"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=full_range
        ).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range: Updates the range based on A1 notation with payload containing the values and query parameter containing range
class UpdateRangeRequest(BaseModel):
    values: list

@router.put("/drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range")
async def update_sheet_range(
    spreadsheet_id: str,
    name: str,
    a1: str = Query(..., description="A1 notation range, e.g. 'A1:B2'"),
    req: UpdateRangeRequest = Body(...),
    sheets_service=Depends(get_sheets_service)
):
    try:
        # Find the sheet ID by name
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get("sheets", [])
        sheet_id = None
        for sheet in sheets:
            if sheet["properties"]["title"] == name:
                sheet_id = sheet["properties"]["sheetId"]
                break
        if sheet_id is None:
            raise HTTPException(status_code=404, detail=f"Sheet '{name}' not found.")
        # Compose the full range as 'SheetName!A1:B2'
        full_range = f"{name}!{a1}"
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            valueInputOption="RAW",
            body={"values": req.values}
        ).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 