#!/bin/bash
# Example usage of the Google API Wrapper endpoints

BASE_URL="http://localhost:8000"
PARENT_ID="your_parent_folder_id_here"  # Replace with a real folder ID if needed

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

# --- Documents ---
# Create a new document (no parent)
curl -X POST "$BASE_URL/drive/document"
echo -e "\n---"

# Create a new document in a specific parent folder
curl -X POST "$BASE_URL/drive/document?parent=$PARENT_ID"
echo -e "\n---"

# Get a document by ID
curl "$BASE_URL/drive/document/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"
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