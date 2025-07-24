from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from google_services import get_sheets_service
from pydantic import BaseModel
from typing import Any, Optional, Dict

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

# DELETE /drive/spreadsheets/{spreadsheet_id}/sheets/{name}: Deletes a specific sheet from the spreadsheet
@router.delete("/drive/spreadsheets/{spreadsheet_id}/sheets/{name}")
async def delete_sheet(spreadsheet_id: str, name: str, sheets_service=Depends(get_sheets_service)):
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get("sheets", [])
        sheet_id = None
        for sheet in sheets:
            if sheet["properties"]["title"] == name:
                sheet_id = sheet["properties"]["sheetId"]
                break
        if sheet_id is None:
            raise HTTPException(status_code=404, detail=f"Sheet '{name}' not found.")
        body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
        result = sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1=: Deletes a range from the sheet based on A1
@router.delete("/drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range")
async def delete_range(
    spreadsheet_id: str,
    name: str,
    a1: str = Query(..., description="A1 notation range to clear, e.g. 'A1:B2'"),
    sheets_service=Depends(get_sheets_service)
):
    try:
        full_range = f"{name}!{a1}"
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            body={}
        ).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range: Updates the range based on A1 notation with payload containing the values and query parameter containing range
class UpdateRangeRequest(BaseModel):
    values: list
    format: Optional[Dict[str, Any]] = None  # Optional formatting

def a1_to_grid_range(a1: str) -> dict:
    """
    Convert A1 notation (e.g., 'A1:B2') to a dict with startRowIndex, endRowIndex, startColumnIndex, endColumnIndex.
    All indices are zero-based and end-exclusive, as required by Google Sheets API.
    """
    import re
    def col_to_index(col):
        idx = 0
        for c in col:
            idx = idx * 26 + (ord(c.upper()) - ord('A') + 1)
        return idx - 1
    match = re.match(r"^([A-Z]+)([0-9]+)(:([A-Z]+)([0-9]+))?$", a1)
    if not match:
        raise ValueError(f"Invalid A1 notation: {a1}")
    start_col, start_row, _, end_col, end_row = match.groups()
    start_row_idx = int(start_row) - 1
    start_col_idx = col_to_index(start_col)
    if end_col and end_row:
        end_row_idx = int(end_row)
        end_col_idx = col_to_index(end_col) + 1
    else:
        end_row_idx = start_row_idx + 1
        end_col_idx = start_col_idx + 1
    return {
        "startRowIndex": start_row_idx,
        "endRowIndex": end_row_idx,
        "startColumnIndex": start_col_idx,
        "endColumnIndex": end_col_idx
    }

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
        # Update values
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            valueInputOption="RAW",
            body={"values": req.values}
        ).execute()
        # Optionally apply formatting
        if req.format:
            grid_range = a1_to_grid_range(a1)
            grid_range["sheetId"] = sheet_id
            body = {
                "requests": [
                    {
                        "repeatCell": {
                            "range": grid_range,
                            "cell": {"userEnteredFormat": req.format},
                            "fields": ",".join(req.format.keys())
                        }
                    }
                ]
            }
            sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 