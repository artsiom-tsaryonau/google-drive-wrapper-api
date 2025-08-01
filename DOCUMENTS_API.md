# Google Documents API

This API provides a simplified wrapper over the Google Docs API, allowing you to create, read, and delete documents via REST endpoints. It also supports managing tabs within documents.

## Sample Document
- **ID:** `1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo` - Simple sample google document

## Document Endpoints

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

## Tab Management Endpoints

Google Docs supports tabs (similar to spreadsheet sheets) for organizing content within a single document. These endpoints allow you to manage tabs within documents.

### Create a New Tab
```
POST /drive/documents/{document_id}/tabs/{name}
```
- **Description:** Create a new empty tab within an existing document.
- **Parameters:**
  - `document_id` (required): The ID of the document
  - `name` (required): The name/title of the new tab
- **Sample Request:**
```
curl -X POST "http://localhost:8000/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/tabs/NewTab"
```
- **Sample Response:**
```json
{
  "replies": [
    {
      "insertTab": {
        "tab": {
          "tabProperties": {
            "tabId": "tab_id_123",
            "title": "NewTab"
          }
        }
      }
    }
  ],
  "writeControl": {
    "requiredRevisionId": "revision_id"
  }
}
```

### Get Tab Content
```
GET /drive/documents/{document_id}/tabs/{name}
```
- **Description:** Retrieve the content of a specific tab from a document.
- **Parameters:**
  - `document_id` (required): The ID of the document
  - `name` (required): The name/title of the tab
- **Sample Request:**
```
curl "http://localhost:8000/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/tabs/NewTab"
```
- **Sample Response:**
```json
{
  "tabProperties": {
    "tabId": "tab_id_123",
    "title": "NewTab"
  },
  "documentTab": {
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
    }
  }
}
```

### Delete a Tab
```
DELETE /drive/documents/{document_id}/tabs/{name}
```
- **Description:** Delete a specific tab and its content from a document.
- **Parameters:**
  - `document_id` (required): The ID of the document
  - `name` (required): The name/title of the tab to delete
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/tabs/NewTab"
```
- **Sample Response:**
```json
{
  "replies": [
    {
      "deleteTab": {}
    }
  ],
  "writeControl": {
    "requiredRevisionId": "revision_id"
  }
}
```

---

## Notes
- All endpoints require authentication via Google API credentials.
- The API is a thin wrapper over the Google Docs API; request and response formats closely follow the official Google API.
- Document creation uses the Google Docs API, while deletion uses the Google Drive API (since documents are stored as files in Drive).
- The `parent` parameter is optional and allows you to specify a folder where the document should be created.
- Document IDs are returned in the `documentId` field when creating documents.
- Tab operations use the Google Docs API's `batchUpdate` method with `includeTabsContent=True` for retrieving tab information.
- Tab names are case-sensitive and must match exactly when retrieving or deleting tabs.
- When a document has multiple tabs, the first tab is typically the default tab that contains the main document content. 