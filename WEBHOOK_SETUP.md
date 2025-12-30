# Clerk Webhook Configuration Guide

## Problem
User signed up but data is not syncing to database (users and sessions tables are empty).

## Root Cause
Clerk webhooks are not configured to send events to your backend endpoint.

## Solution

### Step 1: Configure Clerk Webhook Endpoint

1. Go to Clerk Dashboard: https://dashboard.clerk.com
2. Select your application
3. Navigate to: **Webhooks** (in the left sidebar)
4. Click **Add Endpoint**
5. Enter your webhook URL:
   ```
   https://api.exateks.com/api/v1/auth/clerk-webhook
   ```
   **IMPORTANT**: Note that your endpoint is `/api/v1/auth/clerk-webhook`, not `/webhook/clerk`

### Step 2: Subscribe to Events

Select these events to sync to your database:

**User Events** (Required):
- [x] user.created
- [x] user.updated  
- [x] user.deleted

**Session Events** (Required):
- [x] session.created
- [x] session.ended
- [x] session.removed
- [x] session.revoked

**Organization Events** (Optional but recommended):
- [x] organization.created
- [x] organization.updated
- [x] organization.deleted

### Step 3: Copy Webhook Secret

After creating the endpoint:
1. Clerk will show you the **Signing Secret**
2. Copy it and update your `.env` file:
   ```
   CLERK_WEBHOOK_SECRET=whsec_your_actual_secret_here
   ```

### Step 4: Test the Webhook

Option A: Use Clerk's "Send Example" button in the dashboard

Option B: Sign up a new test user through your application

Option C: Use the testing endpoint (while server is running):
```bash
curl -X POST http://localhost:8000/api/v1/auth/test-sync
```

### Step 5: Verify Data Sync

Check if users are being created:
```bash
.\venv\Scripts\python.exe -c "import asyncio; import asyncpg; async def check(): conn = await asyncpg.connect('postgresql://neondb_owner:npg_mIqbMEV8TuG0@ep-super-mud-adzd7g4h-pooler.c-2.us-east-1.aws.neon.tech/exadb', ssl='require'); users = await conn.fetch('SELECT * FROM users'); print(f'Users: {len(users)}'); await conn.close(); asyncio.run(check())"
```

## Current Webhook Endpoint Status

✅ Webhook handler implemented at: `/api/v1/auth/clerk-webhook`
✅ Database tables created: users, sessions, tenants
✅ Services implemented: UserService, SessionService, TenantService
✅ Logging enabled for debugging

⚠️  **ACTION REQUIRED**: Configure Clerk webhook endpoint in dashboard

## Debugging

The webhook handler now includes extensive logging. When webhooks are received, you'll see:
```
===== CLERK WEBHOOK RECEIVED =====
✓ Webhook signature verified successfully
Created user from Clerk: user_xxxxx
Created session: sess_xxxxx for user: user_xxxxx
```

Check logs at: Server console output

## Alternative: Manual User Sync (Temporary)

If you can't wait for webhook configuration, you can manually sync existing users:

1. Get user data from Clerk API
2. Call the test endpoint to create users manually
3. Or use the Clerk SDK to fetch and sync users in bulk

## Important Notes

- Webhook signature verification is currently set to allow requests even if verification fails (for debugging)
- Once confirmed working, remove the debug bypass in auth.py
- The webhook URL must be publicly accessible (https://api.exateks.com)
- Local development (localhost) won't receive Clerk webhooks - use ngrok or similar for local testing
