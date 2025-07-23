#!/bin/bash

# A collection of example cURL requests for the Google Drive API.
#
# -----------------------------------------------------------------------------
# IMPORTANT: AUTHENTICATION
# -----------------------------------------------------------------------------
# This API uses session-based authentication. To use these cURL commands,
# you must first authenticate with the application in your web browser by
# visiting http://localhost:8000/auth/google.
#
# After authenticating, you need to get the session cookie from your browser's
# developer tools. Look for a cookie named "session" for the domain
# localhost.
#
# You will need to replace the following placeholders in the commands below:
#   - <SESSION_COOKIE_VALUE>
#   - <PRESENTATION_ID>
#   - <DOCUMENT_ID>
#   - <SPREADSHEET_ID>
#   - <SHEET_NAME>
#
# Note: These examples assume the server is running on http://localhost:8000.

echo "--- Presentations API ---"

# 1. Create a new Google Slides presentation
echo "Creating a new Google Slides presentation..."
curl -X POST "http://localhost:8000/drive/presentations" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "title": "My New Presentation"
}'
echo -e "\\n"

# 2. Add a slide with rich content to a presentation
echo "Adding a slide with rich content (replace <PRESENTATION_ID>)..."
curl -X POST "http://localhost:8000/drive/presentations/<PRESENTATION_ID>/slides" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "layout": "TITLE_AND_BODY",
  "title": "Rich Content Slide",
  "texts": [
    {
      "text": "Styled Text",
      "style": {
        "font_size": 24,
        "bold": true,
        "foreground_color": {"red": 1}
      }
    }
  ],
  "tables": [
    {
      "rows": 2,
      "columns": 2,
      "data": [
        ["Cell 1", "Cell 2"],
        ["Cell 3", "Cell 4"]
      ]
    }
  ]
}'
echo -e "\\n"

# 3. Delete a slide from a presentation
echo "Deleting a slide from a presentation (replace <PRESENTATION_ID> and <SLIDE_ID>)..."
curl -X DELETE "http://localhost:8000/drive/presentations/<PRESENTATION_ID>/slides/<SLIDE_ID>" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>"
echo -e "\\n"


echo "--- Documents API ---"

# 1. Create a new Google Document
echo "Creating a new document..."
curl -X POST "http://localhost:8000/drive/documents" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "title": "My Awesome Document"
}'
echo -e "\n"

# 2. Get a Google Document
echo "Getting a document (replace <DOCUMENT_ID>)..."
curl -X GET "http://localhost:8000/drive/documents/<DOCUMENT_ID>" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>"
echo -e "\n"

# 3. Append styled content to a document
echo "Appending styled content to a document (replace <DOCUMENT_ID>)..."
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
echo -e "\n"

# 4. Append content with advanced styling to a document
echo "Appending content with advanced styling to a document (replace <DOCUMENT_ID>)..."
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
echo -e "\n"

# 5. Insert a table into a document
echo "Inserting a table into a document (replace <DOCUMENT_ID>)..."
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
echo -e "\n"

# 6. Add a comment to a document
echo "Adding a comment to a document (replace <DOCUMENT_ID>)..."
curl -X POST "http://localhost:8000/drive/documents/<DOCUMENT_ID>/comments" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "text": "Could you elaborate on this point?",
  "start_index": 20,
  "end_index": 50
}'
echo -e "\n"


echo "--- Spreadsheets API ---"

# 1. Create a new Google Spreadsheet
echo "Creating a new spreadsheet..."
curl -X POST "http://localhost:8000/drive/spreadsheets" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "title": "My Awesome Spreadsheet"
}'
echo -e "\n"

# 2. Get a Google Spreadsheet
echo "Getting a spreadsheet (replace <SPREADSHEET_ID>)..."
curl -X GET "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>"
echo -e "\n"

# 3. Add a new sheet to a spreadsheet
echo "Adding a new sheet to a spreadsheet (replace <SPREADSHEET_ID>)..."
curl -X POST "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>/sheets" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "title": "New Sheet"
}'
echo -e "\n"

# 4. Append data to a sheet
echo "Appending data to a sheet (replace <SPREADSHEET_ID> and <SHEET_NAME>)..."
curl -X POST "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>/sheets/<SHEET_NAME>:append" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
  "values": [
    ["A1", "B1", "C1"],
    ["A2", "B2", "C2"]
  ]
}'
echo -e "\n"

# 5. Append formatted data to a sheet
echo "Appending formatted data to a sheet (replace <SPREADSHEET_ID> and <SHEET_NAME>)..."
curl -X POST "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>/sheets/<SHEET_NAME>:appendFormatted" \
-H "Content-Type: application/json" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>" \
-d '{
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
}'
echo -e "\n"

# 6. Clear a sheet
echo "Clearing a sheet (replace <SPREADSHEET_ID> and <SHEET_NAME>)..."
curl -X POST "http://localhost:8000/drive/spreadsheets/<SPREADSHEET_ID>/sheets/<SHEET_NAME>:clear" \
-H "Cookie: session=<SESSION_COOKIE_VALUE>"
echo -e "\n" 