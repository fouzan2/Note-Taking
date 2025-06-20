#!/bin/bash

# Google Cloud API Test Script using curl
# Base URL for the deployed API
BASE_URL="https://note-taking-api-ne3atfgzsa-uc.a.run.app"
API_URL="${BASE_URL}/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test user credentials
TEST_USER="testuser_$(date +%s)"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Google Cloud API Test - Curl Commands${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Base URL: ${BASE_URL}\n"

# 1. Health Check
echo -e "${GREEN}1. Health Check${NC}"
echo "Command: curl ${BASE_URL}/health"
curl -s "${BASE_URL}/health" | jq '.' || echo "Failed"
echo -e "\n"

# 2. Register User
echo -e "${GREEN}2. Register New User${NC}"
echo "Command: curl -X POST ${API_URL}/auth/register"
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${TEST_USER}\",
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\"
  }")
echo "$REGISTER_RESPONSE" | jq '.'
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id')
echo -e "\n"

# 3. Login
echo -e "${GREEN}3. Login${NC}"
echo "Command: curl -X POST ${API_URL}/auth/login"
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER}&password=${TEST_PASSWORD}")
echo "$LOGIN_RESPONSE" | jq '.'
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo -e "\n"

# 4. Get Current User
echo -e "${GREEN}4. Get Current User Info${NC}"
echo "Command: curl ${API_URL}/auth/me -H 'Authorization: Bearer TOKEN'"
curl -s "${API_URL}/auth/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'
echo -e "\n"

# 5. Create a Note
echo -e "${GREEN}5. Create a Note${NC}"
echo "Command: curl -X POST ${API_URL}/notes/"
NOTE_RESPONSE=$(curl -s -X POST "${API_URL}/notes/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Note from Curl",
    "content": "This is a test note created using curl command.",
    "tags": ["test", "api", "curl"]
  }')
echo "$NOTE_RESPONSE" | jq '.'
NOTE_ID=$(echo "$NOTE_RESPONSE" | jq -r '.id')
echo -e "\n"

# 6. List All Notes
echo -e "${GREEN}6. List All Notes${NC}"
echo "Command: curl ${API_URL}/notes/"
curl -s "${API_URL}/notes/?page=1&per_page=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'
echo -e "\n"

# 7. Search Notes
echo -e "${GREEN}7. Search Notes${NC}"
echo "Command: curl ${API_URL}/notes/search?q=test"
curl -s "${API_URL}/notes/search?q=test&page=1&per_page=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'
echo -e "\n"

# 8. Get Specific Note
echo -e "${GREEN}8. Get Specific Note${NC}"
echo "Command: curl ${API_URL}/notes/${NOTE_ID}"
curl -s "${API_URL}/notes/${NOTE_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'
echo -e "\n"

# 9. Update Note
echo -e "${GREEN}9. Update Note${NC}"
echo "Command: curl -X PUT ${API_URL}/notes/${NOTE_ID}"
curl -s -X PUT "${API_URL}/notes/${NOTE_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Note from Curl",
    "content": "This note has been updated using curl.",
    "tags": ["updated", "curl", "test"]
  }' | jq '.'
echo -e "\n"

# 10. List Tags
echo -e "${GREEN}10. List All Tags${NC}"
echo "Command: curl ${API_URL}/tags/"
curl -s "${API_URL}/tags/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'
echo -e "\n"

# 11. Delete Note
echo -e "${GREEN}11. Delete Note${NC}"
echo "Command: curl -X DELETE ${API_URL}/notes/${NOTE_ID}"
curl -s -X DELETE "${API_URL}/notes/${NOTE_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" -w "HTTP Status: %{http_code}\n"
echo -e "\n"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Test Completed!${NC}"
echo -e "${YELLOW}========================================${NC}"

# Save credentials for future use
echo -e "\n${GREEN}Test Credentials:${NC}"
echo "Username: ${TEST_USER}"
echo "Password: ${TEST_PASSWORD}"
echo "Access Token: ${ACCESS_TOKEN:0:20}..." 