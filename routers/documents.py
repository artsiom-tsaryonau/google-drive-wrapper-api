from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from google_services import get_drive_service, get_docs_service

# --- Pydantic Models ---

class DocumentCreate(BaseModel):
    title: str

class DocumentInfo(BaseModel):
    id: str
    name: str

class Paragraph(BaseModel):
    text: str

class Document(BaseModel):
    document_id: str
    title: str
    content: List[Paragraph]

class Color(BaseModel):
    red: float = Field(..., ge=0, le=1)
    green: float = Field(..., ge=0, le=1)
    blue: float = Field(..., ge=0, le=1)

class Dimension(BaseModel):
    magnitude: float
    unit: str = "PT"

class WeightedFontFamily(BaseModel):
    font_family: str
    weight: int = Field(400, ge=100, le=900)

class TextStyle(BaseModel):
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    foregroundColor: Optional[Color] = None
    font_size: Optional[Dimension] = None
    weighted_font_family: Optional[WeightedFontFamily] = None

class ParagraphStyle(BaseModel):
    namedStyleType: Optional[str] = Field(None, description="e.g., 'HEADING_1', 'TITLE'")
    bulletPreset: Optional[str] = Field(None, description="e.g., 'BULLET_DISC_CIRCLE_SQUARE'")

class ParagraphPayload(BaseModel):
    text: str
    paragraph_style: Optional[ParagraphStyle] = None
    text_style: Optional[TextStyle] = None

class AppendContentPayload(BaseModel):
    content: List[ParagraphPayload]

class TablePayload(BaseModel):
    rows: int = Field(..., gt=0)
    columns: int = Field(..., gt=0)
    data: List[List[str]]

class CommentPayload(BaseModel):
    text: str
    start_index: int
    end_index: int


# --- Service Class for Business Logic ---

