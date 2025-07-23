from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_slides_service

# --- Pydantic Models ---

class PresentationCreate(BaseModel):
    title: str

class PresentationInfo(BaseModel):
    id: str
    name: str

class Color(BaseModel):
    red: float = Field(0.0, ge=0, le=1)
    green: float = Field(0.0, ge=0, le=1)
    blue: float = Field(0.0, ge=0, le=1)

class TextStyle(BaseModel):
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    foreground_color: Optional[Color] = None

class TextPayload(BaseModel):
    text: str
    style: Optional[TextStyle] = None
    element_id: Optional[str] = None

class TablePayload(BaseModel):
    rows: int
    columns: int
    data: List[List[str]]
    element_id: Optional[str] = None

class SlidePayload(BaseModel):
    layout: str = Field(..., description="Layout for the new slide.")
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    texts: Optional[List[TextPayload]] = None
    tables: Optional[List[TablePayload]] = None

class Slide(SlidePayload):
    slide_id: str

class Presentation(BaseModel):
    presentation_id: str
    title: str
    slides: List[Slide]

class SlideCreationResponse(BaseModel):
    slideId: str

# --- Service Class for Business Logic ---

class PresentationService:
    LAYOUTS = {
        "TITLE_SLIDE": {"predefined_layout": "TITLE", "placeholders": {"title": {"type": "CENTERED_TITLE"}, "subtitle": {"type": "SUBTITLE"}}},
        "TITLE_AND_BODY": {"predefined_layout": "TITLE_AND_BODY", "placeholders": {"title": {"type": "TITLE"}, "body": {"type": "BODY"}}},
        "TITLE_ONLY": {"predefined_layout": "TITLE_ONLY", "placeholders": {"title": {"type": "TITLE"}}},
        "BLANK": {"predefined_layout": "BLANK", "placeholders": {}},
    }
    REVERSE_LAYOUTS = {v["predefined_layout"]: k for k, v in LAYOUTS.items()}
    PLACEHOLDER_MAP = {p["type"]: k for _, details in LAYOUTS.items() for k, p in details["placeholders"].items()}

    def __init__(self, drive_service: Resource = Depends(get_drive_service), slides_service: Resource = Depends(get_slides_service)):
        self.drive_service = drive_service
        self.slides_service = slides_service

    def _extract_text(self, shape: Dict[str, Any]) -> Optional[str]:
        if 'text' not in shape:
            return None
        content = "".join(el.get('textRun', {}).get('content', '') for el in shape['text'].get('textElements', []))
        return content.strip() or None

    def create_presentation(self, title: str) -> Dict[str, Any]:
        try:
            '''
                body = {
                    'name': title,
                    'mimeType': 'application/vnd.google-apps.presentation',
                    'parents': ['### folder ID ###']
                }
            '''
            metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.presentation'}
            file = self.drive_service.files().create(body=metadata, fields='id, name').execute()
            return file
        except HttpError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating presentation: {e}")

    def get_presentation(self, presentation_id: str) -> Presentation:
        try:
            self._verify_is_presentation(presentation_id)
            presentation_data = self.slides_service.presentations().get(
                presentationId=presentation_id, fields="presentationId,title,slides,layouts"
            ).execute()
            
            slides = self._simplify_slides(presentation_data)
            
            return Presentation(
                presentation_id=presentation_data['presentationId'],
                title=presentation_data['title'],
                slides=slides
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Presentation '{presentation_id}' not found.")
            raise HTTPException(e.resp.status, f"Error fetching presentation: {e}")

    def add_slide(self, presentation_id: str, payload: SlidePayload) -> Dict[str, str]:
        layout_name = payload.layout.upper()
        if layout_name not in self.LAYOUTS:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid layout. Use one of: {', '.join(self.LAYOUTS.keys())}")

        layout_config = self.LAYOUTS[layout_name]
        slide_id = f"new_slide_{uuid.uuid4().hex}"
        requests = self._build_add_slide_requests(slide_id, layout_config, payload)
        
        try:
            response = self.slides_service.presentations().batchUpdate(presentationId=presentation_id, body={"requests": requests}).execute()
            created_info = response['replies'][0]['createSlide']
            return {"slideId": created_info['objectId']}
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Presentation '{presentation_id}' not found.")
            raise HTTPException(e.resp.status, f"Error adding slide: {e}")
        except (KeyError, IndexError):
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not get created slide ID from API response.")

    def delete_slide(self, presentation_id: str, slide_id: str):
        try:
            self._verify_is_presentation(presentation_id)
            requests = [{'deleteObject': {'objectId': slide_id}}]
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Presentation '{presentation_id}' or slide '{slide_id}' not found.")
            raise HTTPException(e.resp.status, f"Error deleting slide: {e}")

    def _verify_is_presentation(self, file_id: str):
        metadata = self.drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if metadata.get('mimeType') != 'application/vnd.google-apps.presentation':
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is not a Google Slides presentation.")

    def _simplify_slides(self, presentation_data: Dict[str, Any]) -> List[Slide]:
        layout_map = {l['objectId']: l.get('layoutProperties', {}).get('predefinedLayout') for l in presentation_data.get('layouts', [])}
        simplified_slides = []
        for slide_data in presentation_data.get('slides', []):
            layout_id = slide_data.get('slideProperties', {}).get('layoutObjectId')
            predefined_layout = layout_map.get(layout_id)
            layout_name = self.REVERSE_LAYOUTS.get(predefined_layout, "CUSTOM")

            content = {"title": None, "subtitle": None, "body": None}
            for element in slide_data.get('pageElements', []):
                if 'shape' in element and 'placeholder' in element['shape']:
                    placeholder_type = element['shape']['placeholder']['type']
                    content_key = self.PLACEHOLDER_MAP.get(placeholder_type)
                    if content_key:
                        content[content_key] = self._extract_text(element['shape'])
            
            simplified_slides.append(Slide(slide_id=slide_data['objectId'], layout=layout_name, **content))
        return simplified_slides

    def _build_add_slide_requests(self, slide_id: str, layout_config: Dict[str, Any], payload: SlidePayload) -> List[Dict[str, Any]]:
        requests = [{"createSlide": {"objectId": slide_id, "slideLayoutReference": {"predefinedLayout": layout_config["predefined_layout"]}}}]
        
        # Handle styled text boxes
        if payload.texts:
            for text_payload in payload.texts:
                requests.extend(self._build_text_requests(slide_id, text_payload))

        # Handle tables
        if payload.tables:
            for table_payload in payload.tables:
                requests.extend(self._build_table_requests(slide_id, table_payload))

        return requests

    def _build_text_requests(self, slide_id: str, payload: TextPayload) -> List[Dict[str, Any]]:
        element_id = payload.element_id or f"text_box_{uuid.uuid4().hex}"
        requests = [
            {"createShape": {"objectId": element_id, "shapeType": "TEXT_BOX", "elementProperties": {"pageObjectId": slide_id}}},
            {"insertText": {"objectId": element_id, "text": payload.text}}
        ]
        if payload.style:
            style_req = self._build_text_style_request(element_id, payload.style)
            if style_req:
                requests.append(style_req)
        return requests

    def _build_table_requests(self, slide_id: str, payload: TablePayload) -> List[Dict[str, Any]]:
        element_id = payload.element_id or f"table_{uuid.uuid4().hex}"
        requests = [{"createTable": {"objectId": element_id, "elementProperties": {"pageObjectId": slide_id}, "rows": payload.rows, "columns": payload.columns}}]
        
        for r, row_data in enumerate(payload.data):
            for c, cell_text in enumerate(row_data):
                requests.append({"insertText": {"objectId": element_id, "cellLocation": {"rowIndex": r, "columnIndex": c}, "text": cell_text}})
        return requests

    def _build_text_style_request(self, element_id: str, style: TextStyle) -> Optional[Dict[str, Any]]:
        text_style = {}
        fields = []
        if style.font_family:
            text_style["fontFamily"] = style.font_family
            fields.append("fontFamily")
        if style.font_size:
            text_style["fontSize"] = {"magnitude": style.font_size, "unit": "PT"}
            fields.append("fontSize")
        if style.bold is not None:
            text_style["bold"] = style.bold
            fields.append("bold")
        if style.italic is not None:
            text_style["italic"] = style.italic
            fields.append("italic")
        if style.underline is not None:
            text_style["underline"] = style.underline
            fields.append("underline")
        if style.strikethrough is not None:
            text_style["strikethrough"] = style.strikethrough
            fields.append("strikethrough")
        if style.foreground_color:
            text_style["foregroundColor"] = {"opaqueColor": {"rgbColor": style.foreground_color.dict()}}
            fields.append("foregroundColor")

        if not text_style:
            return None

        return {"updateTextStyle": {"objectId": element_id, "textRange": {"type": "ALL"}, "style": text_style, "fields": ",".join(fields)}}

# --- API Router ---

router = APIRouter(
    prefix="/presentations",
    tags=["Presentations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PresentationInfo)
def create_presentation(
    payload: PresentationCreate, 
    service: PresentationService = Depends(PresentationService)
):
    """Create a new empty Google Slides presentation."""
    return service.create_presentation(payload.title)

@router.get("/{presentation_id}", response_model=Presentation)
def get_presentation(
    presentation_id: str, 
    service: PresentationService = Depends(PresentationService)
):
    """Get a Google Slides presentation by its ID in a simplified format."""
    return service.get_presentation(presentation_id)

@router.post("/{presentation_id}/slides", status_code=status.HTTP_201_CREATED, response_model=SlideCreationResponse)
def add_slide(
    presentation_id: str, 
    payload: SlidePayload, 
    service: PresentationService = Depends(PresentationService)
):
    """Add a new slide to an existing presentation."""
    return service.add_slide(presentation_id, payload)

@router.delete("/{presentation_id}/slides/{slide_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slide(
    presentation_id: str,
    slide_id: str,
    service: PresentationService = Depends(PresentationService)
):
    """Delete a slide from a presentation."""
    service.delete_slide(presentation_id, slide_id)
    return {} 