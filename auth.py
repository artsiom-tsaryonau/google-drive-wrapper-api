from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from config import settings

router = APIRouter()

@router.get("/login")
async def login():
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRETS_FILE, scopes=settings.SCOPES, redirect_uri=settings.REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(request: Request):
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRETS_FILE, scopes=settings.SCOPES, redirect_uri=settings.REDIRECT_URI
    )
    
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return RedirectResponse(url='/drive/files')
