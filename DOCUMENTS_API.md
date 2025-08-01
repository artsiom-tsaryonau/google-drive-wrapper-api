# Google Documents API

This API provides a simplified wrapper over the Google Docs API, allowing you to create, read, and delete documents via REST endpoints.

## Sample Document
- **ID:** `1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo` - Simple sample google document

## Endpoints

### Create a New Document
```
POST /drive/documents?parent={parent_id}&title={title}
```
- **Description:** Create a new empty document. Optionally specify a parent folder ID and title.
- **Parameters:**
  - `parent` (optional): Parent folder ID
  - `title` (required): Document title
- **Sample Request:**
```
curl -X POST "http://localhost:8000/drive/documents?title=MyDocument&parent=1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"
```
- **Sample Response:**
```json
{
  "documentId": "1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo",
  "title": "MyDocument",
  ...
}
```

### Get a Document by ID
```
GET /drive/documents/{document_id}
```
- **Description:** Retrieve a document by its ID.
- **Sample Request:**
```
curl "http://localhost:8000/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"
```
- **Sample Response:**
```json
{
  "documentId": "1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo",
  "title": "MyDocument",
  "body": {
    "content": [
      {
        "endIndex": 1,
        "sectionBreak": {
          "sectionStyle": {
            "columnSeparatorStyle": "NONE",
            "contentDirection": "LEFT_TO_RIGHT",
            "sectionType": "CONTINUOUS"
          }
        }
      }
    ]
  },
  ...
}
```

### Delete a Document by ID
```
DELETE /drive/documents/{document_id}
```
- **Description:** Delete a document by its ID.
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"
```
- **Sample Response:**
```json
{
  "message": "Document 1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo deleted successfully"
}
```

---

## Notes
- All endpoints require authentication via Google API credentials.
- The API is a thin wrapper over the Google Docs API; request and response formats closely follow the official Google API.
- Document creation uses the Google Docs API, while deletion uses the Google Drive API (since documents are stored as files in Drive).
- The `parent` parameter is optional and allows you to specify a folder where the document should be created.
- Document IDs are returned in the `documentId` field when creating documents. 