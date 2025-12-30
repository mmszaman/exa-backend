"""
Diagnostic: Check webhook flow manually
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.user_service import UserService
from app.core.logger import get_logger

logger = get_logger("diagnostic")

async def test_webhook_flow():
    # Create database engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # Simulate creating a user like the webhook would
            logger.info("Testing user creation via webhook flow...")
            
            user = await UserService.create_from_clerk(
                db=db,
                clerk_user_id="user_webhook_test_123",
                email="webhooktest@example.com",
                username="webhooktest",
                full_name="Webhook Test User",
                avatar_url=None,
                phone_number=None,
                lead_source="clerk_webhook",
                brand="smbhub",
                referral_code=None,
                utm_source=None,
                utm_medium=None,
                utm_campaign=None,
                clerk_metadata="{}"
            )
            
            logger.info(f"✓ User created successfully: {user.id}, {user.email}")
            
            # Verify user was created
            fetched = await UserService.get_user_by_clerk_id(db, "user_webhook_test_123")
            if fetched:
                logger.info(f"✓ User verified in database: {fetched.email}")
            else:
                logger.error("✗ User not found after creation!")
            
        except Exception as e:
            logger.error(f"✗ Error during webhook flow test: {str(e)}", exc_info=True)
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_webhook_flow())
