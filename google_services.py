from fastapi import Depends, HTTPException, Request
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build

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

def get_docs_service(credentials: Credentials = Depends(get_credentials)):
    return build('docs', 'v1', credentials=credentials)

def get_sheets_service(credentials: Credentials = Depends(get_credentials)):
    return build('sheets', 'v4', credentials=credentials)

def get_slides_service(credentials: Credentials = Depends(get_credentials)):
    return build('slides', 'v1', credentials=credentials) 