# Clerk Authentication Integration Guide

## Overview

SMB Hub has been migrated from JWT-based authentication to **Clerk** authentication. Clerk provides enterprise-grade authentication with built-in support for:

- Email/password authentication
- Social OAuth (Google, GitHub, etc.)
- Multi-factor authentication (MFA)
- Email verification
- Password reset
- **Multi-tenant organizations** (critical for SMB Hub)

## Why Clerk?

1. **Native Multi-Tenancy**: Clerk Organizations map directly to our `tenant_id` requirement
2. **Security**: Industry-standard authentication without maintaining password hashing/JWT logic
3. **User Experience**: Pre-built UI components for auth flows
4. **Compliance**: GDPR, SOC 2 compliant out of the box

## Architecture

### Backend Changes

#### 1. User Model
- **Added**: `clerk_user_id` (unique identifier from Clerk)
- **Removed**: `hashed_password`, `is_verified`, `reset_otp`, `refresh_token`
- **Changed**: `username` is now optional (Clerk may not always provide it)

#### 2. Authentication Flow
```
Frontend (with Clerk.js) → Clerk Session Token → Backend Middleware → Verify JWT → Extract user_id + org_id
```

#### 3. Tenant Resolution
**CRITICAL**: `tenant_id` is derived from Clerk's `org_id` in the JWT token, **never** from client input.

```python
# In any protected route
@router.get("/api/v1/workitems")
async def get_workitems(
    tenant_id: RequiredTenantId,  # Auto-extracted from Clerk JWT
    db: AsyncSession = Depends(get_db)
):
    # tenant_id is guaranteed to come from authenticated token
    items = await WorkItemService.get_by_tenant(db, tenant_id)
    return items
```

## Setup Instructions

### 1. Create Clerk Application

1. Go to [Clerk Dashboard](https://dashboard.clerk.com/)
2. Create a new application
3. Enable **Organizations** in the dashboard
4. Note down:
   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)
   - **Webhook Signing Secret** (for webhook verification)

### 2. Configure Backend

Add to `.env` file:

```env
# Clerk Authentication
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies:
- `clerk-backend-api`: Official Clerk Python SDK
- `svix`: Webhook signature verification

### 4. Run Database Migration

```bash
# Apply the Clerk migration
alembic upgrade head
```

**WARNING**: This migration:
- Adds `clerk_user_id` column
- Removes password-related columns
- Marks existing users with placeholder IDs (`migrated_1`, etc.)

**For production**: Migrate existing users to Clerk first before running this migration.

### 5. Configure Clerk Webhooks

In Clerk Dashboard → Webhooks:

1. Add endpoint: `https://your-domain.com/api/v1/auth/clerk-webhook`
2. Subscribe to events:
   - `user.created`
   - `user.updated`
   - `user.deleted`
   - `organization.created` (future)
   - `organizationMembership.created` (future)
3. Copy the webhook signing secret to `CLERK_WEBHOOK_SECRET`

## Frontend Integration

### 1. Install Clerk React

```bash
npm install @clerk/clerk-react
```

### 2. Wrap App with ClerkProvider

```tsx
// app/layout.tsx or _app.tsx
import { ClerkProvider } from '@clerk/clerk-react'

const clerkPubKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

export default function RootLayout({ children }) {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      {children}
    </ClerkProvider>
  )
}
```

### 3. Add Authentication Components

```tsx
// pages/sign-in.tsx
import { SignIn } from '@clerk/clerk-react'

export default function SignInPage() {
  return <SignIn routing="path" path="/sign-in" />
}

// pages/sign-up.tsx
import { SignUp } from '@clerk/clerk-react'

export default function SignUpPage() {
  return <SignUp routing="path" path="/sign-up" />
}
```

### 4. Making Authenticated API Requests

```tsx
import { useAuth } from '@clerk/clerk-react'

function MyComponent() {
  const { getToken } = useAuth()
  
  const fetchData = async () => {
    const token = await getToken()
    
    const response = await fetch('http://localhost:8000/api/v1/workitems', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    
    return response.json()
  }
  
  // ...
}
```

### 5. Organization (Tenant) Selection

```tsx
import { useOrganization, OrganizationSwitcher } from '@clerk/clerk-react'

function Dashboard() {
  const { organization } = useOrganization()
  
  return (
    <div>
      {/* Org switcher for multi-tenant selection */}
      <OrganizationSwitcher />
      
      {organization ? (
        <div>Current tenant: {organization.name}</div>
      ) : (
        <div>Please select or create an organization</div>
      )}
    </div>
  )
}
```

