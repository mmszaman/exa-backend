import requests
import json

# Test if the webhook endpoint is accessible
url = "http://localhost:8000/api/v1/auth/clerk-webhook"

# This will fail signature verification but should log the attempt
test_payload = {
    "type": "user.created",
    "data": {
        "id": "test_user_123",
        "email_addresses": [
            {
                "id": "email_1",
                "email_address": "test@example.com"
            }
        ],
        "primary_email_address_id": "email_1",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User"
    }
}

headers = {
    "content-type": "application/json",
    "svix-id": "test_id",
    "svix-timestamp": "1234567890",
    "svix-signature": "test_signature"
}

try:
    response = requests.post(url, json=test_payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
