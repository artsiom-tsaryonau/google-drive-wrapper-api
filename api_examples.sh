#!/bin/bash
# Example usage of the Google API Wrapper endpoints

BASE_URL="http://localhost:8000"
PARENT_ID="your_parent_folder_id_here"  # Replace with a real folder ID if needed

# --- Authentication Example ---
# 1. Log in to get the authentication URL (opens browser for OAuth)
echo "Visit the following URL in your browser to authenticate via Google:"
curl -i "$BASE_URL/login"
echo -e "\n---"

# 2. After authenticating, your browser will store a session cookie. To use curl with authentication, export the cookie from your browser and use it like this:
# export SESSION_COOKIE="session=your_session_cookie_here"
# curl -b "$SESSION_COOKIE" "$BASE_URL/drive/search?name=Sample"

# You can use the -b flag with any curl command below to make authenticated requests.

# --- Authenticated Request Example ---
# Example: Search Google Drive objects by name using a session cookie
SESSION_COOKIE="session=your_session_cookie_here"  # Replace with your actual session cookie value
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/search?name=Sample&mimeType="
echo -e "\n---"

# --- Drive API ---
# Search Google Drive objects by name (optionally filter by mimeType)
curl "$BASE_URL/drive/search?name=Sample&mimeType="
echo -e "\n---"

# List Google Drive content in a specific path (optionally filter by mimeType)
curl "$BASE_URL/drive/navigate/folder1/folder2?mimeType="
echo -e "\n---"

# Delete an object by ID
curl -X DELETE "$BASE_URL/drive/your_file_or_folder_id_here"
echo -e "\n---"

# --- Spreadsheets ---
# Create a new spreadsheet (no parent)
curl -X POST "$BASE_URL/drive/spreadsheets"
echo -e "\n---"

# Create a new spreadsheet in a specific parent folder
curl -X POST "$BASE_URL/drive/spreadsheets?parent=$PARENT_ID"
echo -e "\n---"

# Get a spreadsheet by ID
curl "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY"
echo -e "\n---"

# Add a new sheet to a spreadsheet
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Sheet2"}' \
  "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets"
echo -e "\n---"

# Get a specific sheet by name
curl "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1"
echo -e "\n---"

# Get a range from a sheet using A1 notation
curl "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

# Update a range in a sheet using A1 notation
curl -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["New Value 1", "New Value 2"], ["New Value 3", "New Value 4"]]}' \
  "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

# Delete a sheet from a spreadsheet
curl -X DELETE "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet2"
echo -e "\n---"

# Delete a range from a sheet using A1 notation
curl -X DELETE "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

# Update a range in a sheet with formatting
curl -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["Bold", "Red"]], "format": {"textFormat": {"bold": true}, "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8}}}' \
  "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B1"
echo -e "\n---"

# --- Documents ---
# Create a new document (no parent)
curl -X POST "$BASE_URL/drive/documents"
echo -e "\n---"

# Create a new document in a specific parent folder
curl -X POST "$BASE_URL/drive/documents?parent=$PARENT_ID"
echo -e "\n---"

# Get a document by ID
curl "$BASE_URL/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"
echo -e "\n---"

# Add a heading to a document (h1, h2, etc.)
curl -X PUT -H "Content-Type: application/json" \
  -d '{"text": "My Heading", "level": 1}' \
  "$BASE_URL/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/heading"
echo -e "\n---"

# --- Slides ---
# Create a new slide presentation (no parent)
curl -X POST "$BASE_URL/drive/slides"
echo -e "\n---"

# Create a new slide presentation in a specific parent folder
curl -X POST "$BASE_URL/drive/slides?parent=$PARENT_ID"
echo -e "\n---"

# Get a slide presentation by ID
curl "$BASE_URL/drive/slides/17rCbrfnQiFBWqHQCOJ5U7bug05C5XF9c4o4ptRrrOHY"
echo -e "\n---" 