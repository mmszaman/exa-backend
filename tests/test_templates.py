"""
Test script for email template system.
Tests template rendering and sending with different templates.
"""

import asyncio
import httpx


async def test_welcome_template():
    """Test welcome template email."""
    print("\n" + "="*60)
    print("🎉 Testing Welcome Template")
    print("="*60)
    
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "welcome",
        "context": {
            "user_name": "Muhammad Salah",
            "verify_url": "https://example.com/verify/abc123xyz"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/email/send-template",
                json=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Total Sent: {result.get('total_sent')}")
            print(f"Total Failed: {result.get('total_failed')}")
            
            if result.get('results'):
                for r in result['results']:
                    print(f"  ✅ {r['recipient']}: {'Sent' if r['success'] else 'Failed'}")
                    if r.get('error'):
                        print(f"     Error: {r['error']}")
            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def test_password_reset_template():
    """Test password reset template email."""
    print("\n" + "="*60)
    print("🔒 Testing Password Reset Template")
    print("="*60)
    
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "password_reset",
        "context": {
            "user_name": "Muhammad Salah",
            "reset_url": "https://example.com/reset-password/secure-token-here",
            "expiry_hours": "2"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/email/send-template",
                json=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Total Sent: {result.get('total_sent')}")
            print(f"Total Failed: {result.get('total_failed')}")
            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def test_email_verification_template():
    """Test email verification template email."""
    print("\n" + "="*60)
    print("✉️ Testing Email Verification Template")
    print("="*60)
    
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "email_verification",
        "context": {
            "user_name": "Muhammad Salah",
            "verify_url": "https://example.com/verify/verification-token",
            "verification_code": "123456",
            "expiry_hours": "48"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/email/send-template",
                json=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Total Sent: {result.get('total_sent')}")
            print(f"Total Failed: {result.get('total_failed')}")
            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def test_notification_success_template():
    """Test notification template with success type."""
    print("\n" + "="*60)
    print("🔔 Testing Notification Template (Success)")
    print("="*60)
    
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "notification",
        "context": {
            "user_name": "Muhammad Salah",
            "notification_title": "Payment Successful",
            "message": "Your payment has been processed successfully.",
            "notification_type": "success",
            "notification_heading": "Payment Confirmed",
            "notification_text": "We received your payment of $99.99. Your subscription is now active.",
            "action_url": "https://example.com/dashboard",
            "action_text": "View Dashboard",
            "additional_info": "Your next billing date is January 28, 2026.",
            "items": [
                "Access to premium features",
                "Priority customer support",
                "Monthly reports and analytics"
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/email/send-template",
                json=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Total Sent: {result.get('total_sent')}")
            print(f"Total Failed: {result.get('total_failed')}")
            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def test_notification_warning_template():
    """Test notification template with warning type."""
    print("\n" + "="*60)
    print("⚠️ Testing Notification Template (Warning)")
    print("="*60)
    
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "notification",
        "context": {
            "user_name": "Muhammad Salah",
            "notification_title": "Account Security Alert",
            "message": "We noticed unusual activity on your account.",
            "notification_type": "warning",
            "notification_heading": "Security Review Required",
            "notification_text": "Please review recent login attempts and update your password if needed.",
            "action_url": "https://example.com/security",
            "action_text": "Review Security"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/email/send-template",
                json=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def test_invalid_template():
    """Test with invalid template name (should fail validation)."""
    print("\n" + "="*60)
    print("❌ Testing Invalid Template (Should Fail)")
    print("="*60)
    
    data = {
        "recipients": ["exateks@gmail.com"],
        "template_name": "invalid_template_name",
        "context": {
            "user_name": "Test User"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/email/send-template",
                json=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def main():
    """Run all template tests."""
    print("\n" + "="*60)
    print("🚀 EMAIL TEMPLATE TESTING SUITE")
    print("="*60)
    print("Testing all email templates with various scenarios")
    print("Server must be running on http://localhost:8000")
    
    # Test all templates
    await test_welcome_template()
    await asyncio.sleep(1)  # Small delay between tests
    
    await test_password_reset_template()
    await asyncio.sleep(1)
    
    await test_email_verification_template()
    await asyncio.sleep(1)
    
    await test_notification_success_template()
    await asyncio.sleep(1)
    
    await test_notification_warning_template()
    await asyncio.sleep(1)
    
    await test_invalid_template()
    
    print("\n" + "="*60)
    print("✅ All template tests completed!")
    print("="*60)
    print("\nCheck your email inbox (exateks@gmail.com) for template emails.")


if __name__ == "__main__":
    asyncio.run(main())
