"""
Quick test - send a welcome template email.
"""

import asyncio
import httpx


async def test_welcome():
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "welcome",
        "context": {
            "user_name": "Muhammad Salah",
            "verify_url": "https://example.com/verify/abc123"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/email/send-template",
            json=data,
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        print(response.json())


asyncio.run(test_welcome())
