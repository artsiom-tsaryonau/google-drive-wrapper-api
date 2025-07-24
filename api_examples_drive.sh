#!/bin/bash
# Example usage of the Google Drive API Wrapper endpoints

BASE_URL="http://localhost:8000"
SESSION_COOKIE="session=your_session_cookie_here"  # Replace with your actual session cookie value
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md

# Search Google Drive objects by name (optionally filter by mimeType)
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/search?name=Sample&mimeType="
echo -e "\n---"

# List Google Drive content in a specific path (optionally filter by mimeType)
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/navigate/folder1/folder2?mimeType="
echo -e "\n---"

# Delete an object by ID
curl -b "$SESSION_COOKIE" -X DELETE "$BASE_URL/drive/your_file_or_folder_id_here"
echo -e "\n---" 