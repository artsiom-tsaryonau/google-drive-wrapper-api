#!/bin/bash
# Example usage of the Google Documents API Wrapper endpoints

BASE_URL="http://localhost:8000"
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md
SAMPLE_DOCUMENT_ID="1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"  # Sample document id from wrapper_api.md

echo "=== Google Documents API Examples ==="
echo

# Create a new document (no parent)
echo "1. Create a new document (no parent):"
curl -X POST "$BASE_URL/drive/documents?title=MyNewDocument"
echo -e "\n---"

# Create a new document in a specific parent folder
echo "2. Create a new document in a specific parent folder:"
curl -X POST "$BASE_URL/drive/documents?title=MyDocument&parent=$PARENT_ID"
echo -e "\n---"

# Get a document by ID
echo "3. Get a document by ID:"
curl "$BASE_URL/drive/documents/$SAMPLE_DOCUMENT_ID"
echo -e "\n---"

# Delete a document by ID
echo "4. Delete a document by ID:"
curl -X DELETE "$BASE_URL/drive/documents/$SAMPLE_DOCUMENT_ID"
echo -e "\n---"

echo "=== All examples completed ===" 