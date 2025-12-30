"""
Test if webhook endpoint receives requests
"""
import asyncio
import httpx

async def test_webhook():
    url = "http://localhost:8000/webhook/clerk"
    
    # Simple test payload
    test_payload = {
        "type": "user.created",
        "data": {
            "id": "user_test123",
            "email_addresses": [{"email_address": "test@example.com"}],
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        }
    }
    
    # Note: This will fail signature verification, but we can see if endpoint is reachable
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=test_payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
