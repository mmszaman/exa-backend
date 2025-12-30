# Local Webhook Testing Setup

## Problem
Clerk webhooks are configured to send to `https://api.exateks.com/webhook/clerk` (production), so your local server at `localhost:8000` never receives them.

## Solution: Use ngrok + Separate Dev Webhook

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com/download
# Or use winget
winget install ngrok
```

### Step 2: Start ngrok tunnel
```bash
# In a separate terminal
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok.io`

### Step 3: Create Dev Webhook in Clerk

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Navigate to **Webhooks** section
3. Click **Add Endpoint**
4. Configure:
   - **Endpoint URL**: `https://abc123.ngrok.io/webhook/clerk`
   - **Description**: "Local Development"
   - **Subscribe to events**:
     - ✓ user.created
     - ✓ user.updated
     - ✓ user.deleted
     - ✓ session.created
     - ✓ session.ended
     - ✓ session.removed
     - ✓ session.revoked
     - ✓ organization.created
     - ✓ organization.updated
     - ✓ organization.deleted

5. Click **Create**
6. Copy the **Signing Secret** (starts with `whsec_`)

### Step 4: Update .env
Add the dev webhook secret to your `.env` file:
```env
# For local development with ngrok
CLERK_WEBHOOK_SECRET=whsec_YOUR_DEV_SIGNING_SECRET_HERE
```

### Step 5: Test the webhook

1. Make sure your local server is running: `suvc`
2. Make sure ngrok is running: `ngrok http 8000`
3. In Clerk dashboard, go to your dev webhook and click **Send Example**
4. Check your terminal - you should see logs like:
   ```
   INFO - clerk_webhooks - ===== CLERK WEBHOOK RECEIVED =====
   INFO - clerk_webhooks - ✓ Webhook signature verified successfully
   INFO - clerk_webhooks - Processing Clerk webhook: user.created
   INFO - clerk_webhooks - Created user from Clerk: user_xxx
   ```

### Step 6: Test with real signup

1. Go to your frontend app
2. Sign up with a new user
3. Check your backend logs - you should see the webhook received
4. Check database - user should be created

---

## Production Setup

Keep your production webhook at:
- **URL**: `https://api.exateks.com/webhook/clerk`
- **Secret**: Your production `whsec_` secret (already configured)

This way you can test locally without affecting production!

## Troubleshooting

### ngrok URL changes
ngrok free tier gives you a new URL each time you restart. When this happens:
1. Get new ngrok URL
2. Update Clerk dev webhook endpoint URL
3. Restart test

### Webhook not received
1. Check ngrok is running: `ngrok http 8000`
2. Check local server is running: `suvc`
3. Check Clerk webhook endpoint URL matches ngrok URL
4. Check webhook secret in `.env` matches Clerk signing secret

### 401/400 errors
- Webhook signature verification failed
- Make sure `CLERK_WEBHOOK_SECRET` in `.env` matches the signing secret from Clerk dashboard
