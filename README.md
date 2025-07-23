# Google Drive API - Documents Service

This document provides a comprehensive guide to using the Documents API, a service designed to create and manage Google Documents with rich text formatting.

## API Overview

The Documents API provides a set of RESTful endpoints for interacting with Google Documents. It allows you to:

- Create new, empty documents.
- Retrieve the content of existing documents in a simplified, easy-to-use format.
- Append richly formatted content to documents, including headings, styled text, and lists.

All endpoints are organized under the `/drive/documents` resource path and require session-based authentication.

---

## Endpoints

### 1. Create a Document

- **`POST /drive/documents`**

  Creates a new, empty Google Document with a specified title.

  **Request Body:**

  ```json
  {
    "title": "Your Document Title"
  }
  ```

  **Example `curl` Request:**

  ```bash
  curl -X POST "http://localhost:8000/drive/documents" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{
    "title": "My Awesome Document"
  }'
  ```

  **Successful Response (`201 Created`):**

  The API returns the ID and name of the newly created document.

  ```json
  {
    "id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
    "name": "My Awesome Document"
  }
  ```

### 2. Get a Document

- **`GET /drive/documents/{document_id}`**

  Retrieves the content of a specific Google Document in a simplified format.

  **Example `curl` Request:**

  ```bash
  curl -X GET "http://localhost:8000/drive/documents/<DOCUMENT_ID>" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>"
  ```

  **Successful Response (`200 OK`):**

  The API returns the document's ID, title, and a list of paragraphs.

  ```json
  {
    "document_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
    "title": "My Awesome Document",
    "content": [
      { "text": "This is the first paragraph." },
      { "text": "This is the second paragraph." }
    ]
  }
  ```

### 3. Append Styled Content

- **`POST /drive/documents/{document_id}:appendContent`**

  Appends a list of paragraphs with specified text and styles to an existing document. This is the most powerful feature of the Documents API, allowing you to create richly formatted content.

  **Request Body:**

  The request body is a JSON object containing a `content` key, which is a list of paragraph objects. Each paragraph object can have `text`, `paragraph_style`, and `text_style` properties.

  **Example `curl` Request:**

  ```bash
  curl -X POST "http://localhost:8000/drive/documents/<DOCUMENT_ID>:appendContent" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{
    "content": [
      {
        "text": "This is a Heading",
        "paragraph_style": { "namedStyleType": "HEADING_1" }
      },
      {
        "text": "This is a bold and red paragraph.",
        "text_style": {
          "bold": true,
          "foregroundColor": { "red": 1.0, "green": 0.0, "blue": 0.0 }
        }
      },
      {
        "text": "This is a bulleted list item.",
        "paragraph_style": { "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE" }
      }
    ]
  }'
  ```

  **Successful Response (`200 OK`):**

  ```json
  {
    "status": "success",
    "message": "Appended content to document <DOCUMENT_ID>"
  }
  ```

---

## Style Objects

### `paragraph_style`

| Key              | Type   | Description                                           |
| ---------------- | ------ | ----------------------------------------------------- |
| `namedStyleType` | string | The predefined paragraph style (e.g., `HEADING_1`).   |
| `bulletPreset`   | string | The predefined list style (e.g., `BULLET_DISC_CIRCLE_SQUARE`). |

### `text_style`

| Key               | Type   | Description                                    |
| ----------------- | ------ | ---------------------------------------------- |
| `bold`            | boolean| Whether the text is bold.                      |
| `italic`          | boolean| Whether the text is italic.                    |
| `underline`       | boolean| Whether the text is underlined.                |
| `foregroundColor` | object | The color of the text (see `Color` object). |

### `Color`

| Key     | Type   | Description                         |
| ------- | ------ | ----------------------------------- |
| `red`   | float  | The red component (0.0 to 1.0).   |
| `green` | float  | The green component (0.0 to 1.0). |
| `blue`  | float  | The blue component (0.0 to 1.0).  | 