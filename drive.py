from fastapi import APIRouter, Depends, Request, HTTPException
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


@router.get("/drive/files")
async def list_drive_files(drive_service = Depends(get_drive_service)):
    try:
        results = drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])

        if not items:
            return {"message": "No files found."}
        else:
            return {"files": [item['name'] for item in items]}
    except HttpError as error:
        if error.resp.status == 401:
            return RedirectResponse(url='/login')
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")
