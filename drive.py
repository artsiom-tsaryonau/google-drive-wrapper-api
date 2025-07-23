from fastapi import APIRouter, Depends, Request, HTTPException, Query
from pydantic import BaseModel
from googleapiclient.errors import HttpError
from functools import lru_cache

from google_services import get_drive_service

router = APIRouter()

class DriveHelper:
    def __init__(self, drive_service):
        self.drive_service = drive_service

    @lru_cache(maxsize=None)
    def _get_path(self, folder_id):
        if not folder_id:
            return ""
        
        file = self.drive_service.files().get(fileId=folder_id, fields='id, name, parents').execute()
        parent = file.get('parents', [])[0] if file.get('parents') else None
        
        if parent:
            return self._get_path(parent) + "/" + file.get('name', '')
        else:
            return file.get('name', '')

    def get_folder_id_by_path(self, folder_path):
        path_parts = folder_path.split('/')
        folder_id = 'root'
        for part in path_parts:
            query = f"name='{part}' and mimeType='application/vnd.google-apps.folder' and '{folder_id}' in parents"
            results = self.drive_service.files().list(q=query, fields="files(id)").execute()
            items = results.get('files', [])
            
            if not items:
                return None
            folder_id = items[0]['id']
        
        return folder_id

    def list_files_in_folder(self, folder_id):
        query = f"'{folder_id}' in parents"
        results = self.drive_service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])

    def search(self, name):
        if name:
            query = f"name contains '{name}'"
        else:
            query = "'root' in parents"

        results = self.drive_service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, parents, mimeType)"
        ).execute()
        
        items = results.get('files', [])
        
        output = []
        for item in items:
            parent_id = item.get('parents', [])[0] if item.get('parents') else None
            path = self._get_path(parent_id)
            output.append({
                "id": item['id'],
                "name": item['name'],
                "mimeType": item.get('mimeType'),
                "path": f"{path}/{item['name']}" if path else item['name'] # additional line
            })
            
        return output

def get_drive_helper(drive_service=Depends(get_drive_service)):
    return DriveHelper(drive_service)

@router.get("/drive/list/{path:path}")
async def list_drive_path(path: str, helper: DriveHelper = Depends(get_drive_helper)):
    try:
        sanitized_path = path.strip('/')
        
        # Extract the folder name from the path
        folder_name = sanitized_path.split('/')[-1]
        search_results = helper.search(folder_name)
        
        # Find the specific folder that matches the full path
        target_folder = next((item for item in search_results if item['path'] == sanitized_path and item['mimeType'] == 'application/vnd.google-apps.folder'), None)
        
        if not target_folder:
            raise HTTPException(status_code=404, detail="Folder not found at the specified path")
            
        # List the contents of the found folder
        items = helper.list_files_in_folder(target_folder['id'])
        return {"files": items}
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")

@router.get("/drive/search")
async def search_drive(name: str = Query(None), helper: DriveHelper = Depends(get_drive_helper)):
    try:
        items = helper.search(name)
        if not items:
            if name:
                raise HTTPException(status_code=404, detail=f"No file or folder found with name: {name}")
            else:
                return {"message": "No files or folders found in the root directory."}
        return {"results": items}
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")