"""
Test SMTP Connection and Authentication
Simple script to verify email credentials work.
"""

import asyncio
import aiosmtplib
from app.config import settings


async def test_smtp_connection():
    """Test SMTP connection and authentication."""
    
    print("=" * 60)
    print("SMTP Connection Test")
    print("=" * 60)
    
    # Display configuration (hide password)
    print(f"\n📧 Configuration:")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   User: {settings.EMAIL_USER}")
    print(f"   Password: {'*' * len(settings.EMAIL_PASSWORD) if settings.EMAIL_PASSWORD else 'NOT SET'}")
    
    # Check if credentials are set
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        print("\n❌ ERROR: Email credentials not configured!")
        print("   Please set EMAIL_USER and EMAIL_PASSWORD in .env file")
        return False
    
    print(f"\n🔌 Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
    
    try:
        # Create SMTP connection
        smtp = aiosmtplib.SMTP(
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            start_tls=True  # Use STARTTLS
        )
        
        # Connect
        await smtp.connect()
        print("✅ Connected successfully!")
        
        # Authenticate
        print(f"\n🔐 Authenticating as {settings.EMAIL_USER}...")
        await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        print("✅ Authentication successful!")
        
        # Get server info
        print(f"\n📊 Server Info:")
        print(f"   Host: {settings.EMAIL_HOST}")
        print(f"   Port: {settings.EMAIL_PORT}")
        print(f"   Supports TLS: Yes")
        print(f"   Connected: Yes")
        
        # Disconnect
        await smtp.quit()
        print("\n✅ Disconnected cleanly")
        
        print("\n" + "=" * 60)
        print("✅ SMTP TEST PASSED - Your email credentials work!")
        print("=" * 60)
        
        return True
        
    except aiosmtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication Failed!")
        print(f"   Error: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Check EMAIL_USER is correct (your full email)")
        print("   2. Check EMAIL_PASSWORD is correct")
        print("   3. For Gmail: Use an App Password, not your regular password")
        print("      - Go to: https://myaccount.google.com/apppasswords")
        print("      - Generate a new App Password")
        print("      - Use that password in .env file")
        return False
        
    except aiosmtplib.SMTPConnectError as e:
        print(f"\n❌ Connection Failed!")
        print(f"   Error: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Check internet connection")
        print("   2. Check EMAIL_HOST is correct")
        print("   3. Check EMAIL_PORT is correct (usually 587 for TLS)")
        print("   4. Check firewall isn't blocking SMTP")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error!")
        print(f"   Type: {type(e).__name__}")
        print(f"   Error: {e}")
        return False


# Run the test
if __name__ == "__main__":
    print("\n🧪 Starting SMTP Connection Test...\n")
    
    # Run async function
    result = asyncio.run(test_smtp_connection())
    
    if result:
        print("\n✅ You're ready to send emails!")
    else:
        print("\n❌ Please fix the issues above and try again")
