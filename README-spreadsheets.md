# Google Drive API - Spreadsheets Service

This document provides a comprehensive guide to using the Spreadsheets API, a service designed to create and manage Google Spreadsheets with rich text formatting.

## API Overview

The Spreadsheets API provides a set of RESTful endpoints for interacting with Google Spreadsheets. It allows you to:

- Create new, empty spreadsheets.
- Retrieve the content of existing spreadsheets, including all sheets and their values.
- Add new sheets to a spreadsheet.
- Append both simple and richly formatted data to sheets.
- Clear all data from a sheet.

All endpoints are organized under the `/drive/spreadsheets` resource path and require session-based authentication.

---

## Endpoints

### 1. Create a Spreadsheet

- **`POST /drive/spreadsheets`**

  Creates a new, empty Google Spreadsheet with a specified title.

  **Request Body:**

  ```json
  {
    "title": "Your Spreadsheet Title"
  }
  ```

  **Example `curl` Request:**

  ```bash
  curl -X POST "http://localhost:8000/drive/spreadsheets" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{
    "title": "My Awesome Spreadsheet"
  }'
  ```

  **Successful Response (`201 Created`):**

  ```json
  {
    "id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
    "name": "My Awesome Spreadsheet"
  }
  ```

### 2. Get a Spreadsheet

- **`GET /drive/spreadsheets/{spreadsheet_id}`**

  Retrieves the content of a specific Google Spreadsheet, including all sheets and their values.

  **Example `curl` Request:**

  ```bash
  curl -X GET "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>"
  ```

  **Successful Response (`200 OK`):**

  ```json
  {
    "spreadsheet_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
    "title": "My Awesome Spreadsheet",
    "sheets": [
      {
        "title": "Sheet1",
        "values": [["A1", "B1"], ["A2", "B2"]]
      }
    ]
  }
  ```

### 3. Add a Sheet

- **`POST /drive/spreadsheets/{spreadsheet_id}/sheets`**

  Adds a new sheet to an existing spreadsheet.

  **Request Body:**

  ```json
  {
    "title": "New Sheet Title"
  }
  ```

  **Example `curl` Request:**

  ```bash
  curl -X POST "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>/sheets" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<SESSION_COOKIE_VALUE>" \
  -d '{
    "title": "My New Sheet"
  }'
  ```

### 4. Append Data

- **`POST /drive/spreadsheets/{spreadsheet_id}/sheets/{sheet_name}:append`**

  Appends a list of rows to a specific sheet.

  **Request Body:**

  ```json
  {
    "values": [
      ["A1", "B1", "C1"],
      ["A2", "B2", "C2"]
    ]
  }
  ```

### 5. Append Formatted Data

- **`POST /drive/spreadsheets/{spreadsheet_id}/sheets/{sheet_name}:appendFormatted`**

  Appends data with cell-level formatting.

  **Request Body:**

  ```json
  {
    "values": [
      [
        { "value": "Red & Bold", "format": { "textFormat": { "foregroundColor": { "red": 1 }, "bold": true } } },
        { "value": "Green & Italic", "format": { "textFormat": { "foregroundColor": { "green": 1 }, "italic": true } } }
      ],
      [
        { "value": "Large Font", "format": { "textFormat": { "fontSize": 18 } } },
        { "value": "Strikethrough", "format": { "textFormat": { "strikethrough": true } } }
      ]
    ]
  }
  ```

### 6. Clear a Sheet

- **`POST /drive/spreadsheets/{spreadsheet_id}/sheets/{sheet_name}:clear`**

  Clears all data from a specific sheet.

---

## Style Objects

### `CellFormat`

| Key          | Type   | Description                               |
|--------------|--------|-------------------------------------------|
| `textFormat` | object | The text format of the cell (see `TextFormat` object). |

### `TextFormat`

| Key               | Type    | Description                               |
|-------------------|---------|-------------------------------------------|
| `foregroundColor` | object  | The color of the text (see `Color` object). |
| `fontFamily`      | string  | The font family of the text.              |
| `fontSize`        | integer | The font size of the text.                |
| `bold`            | boolean | Whether the text is bold.                 |
| `italic`          | boolean | Whether the text is italic.               |
| `strikethrough`   | boolean | Whether the text has a strikethrough.     |
| `underline`       | boolean | Whether the text is underlined.           |

### `Color`

| Key     | Type  | Description                       |
|---------|-------|-----------------------------------|
| `red`   | float | The red component (0.0 to 1.0).   |
| `green` | float | The green component (0.0 to 1.0). |
| `blue`  | float | The blue component (0.0 to 1.0).  | 