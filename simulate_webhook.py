"""
Manually trigger webhook locally (bypasses Clerk)
This simulates what Clerk would send
"""
import asyncio
import json
from app.core.database import get_db
from app.services.user_service import UserService
from app.services.tenant_service import SessionService
from app.core.logger import get_logger
from datetime import datetime, timezone

logger = get_logger("manual_webhook")

async def simulate_user_created_webhook():
    """
    Simulate a user.created webhook event
    """
    async for db in get_db():
        try:
            # Simulate Clerk user.created webhook data
            event_data = {
                "id": "user_manual_test_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "email_addresses": [
                    {
                        "id": "email_123",
                        "email_address": "manualtest@example.com"
                    }
                ],
                "primary_email_address_id": "email_123",
                "username": "manualtest",
                "first_name": "Manual",
                "last_name": "Test",
                "profile_image_url": "https://example.com/avatar.jpg",
                "phone_numbers": [],
                "public_metadata": {
                    "lead_source": "manual_test",
                    "brand": "smbhub"
                },
                "private_metadata": {},
                "unsafe_metadata": {
                    "utm_source": "test",
                    "utm_campaign": "manual_webhook"
                }
            }
            
            # Extract data (same logic as webhook handler)
            clerk_user_id = event_data.get("id")
            email_addresses = event_data.get("email_addresses", [])
            primary_email = None
            
            for email_obj in email_addresses:
                if email_obj.get("id") == event_data.get("primary_email_address_id"):
                    primary_email = email_obj.get("email_address")
                    break
            
            username = event_data.get("username")
            first_name = event_data.get("first_name", "")
            last_name = event_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            avatar_url = event_data.get("profile_image_url")
            
            public_metadata = event_data.get("public_metadata", {})
            private_metadata = event_data.get("private_metadata", {})
            unsafe_metadata = event_data.get("unsafe_metadata", {})
            
            lead_source = public_metadata.get("lead_source")
            brand = public_metadata.get("brand")
            utm_source = unsafe_metadata.get("utm_source")
            utm_campaign = unsafe_metadata.get("utm_campaign")
            
            clerk_metadata = json.dumps({
                "public": public_metadata,
                "private": private_metadata,
                "unsafe": unsafe_metadata
            })
            
            logger.info(f"Creating user: {clerk_user_id} ({primary_email})")
            
            # Create user
            user = await UserService.create_from_clerk(
                db=db,
                clerk_user_id=clerk_user_id,
                email=primary_email,
                username=username,
                full_name=full_name,
                avatar_url=avatar_url,
                phone_number=None,
                lead_source=lead_source,
                brand=brand,
                referral_code=None,
                utm_source=utm_source,
                utm_medium=None,
                utm_campaign=utm_campaign,
                clerk_metadata=clerk_metadata
            )
            
            logger.info(f"✓ User created: ID={user.id}, Email={user.email}, Clerk ID={user.clerk_user_id}")
            
            # Now create a session for this user
            session_data = {
                "id": "sess_manual_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "user_id": clerk_user_id,
                "client_id": "client_test_123",
                "status": "active",
                "expire_at": int((datetime.now(timezone.utc).timestamp())) + 3600
            }
            
            session = await SessionService.create_or_update_session(
                db=db,
                clerk_session_id=session_data["id"],
                user_id=user.id,
                clerk_user_id=clerk_user_id,
                tenant_id=None,
                status=session_data["status"],
                client_id=session_data["client_id"],
                expires_at=datetime.fromtimestamp(session_data["expire_at"], timezone.utc),
                clerk_metadata=None
            )
            
            logger.info(f"✓ Session created: ID={session.id}, Clerk Session ID={session.clerk_session_id}")
            logger.info("=" * 60)
            logger.info("SUCCESS: User and session created in database!")
            logger.info("=" * 60)
            
            return user, session
            
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(simulate_user_created_webhook())
