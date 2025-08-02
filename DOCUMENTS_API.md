# Google Docs API Wrapper

This document describes the Google Docs API wrapper endpoints. It also supports basic document management operations.

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require Google API credentials. The API uses OAuth 2.0 authentication.

## Document Management Endpoints

### Create a Document
```
POST /drive/documents
```
- **Description:** Create a new empty document with an optional parent folder.
- **Parameters:**
  - `title` (required): The title of the document
  - `parent` (optional): The ID of the parent folder where the document should be created
- **Sample Request:**
```
curl -X POST "http://localhost:8000/drive/documents?title=MyDocument&parent=1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"
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
        "paragraph": {
          "elements": []
        }
      }
    ]
  }
}
```

### Get a Document
```
GET /drive/documents/{document_id}
```
- **Description:** Retrieve a document by its ID.
- **Parameters:**
  - `document_id` (required): The ID of the document
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
        "paragraph": {
          "elements": []
        }
      }
    ]
  }
}
```

### Delete a Document
```
DELETE /drive/documents/{document_id}
```
- **Description:** Delete a document by its ID.
- **Parameters:**
  - `document_id` (required): The ID of the document to delete
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