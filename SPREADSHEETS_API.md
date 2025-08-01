# Google Spreadsheets API

This API provides a simplified wrapper over the Google Sheets API, allowing you to create, read, update, and delete spreadsheets and their contents via REST endpoints.

## Sample Spreadsheet
- **ID:** `1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY` - Simple sample google spreadsheet

## Endpoints

### Create a New Spreadsheet
```
POST /drive/spreadsheets?parent={parent_id}&title={title}
```
- **Description:** Create a new empty spreadsheet. Optionally specify a parent folder ID and title.
- **Parameters:**
  - `parent` (optional): Parent folder ID
  - `title` (required): Spreadsheet title
- **Sample Request:**
```
curl -X POST "http://localhost:8000/drive/spreadsheets?title=MySheet&parent=1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"
```
- **Sample Response:**
```json
{
  "spreadsheetId": "1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY",
  "properties": { "title": "MySheet" },
  ...
}
```

### Get a Spreadsheet by ID
```
GET /drive/spreadsheets/{spreadsheet_id}
```
- **Description:** Retrieve a spreadsheet by its ID.
- **Sample Request:**
```
curl "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY"
```
- **Sample Response:**
```json
{
  "spreadsheetId": "1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY",
  "sheets": [ ... ],
  ...
}
```

### Delete a Spreadsheet by ID
```
DELETE /drive/spreadsheets/{spreadsheet_id}
```
- **Description:** Delete a spreadsheet by its ID.
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY"
```
- **Sample Response:**
```json
{
  "message": "Spreadsheet 1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY deleted successfully"
}
```

### Add a New Sheet to a Spreadsheet
```
POST /drive/spreadsheets/{spreadsheet_id}/sheets
```
- **Description:** Add a new sheet to an existing spreadsheet.
- **Sample Request:**
```
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Sheet2"}' \
  "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets"
```
- **Sample Response:**
```json
{
  "replies": [ ... ],
  ...
}
```

### Get a Specific Sheet by Name
```
GET /drive/spreadsheets/{spreadsheet_id}/sheets/{name}
```
- **Description:** Retrieve a specific sheet from a spreadsheet by its name.
- **Sample Request:**
```
curl "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1"
```
- **Sample Response:**
```json
{
  "properties": {
    "sheetId": 0,
    "title": "Sheet1",
    ...
  },
  ...
}
```

### Delete a Sheet from a Spreadsheet
```
DELETE /drive/spreadsheets/{spreadsheet_id}/sheets/{name}
```
- **Description:** Delete a specific sheet from a spreadsheet by its name.
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet2"
```
- **Sample Response:**
```json
{
  "replies": [ ... ],
  ...
}
```

### Get a Range from a Sheet
```
GET /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1={A1_notation}
```
- **Description:** Retrieve values from a specific range in a sheet using A1 notation.
- **Sample Request:**
```
curl "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
```
- **Sample Response:**
```json
{
  "range": "Sheet1!A1:B2",
  "majorDimension": "ROWS",
  "values": [
    ["Name", "Score"],
    ["Alice", "95"]
  ]
}
```

### Update a Range in a Sheet
```
PUT /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1={A1_notation}
```
- **Description:** Update values and/or formatting in a specific range in a sheet using A1 notation. The request body must include at least one of `values` or `format`.
- **Sample Request (values and formatting):**
```
curl -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["Bold", "Red"]], "format": {"textFormat": {"bold": true}, "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8}}}' \
  "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B1"
```
- **Sample Request (values only):**
```
curl -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["New Value 1", "New Value 2"], ["New Value 3", "New Value 4"]]}' \
  "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
```
- **Sample Request (formatting only):**
```
curl -X PUT -H "Content-Type: application/json" \
  -d '{"format": {"backgroundColor": {"red": 1, "green": 1, "blue": 0.5}}}' \
  "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=B2:B3"
```
- **Sample Request Body:**
```json
{
  "values": [
    ["New Value 1", "New Value 2"],
    ["New Value 3", "New Value 4"]
  ],
  "format": {
    "textFormat": {"bold": true},
    "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8}
  }
}
```
- **Sample Response:**
```json
{
  "spreadsheetId": "1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY",
  "updatedRange": "Sheet1!A1:B2",
  "updatedRows": 2,
  "updatedColumns": 2,
  "updatedCells": 4
}
```

### Delete a Range from a Sheet
```
DELETE /drive/spreadsheets/{spreadsheet_id}/sheets/{name}/range?a1={A1_notation}
```
- **Description:** Delete (clear) a range from a sheet using A1 notation.
- **Sample Request:**
```
curl -X DELETE "http://localhost:8000/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
```
- **Sample Response:**
```json
{
  "replies": [ ... ],
  ...
}
```

---

## Notes
- All endpoints require authentication via Google API credentials.
- The API is a thin wrapper over the Google Sheets API; request and response formats closely follow the official Google API.
- Use the `a1` query parameter to specify ranges in A1 notation (e.g., `A1:B2`).
- For the PUT range endpoint, at least one of `values` or `format` must be provided in the request body.
- The `format` object follows the [Google Sheets API userEnteredFormat schema](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#CellFormat). 