# Google Drive API

This API provides a simplified wrapper over the Google Drive API, allowing you to search, navigate, and manage files and folders via REST endpoints.

## Sample Data
- **Parent ID:** `1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7` - Parent folder ID for testing
- **Document ID:** `1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo` - Sample document for testing

## Endpoints

### Search Drive Objects
```
GET /drive/search?name={name}&mimeType={mimeType}
```
- **Description:** Search Google Drive objects by name with optional mimeType filter.
- **Parameters:**
  - `name` (optional): Name to search for (partial match)
  - `mimeType` (optional): Filter by MIME type (e.g., `application/vnd.google-apps.document`)
- **Sample Request:**
```
curl "http://localhost:8000/drive/search?name=Sample&mimeType=application/vnd.google-apps.document"
```
- **Sample Response:**
```json
[
  {
    "id": "1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo",
    "name": "Sample Document",
    "mimeType": "application/vnd.google-apps.document",
    "path": "/Sample Document",
    "parent_id": "1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"
  }
]
```

### Navigate Drive Path
```
GET /drive/navigate/{path:path}?mimeType={mimeType}
```
- **Description:** List Google Drive content in a specific path with optional mimeType filter.
- **Parameters:**
  - `path` (required): Path to navigate (e.g., `folder1/folder2`)
  - `mimeType` (optional): Filter by MIME type
- **Sample Request:**
```
curl "http://localhost:8000/drive/navigate/folder1/folder2?mimeType=application/vnd.google-apps.folder"
```
- **Sample Response:**
```json
[
  {
    "id": "1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7",
    "name": "Subfolder",
    "mimeType": "application/vnd.google-apps.folder",
    "path": "/folder1/folder2/Subfolder",
    "parent_id": "parent_folder_id"
  }
]
```

### Add Comment to File
```
POST /drive/{file_id}/comment
```
- **Description:** Add a new comment to a file. Supports both unanchored and anchored comments.
- **Parameters:**
  - `file_id` (required): The ID of the file to comment on
- **Request Body:**
```json
{
  "content": "This is a comment on the file",
  "anchor": {
    // Optional: For anchored comments
  }
}
```

#### Unanchored Comments
For general comments on the entire file:
```json
{
  "content": "This is a general comment on the file"
}
```

#### Anchored Comments for Google Docs
For comments on specific text:
```json
{
  "content": "This is a comment on specific text",
  "anchor": {
    "startIndex": 10,
    "endIndex": 20
  }
}
```

#### Anchored Comments for Google Sheets
For comments on specific cells:
```json
{
  "content": "This is a comment on a specific cell",
  "anchor": {
    "sheetId": "sheet_id_123",
    "rowIndex": 5,
    "columnIndex": 3
  }
}
```

- **Sample Request (Unanchored):**
```
curl -X POST "http://localhost:8000/drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a general comment on the file"}'
```

- **Sample Request (Anchored - Google Docs):**
```
curl -X POST "http://localhost:8000/drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a comment on specific text",
    "anchor": {
      "startIndex": 10,
      "endIndex": 20
    }
  }'
```

- **Sample Response:**
```json
{
  "kind": "drive#comment",
  "id": "comment_id_123",
  "createdTime": "2024-01-01T12:00:00.000Z",
  "modifiedTime": "2024-01-01T12:00:00.000Z",
  "author": {
    "kind": "drive#user",
    "displayName": "User Name",
    "photoLink": "https://lh3.googleusercontent.com/...",
    "me": true
  },
  "htmlContent": "This is a comment on the file",
  "content": "This is a comment on the file",
  "deleted": false,
  "resolved": false,
  "anchor": {
    "startIndex": 10,
    "endIndex": 20
  },
  "quotedFileContent": {
    "mimeType": "application/vnd.google-apps.document",
    "value": "quoted content"
  }
}
```

