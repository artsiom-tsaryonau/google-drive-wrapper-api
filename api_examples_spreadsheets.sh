#!/bin/bash
# Example usage of the Google Spreadsheets API Wrapper endpoints

BASE_URL="http://localhost:8000"
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md
SAMPLE_SPREADSHEET_ID="1R3rJWb50oW2JNOqKd4l0XlP-9hdMPr1c9cxjYX3PWnY"  # Sample spreadsheet id from wrapper_api.md

echo "=== Google Spreadsheets API Examples ==="
echo

# Create a new spreadsheet (no parent)
echo "1. Create a new spreadsheet (no parent):"
curl -X POST "$BASE_URL/drive/spreadsheets?title=MyNewSheet"
echo -e "\n---"

# Create a new spreadsheet in a specific parent folder
echo "2. Create a new spreadsheet in a specific parent folder:"
curl -X POST "$BASE_URL/drive/spreadsheets?title=MySheet&parent=$PARENT_ID"
echo -e "\n---"

# Get a spreadsheet by ID
echo "3. Get a spreadsheet by ID:"
curl "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID"
echo -e "\n---"

# Delete a spreadsheet by ID
echo "4. Delete a spreadsheet by ID:"
curl -X DELETE "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID"
echo -e "\n---"

# Add a new sheet to a spreadsheet
echo "5. Add a new sheet to a spreadsheet:"
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Sheet2"}' \
  "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets"
echo -e "\n---"

# Get a specific sheet by name
echo "6. Get a specific sheet by name:"
curl "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet1"
echo -e "\n---"

# Get a range from a sheet using A1 notation
echo "7. Get a range from a sheet using A1 notation:"
curl "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

# Update a range in a sheet using A1 notation (values and formatting)
echo "8. Update a range in a sheet using A1 notation (values and formatting):"
curl -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["Bold", "Red"]], "format": {"textFormat": {"bold": true}, "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8}}}' \
  "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet1/range?a1=A1:B1"
echo -e "\n---"

# Update a range in a sheet using A1 notation (values only)
echo "9. Update a range in a sheet using A1 notation (values only):"
curl -X PUT -H "Content-Type: application/json" \
  -d '{"values": [["New Value 1", "New Value 2"], ["New Value 3", "New Value 4"]]}' \
  "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

# Update a range in a sheet using A1 notation (formatting only)
echo "10. Update a range in a sheet using A1 notation (formatting only):"
curl -X PUT -H "Content-Type: application/json" \
  -d '{"format": {"backgroundColor": {"red": 1, "green": 1, "blue": 0.5}}}' \
  "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet1/range?a1=B2:B3"
echo -e "\n---"

# Delete a sheet from a spreadsheet
echo "11. Delete a sheet from a spreadsheet:"
curl -X DELETE "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet2"
echo -e "\n---"

# Delete a range from a sheet using A1 notation
echo "12. Delete a range from a sheet using A1 notation:"
curl -X DELETE "$BASE_URL/drive/spreadsheets/$SAMPLE_SPREADSHEET_ID/sheets/Sheet1/range?a1=A1:B2"
echo -e "\n---"

echo "=== All examples completed ===" 