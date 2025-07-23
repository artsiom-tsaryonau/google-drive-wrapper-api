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
|/drive/spreadsheets | POST | Create new spreedsheet based on payload |
|/drive/spreadsheets/{spreadsheet_id}| GET | Return a specific spreadsheet |
|/drive/spreadsheets/{spreadsheet_id}/sheets | POST | Creates new sheet within the existing spreadsheet |
|/drive/spreadsheets/{spreadsheet_id}/sheets/{name} | GET | Returns a specific sheet from the existing spreadsheet |

The Google Spreadsheet payload (and response) object should look like this
```
{
    "title": string,
    "sheets": [
        {
            "name": string
            "table": [
                [cell, cell],
                [cell, cell],
                [cell, cell]
            ]
            "rows": optional(int),
            "columns": optional(int)
        }
    ]
}
```
Later it will be extended with additional features like the ability to apply formatting on specific cell. The `table` represents the standard cell table in a corresponding sheet. When information about rows and columns is available (like when returning a sheet) it should be available in the response. 

When requesting or creating `sheet` object, the response (or payload) will look the same as items in "sheets" section.
```
{
    "name": string
    "table": [
        [cell, cell],
        [cell, cell],
        [cell, cell, cell]
    ]
    "rows": optional(int),
    "columns": optional(int)
}
```

## Google Docs API
    |
| **Slides**     | Create new presentation                            | POST   | /drive/slides                                                 |
|                | Get presentation                                   | GET    | /drive/slides/{presentation_id}                               |
|                | Add new slide to existing presentation             | POST   | /drive/{presentation_id}/slides                               |
|                | Delete slide                                       | DELETE | /drive/{presentation_id}/slides/{slide_id}                    |
| **Documents**  | Create new document                                | POST   | /drive/documents                                              |
|                | Get document                                       | GET    | /drive/{document_id}                                          |
|                | Append styled content to the document              | POST   | /drive/{document_id}:appendContent                            |
|                | Insert table into the document                     | POST   | /drive/{document_id}:insertTable                              |
|                | Add comment to the document                        | POST   | /drive/{document_id}/comments                                 |