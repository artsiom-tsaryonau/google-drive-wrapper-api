from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
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

class AppendTextPayload(BaseModel):
    text: str

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
            
            return Document(
                document_id=doc_data['documentId'],
                title=doc_data['title'],
                content=content
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document '{document_id}' not found.")
            raise HTTPException(e.resp.status, f"Error fetching document: {e}")

    def append_text(self, document_id: str, text: str) -> Dict[str, str]:
        try:
            self._verify_is_document(document_id)
            doc = self.docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
            end_index = doc.get('body', {}).get('content', [])[-1].get('endIndex', 1)
            
            requests = [{'insertText': {'location': {'index': end_index - 1}, 'text': text}}]
            self.docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            return {"status": "success", "message": f"Appended text to document {document_id}"}
        except HttpError as e:
            if e.resp.status == 404:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Document '{document_id}' not found.")
            raise HTTPException(e.resp.status, f"Error appending to document: {e}")

    def _verify_is_document(self, file_id: str):
        metadata = self.drive_service.files().get(fileId=file_id, fields='mimeType').execute()
        if metadata.get('mimeType') != 'application/vnd.google-apps.document':
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is not a Google Document.")

    def _simplify_content(self, content_elements: List[Dict[str, Any]]) -> List[Paragraph]:
        simplified_content = []
        for element in content_elements:
            if 'paragraph' in element:
                text_runs = [
                    run.get('content', '')
                    for pe in element['paragraph'].get('elements', [])
                    if 'textRun' in pe
                ]
                text = "".join(text_runs).strip()
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
def create_document(
    payload: DocumentCreate,
    service: DocumentService = Depends(DocumentService)
):
    """Create a new empty Google Document."""
    return service.create_document(payload.title)

@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: str,
    service: DocumentService = Depends(DocumentService)
):
    """Get a Google Document by its ID in a simplified format."""
    return service.get_document(document_id)

@router.post("/{document_id}:append", status_code=status.HTTP_200_OK)
def append_to_document(
    document_id: str,
    payload: AppendTextPayload,
    service: DocumentService = Depends(DocumentService)
):
    """Append text to an existing Google Document."""
    return service.append_text(document_id, payload.text) 