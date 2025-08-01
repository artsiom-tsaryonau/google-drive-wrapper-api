from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
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

class CommentRequest(BaseModel):
    content: str
    anchor: Optional[str] = Field(None, description="Anchor for the comment") # Required for anchored comments

class ReplyRequest(BaseModel):
    content: str

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
        raise HTTPException(status_code=500, detail=f"Google API error: {e}")

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
        raise HTTPException(status_code=500, detail=f"Google API error: {e}")

@router.delete("/drive/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drive_object(
    id: str,
    drive_service=Depends(get_drive_service)
) -> None:
    """Deletes an object by id from Google Drive."""
    try:
        drive_service.files().delete(fileId=id).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise HTTPException(status_code=404, detail=f"File with id '{id}' not found.")
        raise HTTPException(status_code=500, detail=f"Google API error: {e}")

@router.get("/drive/{file_id}/comment")
async def list_comments(
    file_id: str,
    drive_service=Depends(get_drive_service)
):
    """
    List all comments for a file.
    
    Example input request:
        GET /drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment
    
    Google API request sent:
        drive_service.comments().list(fileId=file_id, fields="comments(id,createdTime,modifiedTime,author,content,htmlContent,deleted,resolved,anchor,quotedFileContent)")
    """
    try:
        comments = drive_service.comments().list(
            fileId=file_id, 
            fields="comments(id,createdTime,modifiedTime,author,content,htmlContent,deleted,resolved,anchor,quotedFileContent)"
        ).execute()
        return comments
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.get("/drive/{file_id}/comment/{comment_id}")
async def get_comment(
    file_id: str,
    comment_id: str,
    drive_service=Depends(get_drive_service)
):
    """
    Get a specific comment by ID.
    
    Example input request:
        GET /drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123
    
    Google API request sent:
        drive_service.comments().get(fileId=file_id, commentId=comment_id, fields="id,createdTime,modifiedTime,author,content,htmlContent,deleted,resolved,anchor,quotedFileContent")
    """
    try:
        comment = drive_service.comments().get(
            fileId=file_id,
            commentId=comment_id,
            fields="id,createdTime,modifiedTime,author,content,htmlContent,deleted,resolved,anchor,quotedFileContent"
        ).execute()
        return comment
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.post("/drive/{file_id}/comment")
async def add_comment(
    file_id: str,
    req: CommentRequest = Body(...),
    drive_service=Depends(get_drive_service)
):
    try:
        # Build the comment body
        comment_body = {"content": req.content}
        if req.anchor:
            comment_body["anchor"] = req.anchor
        
        comment = drive_service.comments().create(
            fileId=file_id,
            body=comment_body,
            fields="id,createdTime,modifiedTime,author,content,htmlContent,deleted,resolved,anchor,quotedFileContent"
        ).execute()
        return comment
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.delete("/drive/{file_id}/comment/{comment_id}")
async def delete_comment(
    file_id: str,
    comment_id: str,
    drive_service=Depends(get_drive_service)
):
    """
    Delete a comment from a file.
    
    Example input request:
        DELETE /drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123
    
    Google API request sent:
        drive_service.comments().delete(
            fileId=file_id,
            commentId=comment_id
        )
    """
    try:
        drive_service.comments().delete(
            fileId=file_id,
            commentId=comment_id
        ).execute()
        return {"message": f"Comment {comment_id} deleted successfully"}
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.post("/drive/{file_id}/comment/{comment_id}/reply")
async def add_reply(
    file_id: str,
    comment_id: str,
    req: ReplyRequest = Body(...),
    drive_service=Depends(get_drive_service)
):
    """
    Add a reply to a comment.
    
    Example input request:
        POST /drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123/reply
        Body: {"content": "This is a reply to the comment"}
    
    Google API request sent:
        drive_service.replies().create(
            fileId=file_id,
            commentId=comment_id,
            body={"content": "This is a reply to the comment"}
        )
    """
    try:
        reply = drive_service.replies().create(
            fileId=file_id,
            commentId=comment_id,
            body={"content": req.content}
        ).execute()
        return reply
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))

@router.post("/drive/{file_id}/comment/{comment_id}/resolve")
async def resolve_comment(
    file_id: str,
    comment_id: str,
    drive_service=Depends(get_drive_service)
):
    """
    Resolve a comment (mark it as resolved).
    
    Example input request:
        POST /drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123/resolve
    
    Google API request sent:
        drive_service.comments().update(
            fileId=file_id,
            commentId=comment_id,
            body={"resolved": True}
        )
    """
    try:
        comment = drive_service.comments().update(
            fileId=file_id,
            commentId=comment_id,
            body={"resolved": True}
        ).execute()
        return comment
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
