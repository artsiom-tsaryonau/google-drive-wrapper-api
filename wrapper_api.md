# Google API Wrapper

The goal is implement a wrapper over a clunky Google Drive/Docs/Sheets/Slides API that Google provides. Later this API can be used to provide a frontend with a set of endpoints to implement a similar to those APIs functionality with a different UI.

| Type | ID | Description |
|------|----|-------------|
| document| 1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo | Simple sample google document |
| slide | 17rCbrfnQiFBWqHQCOJ5U7bug05C5XF9c4o4ptRrrOHY | Simple sample google slide |
| sheet | 1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY | Simple same google spreadsheet |
| parent | 1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7 | Parent id |

## Google Drive API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/search?name=&mimeType= | GET | Search Google Drive objects by name with optional mimeType |
| /drive/navigate/{path:path}?mimeType= | GET | List google drive content in a specific path with optional mimeType filter |
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
| /drive/spreadsheets?parent=&title= | POST | Create new empty spreadsheet, with optional parent id |
| /drive/spreadsheets/{spreadsheet_id}| GET | Return a spreadsheet by id |
| /drive/spreadsheets/{spreadsheet_id} | DELETE | Delete a spreadsheet by id |
| /drive/spreadsheets/{spreadsheet_id}/sheets | POST | Creates new empty sheet within the existing spreadsheet |
| /drive/spreadsheets/{spreadsheet_id}/sheets/{name} | GET | Returns a specific sheet from the existing spreadsheet |
| /drive/spreadsheets/{spreadsheet_id}/sheets/{name} | DELETE | Deletes a specific sheet from the spreadsheet |
| /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1= | GET | Returns the range based on A1 notation provided in range query parameter |
| /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1= | PUT | Updates the range based on A1 notation with payload containing the values and query parameter containing range. Requires either values or format to be provided. |
| /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1= | DELETE | Deletes a range from the sheet based on A1 |
Right now the payload and response should adhere to the google's specification for Sheet API.  

## Google Documents API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/documents?parent= | POST | Create new empty document, with optional parent id parameter |
| /drive/documents/{document_id}| GET | Return a specific document |
| /drive/documents/{document_id}/heading | PUT | Adds new heading (h1, h2 etc.) to the document |

Right now the payload and response should adhere to the google's specification for Docs API.

## Google Slides API

| Endpoint | Method | Description | 
|----------|-------|------------|
| /drive/slides?parent= | POST | Create new empty presentation, with optional parent id parameter |
| /drive/slides/{slides_id}| GET | Return a specific presentation |

Right now the payload and response should adhere to the google's specification for Slides API.
