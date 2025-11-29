"""
Test sending admin notification email
"""
import httpx
import asyncio


async def test_admin_notification():
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        print("\n" + "=" * 60)
        print("Testing Admin Notification Email")
        print("=" * 60)
        
        template_data = {
            "recipients": ["exateks@gmail.com"],
            "template_name": "admin_notification",
            "subject": "Admin Notification - Test Email Sent",
            "from_name": "ExaKeep Admin",
            "from_email": "support@exakeep.com",
            "context": {
                "title": "Email Activity Notification",
                "user_email": "exateks@gmail.com",
                "email_purpose": "Testing admin notification template with ExaKeep sender",
                "company_name": "ExaKeep"
            }
        }
        
        try:
            print("\nSending admin notification template email...")
            print(f"From: {template_data['from_name']} <{template_data['from_email']}>")
            print(f"To: {template_data['recipients']}")
            print(f"Subject: {template_data['subject']}")
            print(f"Template: {template_data['template_name']}")
            
            response = await client.post(
                f"{base_url}/api/email/send-template",
                json=template_data,
                timeout=30.0
            )
            
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.json()}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_admin_notification())
