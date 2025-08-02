from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field

class CommentRequest(BaseModel):
    content: str
    anchor: Optional[str] = Field(None, description="Custom anchor string for Google Docs")

class ReplyRequest(BaseModel):
    content: str 