class DocumentService:
    def __init__(self, drive_service: Resource = Depends(get_drive_service), docs_service: Resource = Depends(get_docs_service)):
        self.drive_service = drive_service
        self.docs_service = docs_service

    def create_document(self, title: str) -> Dict[str, Any]:
        try:
            metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
            file = self.drive_service.files().create(body=metadata, fields='id, name').execute()
            return file
        except HttpError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating document: {e}")

    def get_document(self, document_id: str) -> Document:
        try:
            self._verify_is_document(document_id)
            doc_data = self.docs_service.documents().get(documentId=document_id).execute()
            content = self._simplify_content(doc_data.get('body', {}).get('content', []))
            return Document(document_id=doc_data['documentId'], title=doc_data['title'], content=content)
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document '{document_id}' not found.")
            raise HTTPException(e.resp.status, f"Error fetching document: {e}")

    def append_content(self, document_id: str, payload: AppendContentPayload) -> Dict[str, str]:
        try:
            self._verify_is_document(document_id)
            doc = self.docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
            start_index = doc.get('body', {}).get('content', [])[-1].get('endIndex', 1) - 1

            requests = self._build_append_requests(payload, start_index)
            
            if requests:
                self.docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            
            return {"status": "success", "message": f"Appended content to document {document_id}"}
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document '{document_id}' not found.")
            raise HTTPException(e.resp.status, f"Error appending content: {e}")

    def insert_table(self, document_id: str, payload: TablePayload) -> Dict[str, str]:
        try:
            self._verify_is_document(document_id)
            doc = self.docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
            start_index = doc.get('body', {}).get('content', [])[-1].get('endIndex', 1) - 1

            requests = self._build_table_requests(payload, start_index)
            
            if requests:
                self.docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            
            return {"status": "success", "message": f"Inserted table into document {document_id}"}
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document '{document_id}' not found.")
            raise HTTPException(e.resp.status, f"Error inserting table: {e}")

    def add_comment(self, document_id: str, payload: CommentPayload) -> Dict[str, Any]:
        try:
            self._verify_is_document(document_id)
            
            # The anchor format is specific to the Drive API for comments.
            anchor = f"{{'line': {{'n': {payload.start_index}, 'l': {payload.end_index - payload.start_index}}}}}"
            
            comment = {
                'content': payload.text,
                'anchor': anchor
            }
            
            # Use drive_service to create the comment
            comment_result = self.drive_service.comments().create(
                fileId=document_id,
                body=comment,
                fields='id,content,author'
            ).execute()
            
            return comment_result
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document '{document_id}' not found.")
            raise HTTPException(e.resp.status, f"Error adding comment: {e}")

    def _build_table_requests(self, payload: TablePayload, start_index: int) -> List[Dict[str, Any]]:
        requests = [
            {'insertTable': {
                'location': {'index': start_index},
                'rows': payload.rows,
                'columns': payload.columns
            }}
        ]
        
        # Table content insertion starts at `start_index + 2` because of the table start element and newline
        cell_start_index = start_index + 4
        for r, row_data in enumerate(payload.data):
            for c, cell_text in enumerate(row_data):
                if cell_text:
                    requests.append({
                        'insertText': {
                            'location': {'index': cell_start_index},
                            'text': cell_text
                        }
                    })
                # Move to the next cell. Each cell takes up 2 indices (start and end).
                cell_start_index += 2
            # Each row also has an end element
            cell_start_index += 2


        return requests

    def _build_append_requests(self, payload: AppendContentPayload, start_index: int) -> List[Dict[str, Any]]:
        requests = []
        current_index = start_index
        for para in payload.content:
            text_to_insert = para.text + '\n'
            text_len = len(text_to_insert)
            
            requests.append({'insertText': {'location': {'index': current_index}, 'text': text_to_insert}})
            
            paragraph_range = {'startIndex': current_index, 'endIndex': current_index + text_len}
            text_range = {'startIndex': current_index, 'endIndex': current_index + text_len -1} # Exclude newline for text style
            
            if para.paragraph_style:
                if para.paragraph_style.namedStyleType:
                    requests.append({'updateParagraphStyle': {
                        'range': paragraph_range,
                        'paragraphStyle': {'namedStyleType': para.paragraph_style.namedStyleType},
                        'fields': 'namedStyleType'
                    }})
                if para.paragraph_style.bulletPreset:
                    requests.append({'createParagraphBullets': {
                        'range': paragraph_range,
                        'bulletPreset': para.paragraph_style.bulletPreset
                    }})
            
            if para.text_style:
                style_request = {'updateTextStyle': {'range': text_range, 'textStyle': {}, 'fields': ''}}
                ts_fields = []
                if para.text_style.bold is not None:
                    style_request['updateTextStyle']['textStyle']['bold'] = para.text_style.bold
                    ts_fields.append('bold')
                if para.text_style.italic is not None:
                    style_request['updateTextStyle']['textStyle']['italic'] = para.text_style.italic
                    ts_fields.append('italic')
                if para.text_style.underline is not None:
                    style_request['updateTextStyle']['textStyle']['underline'] = para.text_style.underline
                    ts_fields.append('underline')
                if para.text_style.strikethrough is not None:
                    style_request['updateTextStyle']['textStyle']['strikethrough'] = para.text_style.strikethrough
                    ts_fields.append('strikethrough')
                if para.text_style.foregroundColor:
                    style_request['updateTextStyle']['textStyle']['foregroundColor'] = {
                        'color': {'rgbColor': para.text_style.foregroundColor.dict()}
                    }
                    ts_fields.append('foregroundColor')
                if para.text_style.font_size:
                    style_request['updateTextStyle']['textStyle']['fontSize'] = para.text_style.font_size.dict()
                    ts_fields.append('fontSize')
                if para.text_style.weighted_font_family:
                    style_request['updateTextStyle']['textStyle']['weightedFontFamily'] = {
                        'fontFamily': para.text_style.weighted_font_family.font_family,
                        'weight': para.text_style.weighted_font_family.weight
                    }
                    ts_fields.append('weightedFontFamily')

                if ts_fields:
                    style_request['updateTextStyle']['fields'] = ','.join(ts_fields)
                    requests.append(style_request)

            current_index += text_len
        return requests

    def _verify_is_document(self, file_id: str):
        metadata = self.drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if metadata.get('mimeType') != 'application/vnd.google-apps.document':
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is not a Google Document.")

    def _simplify_content(self, content_elements: List[Dict[str, Any]]) -> List[Paragraph]:
        simplified_content = []
        for element in content_elements:
            if 'paragraph' in element:
                text = "".join(
                    pe.get('textRun', {}).get('content', '') for pe in element['paragraph'].get('elements', [])
                ).strip()
                if text:
                    simplified_content.append(Paragraph(text=text))
        return simplified_content

# --- API Router ---

router = APIRouter(
    prefix="/drive/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DocumentInfo)
def create_document(payload: DocumentCreate, service: DocumentService = Depends(DocumentService)):
    """Create a new empty Google Document."""
    return service.create_document(payload.title)

@router.get("/{document_id}", response_model=Document)
def get_document(document_id: str, service: DocumentService = Depends(DocumentService)):
    """Get a Google Document by its ID in a simplified format."""
    return service.get_document(document_id)

@router.post("/{document_id}:appendContent", status_code=status.HTTP_200_OK)
def append_content(document_id: str, payload: AppendContentPayload, service: DocumentService = Depends(DocumentService)):
    """Append styled content to an existing Google Document."""
    return service.append_content(document_id, payload)

@router.post("/{document_id}:insertTable", status_code=status.HTTP_200_OK)
def insert_table(document_id: str, payload: TablePayload, service: DocumentService = Depends(DocumentService)):
    """Insert a table into an existing Google Document."""
    return service.insert_table(document_id, payload)

@router.post("/{document_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(document_id: str, payload: CommentPayload, service: DocumentService = Depends(DocumentService)):
    """Add a comment to a specific text range in a Google Document."""
    return service.add_comment(document_id, payload) 