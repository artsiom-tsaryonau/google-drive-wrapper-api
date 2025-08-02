from fastapi import APIRouter, Depends, Body, HTTPException
from googleapiclient.errors import HttpError
from google_services import get_drive_service
from .models import CommentRequest, ReplyRequest

router = APIRouter()

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
    """
    Create a new comment on a file.
    
    Note: The comment system uses a custom anchor system for Google Docs.
    The anchor parameter is passed through as-is without validation.
    For other file types (Spreadsheets, Slides), anchoring is not yet supported.
    
    Example input request:
        POST /drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment
        Body: {
            "content": "This is a comment",
            "anchor": "custom_anchor_string"
        }
    """
    try:
        # Build the comment body
        comment_body = {"content": req.content}
        
        # Handle custom anchor system for Google Docs
        if req.anchor:
            # Pass through the anchor string without validation
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