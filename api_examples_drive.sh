#!/bin/bash
# Example usage of the Google Drive API Wrapper endpoints

BASE_URL="http://localhost:8000"
SESSION_COOKIE="session=your_session_cookie_here"  # Replace with your actual session cookie value
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md
SAMPLE_DOCUMENT_ID="1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"  # Sample document id from wrapper_api.md

echo "=== Google Drive API Examples ==="
echo

# Search Google Drive objects by name (optionally filter by mimeType)
echo "1. Search Google Drive objects by name:"
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/search?name=Sample&mimeType="
echo -e "\n---"

# List Google Drive content in a specific path (optionally filter by mimeType)
echo "2. List Google Drive content in a specific path:"
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/navigate/folder1/folder2?mimeType="
echo -e "\n---"

# Add a comment to a file
echo "3. Add a comment to a file:"
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/$SAMPLE_DOCUMENT_ID/comment" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a test comment on the document"}'
echo -e "\n---"

# Add a reply to a comment (replace COMMENT_ID with actual comment ID from previous response)
echo "4. Add a reply to a comment:"
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/$SAMPLE_DOCUMENT_ID/comment/COMMENT_ID/reply" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a reply to the comment"}'
echo -e "\n---"

# Resolve a comment (replace COMMENT_ID with actual comment ID)
echo "5. Resolve a comment:"
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/$SAMPLE_DOCUMENT_ID/comment/COMMENT_ID/resolve"
echo -e "\n---"

# Delete a comment (replace COMMENT_ID with actual comment ID)
echo "6. Delete a comment:"
curl -b "$SESSION_COOKIE" -X DELETE "$BASE_URL/drive/$SAMPLE_DOCUMENT_ID/comment/COMMENT_ID"
echo -e "\n---"

# Delete an object by ID
echo "7. Delete an object by ID:"
curl -b "$SESSION_COOKIE" -X DELETE "$BASE_URL/drive/your_file_or_folder_id_here"
echo -e "\n---"

echo "=== All examples completed ===" 