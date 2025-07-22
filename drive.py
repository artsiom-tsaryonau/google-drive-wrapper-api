from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

router = APIRouter()

def get_credentials(request: Request) -> Credentials:
    if 'credentials' not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    
    creds_data = request.session['credentials']
    credentials = Credentials(**creds_data)

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(GoogleRequest())
        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    return credentials

def get_drive_service(credentials: Credentials = Depends(get_credentials)):
    return build('drive', 'v3', credentials=credentials)

@router.get("/drive/search")
async def search_drive(name: str = Query(None), drive_service=Depends(get_drive_service)):
    try:
        items = find_file_or_folder(drive_service, name)
        if not items:
            if name:
                raise HTTPException(status_code=404, detail=f"No file or folder found with name: {name}")
            else:
                return {"message": "No files or folders found in the root directory."}
        return {"results": items}
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")


def find_file_or_folder(drive_service, name):
    if name:
        query = f"name contains '{name}'"
    else:
        query = "'root' in parents"

    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, parents, mimeType)"
    ).execute()
    
    items = results.get('files', [])
    
    output = []
    for item in items:
        path = get_full_path(drive_service, item.get('parents', [])[0] if item.get('parents') else None)
        output.append({
            "id": item['id'],
            "name": item['name'],
            "type": "folder" if item['mimeType'] == 'application/vnd.google-apps.folder' else "file",
            "path": f"{path}/{item['name']}"
        })
        
    return output


def get_full_path(drive_service, folder_id):
    if not folder_id:
        return ""
    
    file = drive_service.files().get(fileId=folder_id, fields='id, name, parents').execute()
    parent = file.get('parents', [])[0] if file.get('parents') else None
    
    if parent:
        return get_full_path(drive_service, parent) + "/" + file.get('name', '')
    else:
        return file.get('name', '')


def get_folder_id_by_path(drive_service, folder_path):
    path_parts = folder_path.split('/')
    folder_id = 'root' 

    for part in path_parts:
        query = f"name='{part}' and mimeType='application/vnd.google-apps.folder' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            return None
        folder_id = items[0]['id']
    
    return folder_id