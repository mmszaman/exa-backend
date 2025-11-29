"""
Test Sending Actual Email
Send a real email using the email service to verify everything works.
"""

import asyncio
from app.services.email_service import EmailService
from app.config import settings


async def test_send_email():
    """Send a test email to verify the email service works."""
    
    print("\n" + "=" * 60)
    print("📧 EMAIL SERVICE TEST")
    print("=" * 60)
    
    # Test: Send a simple email to yourself
    print("\n🧪 Sending test email...")
    print(f"   From: {settings.EMAIL_USER}")
    print(f"   To: {settings.ADMIN_TO}")
    
    html_body = """
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4CAF50;">✅ Email Service Test Successful!</h2>
            <p>This is a test email from your Exa-Backend email service.</p>
            <p><strong>Features working:</strong></p>
            <ul>
                <li>✅ SMTP connection to Gmail Workspace</li>
                <li>✅ HTML email rendering</li>
                <li>✅ Email validation</li>
                <li>✅ Async sending</li>
                <li>✅ Logging system</li>
            </ul>
            <p style="margin-top: 20px; color: #666;">
                <small>Sent from Exa-Backend Email Service</small>
            </p>
        </body>
    </html>
    """
    
    text_body = """
Email Service Test Successful!

This is a test email from your Exa-Backend email service.

Features working:
- SMTP connection to Gmail Workspace
- HTML email rendering
- Email validation
- Async sending
- Logging system

Sent from Exa-Backend Email Service
    """
    
    try:
        results = await EmailService.send_email(
            recipients=[settings.ADMIN_TO],
            subject="Test Email from Exa-Backend",
            body_text=text_body,
            body_html=html_body,
            from_name="Exa-Backend Test",
            from_email="support@exateks.com"
        )
        
        print(f"\n📊 Results:")
        
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.recipient}")
            if result.success:
                print(f"      Sent at: {result.sent_at}")
            else:
                print(f"      Error: {result.error}")
        
        successful = sum(1 for r in results if r.success)
        if successful > 0:
            print("\n✅ Email sent successfully!")
            print(f"   Check your inbox: {settings.ADMIN_TO}")
        else:
            print("\n❌ Email sending failed!")
            
    except Exception as e:
        print(f"\n❌ Error sending email:")
        print(f"   {type(e).__name__}: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ EMAIL SERVICE TESTS COMPLETED")
    print("=" * 60)
    print("\nCheck your email logs at: logs/email_service.log")
    print(f"Check your inbox at: {settings.ADMIN_TO}\n")
    
    return True


if __name__ == "__main__":
    print("\n🚀 Starting Email Service Tests...\n")
    asyncio.run(test_send_email())
