import requests
import json

# Test the sync endpoint
url = "http://localhost:8000/api/v1/auth/test-sync"

try:
    response = requests.post(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Also check if any users exist
print("\n" + "="*50)
print("Checking database...")
print("="*50)

import asyncio
import asyncpg

async def check_db():
    conn = await asyncpg.connect(
        'postgresql://neondb_owner:npg_mIqbMEV8TuG0@ep-super-mud-adzd7g4h-pooler.c-2.us-east-1.aws.neon.tech/exadb',
        ssl='require'
    )
    
    users = await conn.fetch("SELECT id, clerk_user_id, email, username FROM users")
    print(f"\nUsers in database: {len(users)}")
    for user in users:
        print(f"  - {user['email']} (clerk_id: {user['clerk_user_id']})")
    
    sessions = await conn.fetch("SELECT id, clerk_session_id, clerk_user_id, status FROM sessions")
    print(f"\nSessions in database: {len(sessions)}")
    for session in sessions:
        print(f"  - Session {session['clerk_session_id']} - Status: {session['status']}")
    
    await conn.close()

asyncio.run(check_db())
