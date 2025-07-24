#!/bin/bash
# Example usage of the Google Documents API Wrapper endpoints

BASE_URL="http://localhost:8000"
SESSION_COOKIE="session=your_session_cookie_here"  # Replace with your actual session cookie value
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md

# Create a new document (no parent)
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/documents"
echo -e "\n---"

# Create a new document in a specific parent folder
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/documents?parent=$PARENT_ID"
echo -e "\n---"

# Get a document by ID
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo"
echo -e "\n---"

# Add a heading to a document (h1, h2, etc.)
curl -b "$SESSION_COOKIE" -X PUT -H "Content-Type: application/json" \
  -d '{"text": "My Heading", "level": 1}' \
  "$BASE_URL/drive/documents/1a-28yTY23NuCa7vmyMABGgRDCErW58Q99F_2o9ZePGo/heading"
echo -e "\n---" 