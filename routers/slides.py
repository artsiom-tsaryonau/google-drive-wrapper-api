from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_slides_service

# Pydantic Models for type safety and API documentation
class PresentationCreate(BaseModel):
    title: str

class PresentationInfo(BaseModel):
    id: str
    name: str

class SlideContent(BaseModel):
    layout: str = Field(..., description="Layout for the new slide.")
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None

class SlideCreationResponse(BaseModel):
    slideId: str

# Router configuration for better organization
router = APIRouter(
    prefix="/drive/presentations",
    tags=["Presentations"],
    responses={404: {"description": "Not found"}},
)

LAYOUTS = {
    "TITLE_SLIDE": {
        "predefined_layout": "TITLE",
        "placeholders": {
            "title": {"type": "CENTERED_TITLE"},
            "subtitle": {"type": "SUBTITLE"}
        }
    },
    "TITLE_AND_BODY": {
        "predefined_layout": "TITLE_AND_BODY",
        "placeholders": {
            "title": {"type": "TITLE"},
            "body": {"type": "BODY"}
        }
    },
    "TITLE_ONLY": {
        "predefined_layout": "TITLE_ONLY",
        "placeholders": {
            "title": {"type": "TITLE"}
        }
    },
    "BLANK": {
        "predefined_layout": "BLANK",
        "placeholders": {}
    }
}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PresentationInfo)
async def create_google_presentation(presentation: PresentationCreate, drive_service=Depends(get_drive_service)):
    """
    Create a new empty Google Slides presentation.
    """
    try:
        file_metadata = {
            'name': presentation.title,
            'mimeType': 'application/vnd.google-apps.presentation'
        }
        file = drive_service.files().create(body=file_metadata, fields='id, name').execute()
        return file
    except HttpError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while creating presentation: {error}")


@router.get("/{presentation_id}", response_model=dict)
async def get_google_presentation(presentation_id: str, drive_service=Depends(get_drive_service), slides_service=Depends(get_slides_service)):
    """
    Get a Google Slides presentation by its ID.
    """
    try:
        file_metadata = drive_service.files().get(fileId=presentation_id, fields='mimeType').execute()
        if file_metadata.get('mimeType') != 'application/vnd.google-apps.presentation':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is not a Google Slides presentation.")

        presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
        return presentation
    except HttpError as error:
        if error.resp.status == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Presentation with ID '{presentation_id}' not found.")
        raise HTTPException(status_code=error.resp.status, detail=f"An error occurred while fetching presentation: {error}")


@router.post("/{presentation_id}/slides", status_code=status.HTTP_201_CREATED, response_model=SlideCreationResponse)
async def add_slide_to_presentation(presentation_id: str, content: SlideContent, slides_service=Depends(get_slides_service)):
    """
    Add a new slide to an existing presentation.
    """
    layout_name = content.layout.upper()
    if layout_name not in LAYOUTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid layout. Supported layouts: {', '.join(LAYOUTS.keys())}"
        )

    layout_config = LAYOUTS[layout_name]
    slide_id = f"new_slide_{uuid.uuid4().hex}"
    
    requests = [
        {
            "createSlide": {
                "objectId": slide_id,
                "slideLayoutReference": {
                    "predefinedLayout": layout_config["predefined_layout"]
                }
            }
        }
    ]

    content_map = {
        "title": content.title,
        "subtitle": content.subtitle,
        "body": content.body
    }

    for name, text in content_map.items():
        if text and name in layout_config["placeholders"]:
            placeholder_type = layout_config["placeholders"][name]['type']
            requests.append({
                "insertText": {
                    "objectId": slide_id,
                    "text": text,
                    "placeholderType": placeholder_type
                }
            })

    body = {"requests": requests}
    try:
        response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        
        created_slide_info = response['replies'][0]['createSlide']
        created_slide_id = created_slide_info['objectId']
        
        return {"slideId": created_slide_id}

    except HttpError as error:
        if error.resp.status == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Presentation with ID '{presentation_id}' not found.")
        raise HTTPException(status_code=error.resp.status, detail=f"An error occurred while adding slide: {error}")
    except (KeyError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not retrieve created slide ID from Google API response."
        ) 