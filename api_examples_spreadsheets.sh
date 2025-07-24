#!/bin/bash
# Example usage of the Google Spreadsheets API Wrapper endpoints

BASE_URL="http://localhost:8000"
SESSION_COOKIE="session=your_session_cookie_here"  # Replace with your actual session cookie value
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md

# Create a new spreadsheet (no parent)
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/spreadsheets"
echo -e "\n---"

# Create a new spreadsheet in a specific parent folder
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/spreadsheets?parent=$PARENT_ID"
echo -e "\n---"

# Get a spreadsheet by ID
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY"
echo -e "\n---"

# Add a new sheet to a spreadsheet
curl -b "$SESSION_COOKIE" -X POST -H "Content-Type: application/json" \
  -d '{"name": "Sheet2"}' \
  "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets"
echo -e "\n---"

# Get a specific sheet by name
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1"
echo -e "\n---"

# Get a range from a sheet using A1 notation
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

# Update a range in a sheet using A1 notation (values and formatting)
curl -b "$SESSION_COOKIE" -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["Bold", "Red"]], "format": {"textFormat": {"bold": true}, "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8}}}' \
  "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B1"
echo -e "\n---"

# Update a range in a sheet using A1 notation (formatting only)
curl -b "$SESSION_COOKIE" -X PUT -H "Content-Type: application/json" \
  -d '{"format": {"backgroundColor": {"red": 1, "green": 1, "blue": 0.5}}}' \
  "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=B2:B3"
echo -e "\n---"

# Delete a sheet from a spreadsheet
curl -b "$SESSION_COOKIE" -X DELETE "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet2"
echo -e "\n---"

# Delete a range from a sheet using A1 notation
curl -b "$SESSION_COOKIE" -X DELETE "$BASE_URL/drive/spreadsheets/1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---" 