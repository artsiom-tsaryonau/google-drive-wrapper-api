# Google API Wrapper

The goal is implement a wrapper over a clunky Google Drive/Docs/Sheets/Slides API that Google provides. Later this API can be used to provide a frontend with a set of endpoints to implement a similar to those APIs functionality with a different UI.

| Type | ID | Description |
|------|----|-------------|
| document| 1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo | Simple sample google document |
| slide | 17rCbrfnQiFBWqHQCOJ5U7bug05C5XF9c4o4ptRrrOHY | Simple sample google slide |
| sheet | 1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY | Simple same google spreadsheet |

## Google Drive API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/search?name=&mimeType= | GET | Search Google Drive objects by name with optional mimeType |
| /drive/{path:path}?mimeType= | GET | List google drive content in a specific path with optional mimeType filter |
| /drive/{id} | DELETE | Deletes and object by id from the Google Drive |

The Google Drive object information should look like this
```
{
    id: string
    name: string
    mimeType: string
    path: string
    parent_id: string
}
```
With `path` being a full path from the root to the object and parent_id. List and search functions return a list of objects, containing zero, one or more objects.

## Google Spreadsheets API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/spreadsheets | POST | Create new empty spreadsheet |
| /drive/spreadsheets/{spreadsheet_id}| GET | Return a spreadsheet by id |
| /drive/spreadsheets/{spreadsheet_id}/sheets | POST | Creates new empty sheet within the existing spreadsheet |
| /drive/spreadsheets/{spreadsheet_id}/sheets/{name} | GET | Returns a specific sheet from the existing spreadsheet |

Right now the payload and response should adhere to the google's specification for Sheet API.  

## Google Docs API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/document | POST | Create new empty presentation |
| /drive/document/{document_id}| GET | Return a specific document |

Right now the payload and response should adhere to the google's specification for Docs API.

## Google Slides API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/slides | POST | Create new empty presentation |
| /drive/slides/{slides_id}| GET | Return a specific presentation |

Right now the payload and response should adhere to the google's specification for Slides API.
