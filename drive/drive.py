from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from googleapiclient.errors import HttpError
from pydantic.fields import Field
from google_services import get_drive_service

router = APIRouter()

class DriveObject(BaseModel):
    id: str
    name: str
    mimeType: str
    path: str
    parent_id: Optional[str] = Field(None, description="Parent ID of the file")


def build_drive_object(item: dict, parent_path: str = "") -> DriveObject:
    """Builds a DriveObject from Google Drive API item."""
    return DriveObject(
        id=item.get("id"),
        name=item.get("name"),
        mimeType=item.get("mimeType"),
        path=f"{parent_path}/{item.get('name')}" if parent_path else f"/{item.get('name')}",
        parent_id=item.get("parents", [None])[0]
    )

@router.get("/drive/search", response_model=List[DriveObject])
async def search_drive(
    name: Optional[str] = Query(None, description="Name to search for"),
    mimeType: Optional[str] = Query(None, description="Filter by mimeType"),
    drive_service=Depends(get_drive_service)
) -> List[DriveObject]:
    """Search Google Drive objects by name with optional mimeType filter."""
    try:
        q = []
        if name:
            q.append(f"name contains '{name}'")
        if mimeType:
            q.append(f"mimeType='{mimeType}'")
        query = " and ".join(q) if q else None
        results = drive_service.files().list(q=query, fields="files(id, name, mimeType, parents)").execute()
        files = results.get("files", [])
        return [build_drive_object(f) for f in files]
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.get("/drive/navigate/{path:path}", response_model=List[DriveObject])
async def list_drive_path(
    path: str,
    mimeType: Optional[str] = Query(None, description="Filter by mimeType"),
    drive_service=Depends(get_drive_service)
) -> List[DriveObject]:
    """List Google Drive content in a specific path with optional mimeType filter."""
    try:
        parts = [p for p in path.strip("/").split("/") if p]
        parent_id = "root"
        parent_path = ""
        for part in parts:
            q = f"'{parent_id}' in parents and name='{part}' and mimeType='application/vnd.google-apps.folder'"
            res = drive_service.files().list(q=q, fields="files(id, name, mimeType, parents)").execute()
            folders = res.get("files", [])
            if not folders:
                raise HTTPException(status_code=404, detail=f"Folder '{part}' not found in path '{parent_path}'")
            parent_id = folders[0]["id"]
            parent_path += f"/{part}"
        q = f"'{parent_id}' in parents"
        if mimeType:
            q += f" and mimeType='{mimeType}'"
        results = drive_service.files().list(q=q, fields="files(id, name, mimeType, parents)").execute()
        files = results.get("files", [])
        return [build_drive_object(f, parent_path) for f in files]
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.delete("/drive/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drive_object(
    id: str,
    drive_service=Depends(get_drive_service)
) -> None:
    """Deletes an object by id from Google Drive."""
    try:
        drive_service.files().delete(fileId=id).execute()
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))


