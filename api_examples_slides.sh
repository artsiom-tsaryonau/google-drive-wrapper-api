#!/bin/bash
# Example usage of the Google Slides API Wrapper endpoints

BASE_URL="http://localhost:8000"
SESSION_COOKIE="session=your_session_cookie_here"  # Replace with your actual session cookie value
PARENT_ID="1xa0a3Z4YUfDZ3FQS4LrpdOZEkVp8hrq7"  # Parent id from wrapper_api.md

# Create a new slide presentation (no parent)
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/slides"
echo -e "\n---"

# Create a new slide presentation in a specific parent folder
curl -b "$SESSION_COOKIE" -X POST "$BASE_URL/drive/slides?parent=$PARENT_ID"
echo -e "\n---"

# Get a slide presentation by ID
curl -b "$SESSION_COOKIE" "$BASE_URL/drive/slides/17rCbrfnQiFBWqHQCOJ5U7bug05C5XF9c4o4ptRrrOHY"
echo -e "\n---" 