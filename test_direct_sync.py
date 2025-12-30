"""
Direct test of user and session creation (bypassing webhook)
This verifies that the database services work correctly.
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.user_service import UserService
from app.services.tenant_service import SessionService
from datetime import datetime, timezone

async def test_direct_sync():
    print("\n" + "="*60)
    print("TESTING DIRECT DATABASE SYNC")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        try:
            # Test 1: Create a user
            print("\n1. Creating test user...")
            user = await UserService.create_from_clerk(
                db=db,
                clerk_user_id=f"test_user_{int(datetime.now().timestamp())}",
                email=f"testuser_{int(datetime.now().timestamp())}@example.com",
                username="testuser",
                full_name="Test User",
                tenant_id="org_test123",
                brand="smbhub",
                lead_source="direct",
                role="member"
            )
            print(f"   ✓ User created successfully!")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Clerk ID: {user.clerk_user_id}")
            print(f"   - Tenant: {user.tenant_id}")
            print(f"   - Brand: {user.brand}")
            
            # Test 2: Create a session for this user
            print("\n2. Creating test session...")
            session = await SessionService.create_or_update_session(
                db=db,
                clerk_session_id=f"sess_{int(datetime.now().timestamp())}",
                user_id=user.id,
                clerk_user_id=user.clerk_user_id,
                tenant_id=user.tenant_id,
                status="active",
                ip_address="127.0.0.1",
                device_type="desktop",
                browser="Chrome"
            )
            print(f"   ✓ Session created successfully!")
            print(f"   - ID: {session.id}")
            print(f"   - Clerk Session ID: {session.clerk_session_id}")
            print(f"   - Status: {session.status}")
            print(f"   - Device: {session.device_type}")
            
            # Test 3: Verify data in database
            print("\n3. Verifying database records...")
            import asyncpg
            conn = await asyncpg.connect(
                'postgresql://neondb_owner:npg_mIqbMEV8TuG0@ep-super-mud-adzd7g4h-pooler.c-2.us-east-1.aws.neon.tech/exadb',
                ssl='require'
            )
            
            users = await conn.fetch("SELECT COUNT(*) as count FROM users")
            sessions_count = await conn.fetch("SELECT COUNT(*) as count FROM sessions")
            
            print(f"   ✓ Total users in database: {users[0]['count']}")
            print(f"   ✓ Total sessions in database: {sessions_count[0]['count']}")
            
            # Show recent users
            recent_users = await conn.fetch(
                "SELECT email, clerk_user_id, brand, lead_source, created_at "
                "FROM users ORDER BY created_at DESC LIMIT 5"
            )
            print(f"\n   Recent users:")
            for u in recent_users:
                print(f"     - {u['email']} (Brand: {u['brand']}, Source: {u['lead_source']})")
            
            await conn.close()
            
            print("\n" + "="*60)
            print("✓ ALL TESTS PASSED - Database sync is working!")
            print("="*60)
            print("\nNext step: Configure Clerk webhook to auto-sync users")
            print("See WEBHOOK_SETUP.md for instructions")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_sync())
