# Quick Start: Clerk Organizations Integration

## Summary
The tenant management system now uses Clerk Organizations as the source of truth. All new tenants are created in Clerk first, then synced to the local database.

## Key Changes

### ✅ Completed
1. **Database**: Added `clerk_org_id` column to tenants table (nullable, unique, indexed)
2. **Service Layer**: Added 3 new methods for Clerk integration
3. **API Endpoints**: Updated create and list endpoints to use Clerk
4. **Schema**: Added `clerkOrgId` to API responses

### 🔄 How It Works Now

#### Creating Organizations
```python
# Old way (deprecated)
tenant = await TenantService.create_tenant(db, tenant_data)

# New way (recommended)
tenant = await TenantService.create_tenant_from_clerk(
    db=db,
    clerk_org_id=None,
    clerk_user_id=current_user.clerk_user_id,
    tenant_data=tenant_data
)
```

#### Fetching Organizations
```python
# Automatically syncs from Clerk before returning
GET /api/v1/tenants/me/get-tenants?sync_from_clerk=true

# Skip Clerk sync (use local DB only)
GET /api/v1/tenants/me/get-tenants?sync_from_clerk=false
```

## API Changes

### POST /api/v1/tenants/create
- Now creates organization in Clerk first
- User automatically added as admin in Clerk
- Returns tenant with `clerkOrgId` populated
- Throws 500 if Clerk API fails

### GET /api/v1/tenants/me/get-tenants
- **New param**: `sync_from_clerk` (default: true)
- Syncs user's orgs from Clerk before returning
- Gracefully falls back to DB if Clerk fails
- Returns sorted list (primary org first)

## New Service Methods

### TenantService.create_tenant_from_clerk()
Creates org in Clerk, syncs to DB
```python
tenant = await TenantService.create_tenant_from_clerk(
    db=db,
    clerk_org_id=None,  # Auto-created
    clerk_user_id="user_xxx",
    tenant_data=tenant_input
)
```

### TenantService.get_or_sync_from_clerk()
Gets tenant by Clerk org ID, syncs if not in DB
```python
tenant = await TenantService.get_or_sync_from_clerk(
    db=db,
    clerk_org_id="org_xxx"
)
```

### TenantService.sync_user_tenants_from_clerk()
Syncs all user's orgs from Clerk
```python
tenants = await TenantService.sync_user_tenants_from_clerk(
    db=db,
    clerk_user_id="user_xxx"
)
```

## Clerk Helper Functions

Located in `app/core/clerk_auth.py`:

```python
# Get org from Clerk
org_data = await get_clerk_org("org_xxx")

# Create org in Clerk
org_data = await create_clerk_org(
    name="My Company",
    created_by="user_xxx",
    slug="my-company"  # optional
)

# Get user's orgs from Clerk
orgs = await get_user_clerk_orgs("user_xxx")

# Sync org to DB
tenant = await sync_clerk_org_to_db(
    db=db,
    clerk_org_id="org_xxx",
    clerk_org_data=org_data  # optional
)
```

## Migration Notes

### Existing Tenants
- Old tenants have `clerk_org_id = NULL`
- They continue to work normally
- No immediate action required
- Can migrate later if needed

### New Tenants
- All created through Clerk
- `clerk_org_id` always populated
- Linked to Clerk organization

## Testing

### Before Server Start
```powershell
# Install dependencies (if not already)
pip install -r requirements.txt

# Run migration
venv\Scripts\python -m alembic upgrade head

# Verify CLERK_SECRET_KEY in .env
```

### Test Create Org
```bash
POST http://localhost:8000/api/v1/tenants/create
{
  "name": "Test Company"
}
```

Expected response includes:
```json
{
  "clerkOrgId": "org_xxxxxxxxxxxxx",
  "name": "Test Company",
  ...
}
```

### Test List Orgs
```bash
GET http://localhost:8000/api/v1/tenants/me/get-tenants?sync_from_clerk=true
```

Should return orgs from Clerk.

## Troubleshooting

### Error: "Failed to create organization"
- Check CLERK_SECRET_KEY in .env
- Verify Clerk API is accessible
- Check server logs for detailed error

### Tenants not syncing from Clerk
- Ensure `sync_from_clerk=true` query param
- Check user has org memberships in Clerk
- Verify CLERK_SECRET_KEY is correct

### Legacy tenants without clerkOrgId
- This is normal for pre-migration data
- They will work but won't sync from Clerk
- Can be migrated manually if needed

## Next Steps

### Recommended
1. Test create endpoint with Clerk
2. Test list endpoint with sync
3. Monitor server logs for Clerk API errors
4. Consider adding webhook handlers for org updates

### Optional
- Add bulk migration script for old tenants
- Implement caching for Clerk org data
- Add retry logic for Clerk API calls
- Set up monitoring for sync failures

## Files Changed

### Core Files
- [app/models/tenant.py](../app/models/tenant.py) - Added clerk_org_id field
- [app/services/tenant_service.py](../app/services/tenant_service.py) - Added 3 new methods
- [app/api/v1/tenant.py](../app/api/v1/tenant.py) - Updated create/list endpoints
- [app/schemas/tenant_schema.py](../app/schemas/tenant_schema.py) - Added clerkOrgId
- [app/core/clerk_auth.py](../app/core/clerk_auth.py) - Added 4 helper functions

### Migration
- [alembic/versions/a607aeb66854_add_clerk_org_id_to_tenants.py](../alembic/versions/a607aeb66854_add_clerk_org_id_to_tenants.py)

### Documentation
- [docs/CLERK_ORGANIZATION_INTEGRATION.md](CLERK_ORGANIZATION_INTEGRATION.md)
- [docs/CLERK_ORGANIZATIONS_QUICK_START.md](CLERK_ORGANIZATIONS_QUICK_START.md) (this file)

## Support

For detailed information, see [CLERK_ORGANIZATION_INTEGRATION.md](CLERK_ORGANIZATION_INTEGRATION.md).

For Clerk API documentation: https://clerk.com/docs/organizations/overview