## API Reference

### Protected Endpoints

All protected endpoints now use Clerk authentication:

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <clerk_session_token>
```

Response:
```json
{
  "id": 1,
  "clerk_user_id": "user_xxxxx",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "newsletter": false,
  "tenant_id": "org_xxxxx",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z"
}
```

### Dependency Injection Helpers

```python
from app.api.auth_deps import CurrentUser, CurrentUserId, RequiredTenantId

@router.get("/example")
async def example_route(
    current_user: CurrentUser,          # Full user object from DB
    user_id: CurrentUserId,             # Just the Clerk user ID
    tenant_id: RequiredTenantId,        # Requires org context (403 if none)
):
    # Use tenant_id for all queries
    pass
```

## Multi-Tenancy Enforcement

### Critical Rules

1. **Never accept `tenant_id` from client input**
   ```python
   # ❌ WRONG
   @router.post("/items")
   async def create_item(tenant_id: str, data: ItemCreate):
       pass
   
   # ✅ CORRECT
   @router.post("/items")
   async def create_item(
       tenant_id: RequiredTenantId,  # From auth token only
       data: ItemCreate
   ):
       pass
   ```

2. **Every database query must filter by tenant_id**
   ```python
   # For future WorkItem table
   items = await db.execute(
       select(WorkItem)
       .where(WorkItem.tenant_id == tenant_id)
   )
   ```

3. **Users without organization context**
   - Some routes may allow `Optional[str]` for `tenant_id`
   - Most business operations require `RequiredTenantId`
   - Frontend should prompt users to create/join an organization

## Migration from JWT

### For Existing Users

**Option 1: Invite to Clerk** (Recommended)
1. Export existing user emails
2. Invite them to Clerk via dashboard or API
3. Users set new passwords in Clerk
4. Webhook auto-creates local user records

**Option 2: Manual Migration**
1. Create Clerk users programmatically via Clerk API
2. Update local database with `clerk_user_id`
3. Notify users of authentication change

### Removed Features

These features are now handled by Clerk:
- ❌ `/api/v1/auth/request-signup`
- ❌ `/api/v1/auth/verify-email`
- ❌ `/api/v1/auth/complete-signup`
- ❌ `/api/v1/auth/login`
- ❌ `/api/v1/auth/refresh`
- ❌ `/api/v1/auth/forgot-password`
- ❌ `/api/v1/auth/verify-otp`
- ❌ `/api/v1/auth/reset-password`

### New Endpoints

- ✅ `GET /api/v1/auth/me` - Get current user
- ✅ `POST /api/v1/auth/clerk-webhook` - Clerk webhook handler
- ✅ `GET /api/v1/auth/health` - Health check

## Troubleshooting

### "No authentication token provided"
- Ensure frontend is sending `Authorization: Bearer <token>` header
- Check that Clerk session is active: `const { isSignedIn } = useAuth()`

### "This operation requires organization context"
- User needs to create or select an organization
- Use `<OrganizationSwitcher />` component in UI
- Check `organization` object: `const { organization } = useOrganization()`

### "Webhook verification failed"
- Verify `CLERK_WEBHOOK_SECRET` matches Clerk dashboard
- Ensure webhook URL is publicly accessible (use ngrok for local testing)
- Check webhook event logs in Clerk dashboard

### Auto-provisioning not working
- Check webhook is configured and accessible
- Verify database connection
- Check logs: `tail -f logs/app.log`

## Security Considerations

1. **Token Verification**: All tokens verified using Clerk's JWKS
2. **Organization Isolation**: Tenant ID from token only, never user input
3. **Webhook Signatures**: All webhooks verified using Svix
4. **Session Management**: Handled by Clerk (refresh tokens, etc.)

## Next Steps

1. **Add tenant-scoped models**: WorkItem, Invoice, Contact, etc.
2. **Implement RBAC**: Use Clerk roles + custom authorization
3. **Add organization settings**: Profile-driven configuration
4. **Build onboarding flow**: Guide users to create organizations

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk React SDK](https://clerk.com/docs/references/react/overview)
- [Clerk Backend API](https://clerk.com/docs/references/backend/overview)
- [Organizations Guide](https://clerk.com/docs/organizations/overview)