### Delete Comment
```
DELETE /drive/{file_id}/comment/{comment_id}
```
- **Description:** Delete a comment from a file.
- **Parameters:**
  - `file_id` (required): The ID of the file
  - `comment_id` (required): The ID of the comment to delete
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123"
```
- **Sample Response:**
```json
{
  "message": "Comment comment_id_123 deleted successfully"
}
```

### Add Reply to Comment
```
POST /drive/{file_id}/comment/{comment_id}/reply
```
- **Description:** Add a reply to a comment.
- **Parameters:**
  - `file_id` (required): The ID of the file
  - `comment_id` (required): The ID of the comment to reply to
- **Request Body:**
```json
{
  "content": "This is a reply to the comment"
}
```
- **Sample Request:**
```
curl -X POST "http://localhost:8000/drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123/reply" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a reply to the comment"}'
```
- **Sample Response:**
```json
{
  "kind": "drive#reply",
  "id": "reply_id_456",
  "createdTime": "2024-01-01T12:30:00.000Z",
  "modifiedTime": "2024-01-01T12:30:00.000Z",
  "author": {
    "kind": "drive#user",
    "displayName": "User Name",
    "photoLink": "https://lh3.googleusercontent.com/...",
    "me": true
  },
  "htmlContent": "This is a reply to the comment",
  "content": "This is a reply to the comment",
  "deleted": false
}
```

### Resolve Comment
```
POST /drive/{file_id}/comment/{comment_id}/resolve
```
- **Description:** Resolve a comment (mark it as resolved).
- **Parameters:**
  - `file_id` (required): The ID of the file
  - `comment_id` (required): The ID of the comment to resolve
- **Sample Request:**
```
curl -X POST "http://localhost:8000/drive/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/comment/comment_id_123/resolve"
```
- **Sample Response:**
```json
{
  "kind": "drive#comment",
  "id": "comment_id_123",
  "createdTime": "2024-01-01T12:00:00.000Z",
  "modifiedTime": "2024-01-01T12:45:00.000Z",
  "author": {
    "kind": "drive#user",
    "displayName": "User Name",
    "photoLink": "https://lh3.googleusercontent.com/...",
    "me": true
  },
  "htmlContent": "This is a comment on the file",
  "content": "This is a comment on the file",
  "deleted": false,
  "resolved": true,
  "anchor": {
    "startIndex": 10,
    "endIndex": 20
  },
  "quotedFileContent": {
    "mimeType": "application/vnd.google-apps.document",
    "value": "quoted content"
  }
}
```

### Delete Drive Object
```
DELETE /drive/{id}
```
- **Description:** Delete an object by ID from Google Drive.
- **Parameters:**
  - `id` (required): The ID of the file or folder to delete
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/your_file_or_folder_id_here"
```
- **Sample Response:**
```
HTTP 204 No Content
```

## Drive Object Structure

All search and navigation endpoints return objects with the following structure:

```json
{
  "id": "string",
  "name": "string", 
  "mimeType": "string",
  "path": "string",
  "parent_id": "string"
}
```

- **id**: Unique identifier for the file/folder
- **name**: Display name of the file/folder
- **mimeType**: MIME type indicating the file type
- **path**: Full path from root to the object
- **parent_id**: ID of the parent folder (null for root-level items)

## Common MIME Types

| MIME Type | Description |
|-----------|-------------|
| `application/vnd.google-apps.folder` | Google Drive folder |
| `application/vnd.google-apps.document` | Google Docs document |
| `application/vnd.google-apps.spreadsheet` | Google Sheets spreadsheet |
| `application/vnd.google-apps.presentation` | Google Slides presentation |
| `application/vnd.google-apps.drawing` | Google Drawings |
| `application/vnd.google-apps.form` | Google Forms |
| `text/plain` | Plain text file |
| `application/pdf` | PDF file |
| `image/jpeg` | JPEG image |
| `image/png` | PNG image |

## Anchor Comment Formats

### Google Docs Anchors
For comments on specific text in Google Docs:
```json
{
  "anchor": {
    "startIndex": 10,  // Start position of the text
    "endIndex": 20     // End position of the text
  }
}
```

### Google Sheets Anchors
For comments on specific cells in Google Sheets:
```json
{
  "anchor": {
    "sheetId": "sheet_id_123",  // ID of the sheet
    "rowIndex": 5,              // Row index (0-based)
    "columnIndex": 3            // Column index (0-based)
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK**: Successful operation
- **204 No Content**: Successful deletion
- **400 Bad Request**: Invalid parameters or anchor format
- **403 Forbidden**: Permission denied
- **404 Not Found**: File or folder not found
- **500 Internal Server Error**: Google API error

## Notes

- All endpoints require authentication via Google API credentials
- The API is a thin wrapper over the Google Drive API
- Search operations use partial name matching
- Navigation operations traverse the folder hierarchy step by step
- Comments can be unanchored (general file comments) or anchored (tied to specific content)
- Anchored comments are supported for Google Docs and Google Sheets
- Comment replies are threaded under the parent comment
- Resolved comments are marked as resolved but not deleted
- The `path` field is constructed by the API and represents the full path from root
- Parent ID is extracted from the first parent in the parents array (Google Drive supports multiple parents)
- Anchor parameters must match the file type (Docs vs Sheets have different anchor formats) 