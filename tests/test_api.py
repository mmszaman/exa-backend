"""
Test Email API Endpoint
Test the FastAPI email endpoint by making HTTP requests.
"""

import asyncio
import httpx


async def test_email_api():
    """Test the email API endpoint."""
    
    base_url = "http://localhost:8000"
    
    print("\n" + "=" * 60)
    print("🧪 EMAIL API ENDPOINT TEST")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        print("\n📊 Test 1: Health Check")
        print("-" * 60)
        
        try:
            response = await client.get(f"{base_url}/api/email/check")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n⚠️  Make sure the server is running:")
            print("   python -m uvicorn app.main:app --reload")
            return
        
        # Test 2: Send template email (welcome template)
        print("\n📧 Test 2: Send Welcome Template Email")
        print("-" * 60)
        
        template_data = {
            "recipients": ["exateks@gmail.com"],
            "template_name": "welcome",
            "subject": "Welcome to Exateks!",
            "from_name": "Exateks Team",
            "from_email": "support@exateks.com",
            "context": {
                "user_name": "Muhammad Salah",
                "verify_url": "https://example.com/verify/abc123xyz456",
                "company_name": "Exateks"
            }
        }
        
        print(f"Sending to: {template_data['recipients']}")
        print(f"Template: {template_data['template_name']}")
        print(f"Context: {template_data['context']}")
        
        try:
            response = await client.post(
                f"{base_url}/api/email/send-template",
                json=template_data
            )
            
            print(f"\nStatus Code: {response.status_code}")
            result = response.json()
            
            print(f"\n📊 Response:")
            print(f"   Success: {result.get('success')}")
            print(f"   Total Sent: {result.get('total_sent')}")
            print(f"   Total Failed: {result.get('total_failed')}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('results'):
                print(f"\n📝 Details:")
                for r in result['results']:
                    status = "✅" if r['success'] else "❌"
                    print(f"   {status} {r['recipient']}")
                    if r.get('sent_at'):
                        print(f"      Sent at: {r['sent_at']}")
                    if r.get('error'):
                        print(f"      Error: {r['error']}")
            
            if result.get('success'):
                print("\n✅ Welcome email sent successfully via API!")
                print("📬 Check your inbox at exateks@gmail.com")
            else:
                print("\n⚠️  Some emails failed to send")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API TESTS COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting API Tests...")
    print("⚠️  Make sure the server is running: python -m uvicorn app.main:app --reload\n")
    
    asyncio.run(test_email_api())
