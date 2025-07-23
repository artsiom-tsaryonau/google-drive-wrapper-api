# Google Docs API Wrapper

The goal is 

# Sample objects ids
document_id = 1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo
slides_id = 17rCbrfnQiFBWqHQCOJ5U7bug05C5XF9c4o4ptRrrOHY
spreadsheet_id = 1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY

{
    id: string
    name: string
    mimeType: string
    path: string
    parent_id: string
}


| API            | Action/Description                                 | Method | Endpoint                                                      |
|----------------|----------------------------------------------------|--------|---------------------------------------------------------------|
| **Drive**      | Search any object                                  | GET    | /drive/search?name=                                           |
|                | List content in a specific path                    | GET    | /drive/list/{path:path}                                       |
| **Spreadsheet**| Create new spreadsheet                             | POST   | /drive/spreadsheets                                           |
|                | Get spreadsheet                                    | GET    | /drive/spreadsheets/{spreadsheet_id}                          |
|                | Add new sheet to existing spreadsheet              | POST   | /drive/spreadsheets/{spreadsheet_id}/sheets                   |
|                | Append data to a specific sheet                    | POST   | /drive/{spreadsheet_id}/sheets/{sheet_name}:append            |
|                | Append data to a specific sheet with formatting    | POST   | /drive/{spreadsheet_id}/sheets/{sheet_name}:appendFormatted   |
|                | Clear a specific sheet                             | POST   | /drive/{spreadsheet_id}/sheets/{sheet_name}:clear             |
| **Slides**     | Create new presentation                            | POST   | /drive/slides                                                 |
|                | Get presentation                                   | GET    | /drive/slides/{presentation_id}                               |
|                | Add new slide to existing presentation             | POST   | /drive/{presentation_id}/slides                               |
|                | Delete slide                                       | DELETE | /drive/{presentation_id}/slides/{slide_id}                    |
| **Documents**  | Create new document                                | POST   | /drive/documents                                              |
|                | Get document                                       | GET    | /drive/{document_id}                                          |
|                | Append styled content to the document              | POST   | /drive/{document_id}:appendContent                            |
|                | Insert table into the document                     | POST   | /drive/{document_id}:insertTable                              |
|                | Add comment to the document                        | POST   | /drive/{document_id}/comments                                 |