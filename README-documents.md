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

### 4. Insert a Table

- **`POST /drive/documents/{document_id}:insertTable`**

  Inserts a table with specified dimensions and data into an existing document.

  **Request Body:**

  The request body is a JSON object that defines the structure of the table.

  ```json
  {
    "rows": 3,
    "columns": 3,
    "data": [
      ["A1", "B1", "C1"],
      ["A2", "B2", "C2"],
      ["A3", "B3", "C3"]
    ]
  }
  ```

  **Example `curl` Request:**

  ```bash
  curl -X POST "http://localhost:8000/drive/documents/<DOCUMENT_ID>:insertTable" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{
    "rows": 3,
    "columns": 3,
    "data": [
      ["Header 1", "Header 2", "Header 3"],
      ["Data 1", "Data 2", "Data 3"],
      ["Data 4", "Data 5", "Data 6"]
    ]
  }'
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
| `strikethrough`   | boolean| Whether the text has a strikethrough.          |
| `foregroundColor` | object | The color of the text (see `Color` object).    |
| `font_size`       | object | The font size (see `Dimension` object).        |
| `weighted_font_family` | object | The font family and weight (see `WeightedFontFamily` object). |

### `Color`

| Key     | Type   | Description                         |
| ------- | ------ | ----------------------------------- |
| `red`   | float  | The red component (0.0 to 1.0).   |
| `green` | float  | The green component (0.0 to 1.0). |
| `blue`  | float  | The blue component (0.0 to 1.0).  |

### `Dimension`

| Key         | Type   | Description                             |
| ----------- | ------ | --------------------------------------- |
| `magnitude` | float  | The numerical value of the dimension.   |
| `unit`      | string | The unit of measurement (default: `PT`). |

### `WeightedFontFamily`

| Key           | Type   | Description                                     |
| ------------- | ------ | ----------------------------------------------- |
| `font_family` | string | The name of the font family (e.g., `Arial`).    |
| `weight`      | integer| The font weight (100-900, default: `400`).      |

---

## Advanced Text Styling Example

Here's an example that demonstrates how to use the new advanced text styling features:

```bash
curl -X POST "http://localhost:8000/drive/documents/<DOCUMENT_ID>:appendContent" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "content": [
    {
      "text": "This text is 24pt, Arial, and bold.",
      "text_style": {
        "font_size": { "magnitude": 24, "unit": "PT" },
        "weighted_font_family": { "font_family": "Arial", "weight": 700 },
        "bold": true
      }
    },
    {
      "text": "This text has a strikethrough.",
      "text_style": {
        "strikethrough": true
      }
    }
  ]
}'
```

---

## Supported `namedStyleType` Values

The following are the supported values for the `namedStyleType` property:

- `NORMAL_TEXT`
- `TITLE`
- `SUBTITLE`
- `HEADING_1`
- `HEADING_2`
- `HEADING_3`
- `HEADING_4`
- `HEADING_5`
- `HEADING_6`

---

## Supported `bulletPreset` Values

The following are the supported values for the `bulletPreset` property:

- `BULLET_DISC_CIRCLE_SQUARE`
- `BULLET_DIAMONDX_ARROW3D_SQUARE`
- `BULLET_CHECKBOX`
- `BULLET_ARROW_DIAMOND_DISC`
- `BULLET_STAR_CIRCLE_SQUARE`
- `BULLET_ARROW3D_CIRCLE_SQUARE`
- `BULLET_LEFTTRIANGLE_DIAMOND_DISC`
- `BULLET_DIAMONDX_HOLLOWDIAMOND_SQUARE`
- `BULLET_DIAMOND_CIRCLE_SQUARE`
- `NUMBERED_DECIMAL_ALPHA_ROMAN`
- `NUMBERED_DECIMAL_ALPHA_ROMAN_PARENS`
- `NUMBERED_DECIMAL_NESTED`
- `NUMBERED_UPPERALPHA_ALPHA_ROMAN`
- `NUMBERED_UPPERROMAN_UPPERALPHA_DECIMAL`
- `NUMBERED_ZERODECIMAL_ALPHA_ROMAN` 