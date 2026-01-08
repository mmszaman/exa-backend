# Clerk Organization Integration

## Overview
This document describes the integration of Clerk Organizations with the tenant management system. The integration makes Clerk the source of truth for organizations while maintaining a local database mirror for performance and relational data.

## Migration Strategy
- **Approach**: Gradual migration with nullable `clerk_org_id` field
- **Backward Compatibility**: Existing tenants without Clerk org IDs continue to work
- **Forward Path**: All new tenants are created in Clerk first, then synced to DB

## Database Changes

### Migration: a607aeb66854_add_clerk_org_id_to_tenants
- Added `clerk_org_id` column to `tenants` table
- Type: `VARCHAR(255)`, nullable, unique, indexed
- Purpose: Links local tenant record to Clerk organization

### TenantModel Changes
- **New Field**: `clerk_org_id` - Stores Clerk organization ID
- **Constraint**: Unique to ensure one-to-one mapping
- **Index**: Added for fast lookups by Clerk org ID

## Schema Changes

### Tenant Response Schema
```python
clerk_org_id: Optional[str] = Field(None, alias="clerkOrgId")
```
- Exposed in API responses as `clerkOrgId`
- Nullable for backward compatibility with legacy tenants

## Service Layer Changes

### New Methods in TenantService

#### 1. `create_tenant_from_clerk()`
Primary method for creating new tenants:
- Creates organization in Clerk first
- Syncs Clerk org data to local database
- Updates additional fields not in Clerk
- Returns fully populated tenant record

**Flow**:
1. Call `create_clerk_org()` with name, creator, and optional slug
2. Receive Clerk org ID
3. Call `sync_clerk_org_to_db()` to create local record
4. Update additional fields (legal_name, tax_id, etc.)
5. Return tenant

#### 2. `get_or_sync_from_clerk()`
Retrieves tenant by Clerk org ID:
- First checks local database
- If not found, fetches from Clerk and syncs
- Ensures eventual consistency

**Use Case**: When receiving Clerk webhooks or external org references

#### 3. `sync_user_tenants_from_clerk()`
Syncs all of a user's organizations from Clerk:
- Fetches user's org memberships from Clerk API
- Syncs each organization to local database
- Returns list of tenant records

**Use Case**: Bulk sync during user login or tenant list retrieval

### Updated Legacy Method

#### `create_tenant()`
- Added optional `clerk_org_id` parameter
- Maintains backward compatibility
- Use `create_tenant_from_clerk()` for new implementations

## API Endpoint Changes

### POST /api/v1/tenants/create

**Before**:
```python
tenant = await TenantService.create_tenant(db, tenant_data)
```

**After**:
```python
tenant = await TenantService.create_tenant_from_clerk(
    db=db,
    clerk_org_id=None,
    clerk_user_id=current_user.clerk_user_id,
    tenant_data=tenant_data
)
```

**Changes**:
- Creates organization in Clerk first
- User automatically added as admin in Clerk org
- Syncs Clerk org to local DB
- Creates membership record for owner role
- Full error handling with rollback

### GET /api/v1/tenants/me/get-tenants

**New Query Parameters**:
- `sync_from_clerk`: bool (default: True) - Sync from Clerk before returning
- `active_only`: bool (default: True) - Filter by active memberships

**Flow**:
1. If `sync_from_clerk=True`, fetch and sync user's orgs from Clerk
2. Query local membership records
3. Return sorted tenant list (primary first)
4. Fallback to DB-only on Clerk API errors

**Error Handling**:
- Graceful degradation if Clerk API is unavailable
- Falls back to local database records
- Logs errors for monitoring

## Clerk Integration Functions

All Clerk API interactions are centralized in [app/core/clerk_auth.py](../app/core/clerk_auth.py):

### 1. `get_clerk_org(org_id: str)`
- Fetches organization from Clerk API
- Returns dict with id, name, slug, metadata
- Used for syncing existing orgs

### 2. `create_clerk_org(name, created_by, slug)`
- Creates new organization in Clerk
- Adds creator as admin member
- Returns created org data
- Used when creating new tenants

### 3. `get_user_clerk_orgs(user_id: str)`
- Fetches all organizations for a user
- Includes role information
- Returns list of org data dicts
- Used for bulk sync operations

### 4. `sync_clerk_org_to_db(db, clerk_org_id, clerk_org_data)`
- Core sync function
- Creates or updates local tenant record
- Maps Clerk fields to tenant model
- Returns tenant record

## Data Flow

### Creating a New Organization
```
User Request → API Endpoint
    ↓
create_tenant_from_clerk()
    ↓
create_clerk_org() → Clerk API
    ↓
sync_clerk_org_to_db() → Local DB
    ↓
create_membership() → Local DB
    ↓
Return Tenant
```

### Fetching User's Organizations
```
User Request → API Endpoint
    ↓
sync_user_tenants_from_clerk()
    ↓
get_user_clerk_orgs() → Clerk API
    ↓
For each org:
  sync_clerk_org_to_db() → Local DB
    ↓
Query memberships → Local DB
    ↓
Return Tenants
```

## Error Handling

### Clerk API Errors
- All Clerk API calls wrapped in try-catch
- Detailed logging of errors
- Fallback to local DB when possible
- HTTP 500 with descriptive error messages

### Migration Safety
- Nullable `clerk_org_id` prevents breaking existing data
- Legacy tenants continue to work without Clerk org
- Gradual migration path available

## Testing Recommendations

### Unit Tests
- Test `create_tenant_from_clerk()` with mocked Clerk API
- Test `sync_clerk_org_to_db()` with various org data
- Test error handling for Clerk API failures

### Integration Tests
- Test full tenant creation flow
- Test tenant list sync from Clerk
- Test backward compatibility with legacy tenants
- Test error fallback scenarios

### E2E Tests
- Create org through API, verify in Clerk and DB
- List orgs, verify sync from Clerk
- Handle Clerk API downtime gracefully

## Environment Variables

Required in `.env`:
```bash
CLERK_SECRET_KEY=sk_test_...
```

Already configured in [app/core/config.py](../app/core/config.py).

## Dependencies

Required package (already in requirements.txt):
```
clerk-backend-api
```

## Future Enhancements

### Planned
- [ ] Webhook handler for Clerk org updates
- [ ] Sync org updates from Clerk to DB
- [ ] Delete/archive tenant when Clerk org is deleted
- [ ] Bulk migration script for existing tenants
- [ ] Admin endpoint to force sync from Clerk

### Considerations
- Rate limiting for Clerk API calls
- Caching layer for frequently accessed orgs
- Retry logic with exponential backoff
- Monitoring and alerting for sync failures

## Troubleshooting

### Tenant not syncing from Clerk
1. Check CLERK_SECRET_KEY in environment
2. Verify user has org membership in Clerk
3. Check application logs for Clerk API errors
4. Try calling with `sync_from_clerk=True` explicitly

### Legacy tenants without clerk_org_id
- These are older tenants created before migration
- They continue to work normally
- Can be migrated by creating corresponding Clerk org
- Migration script can be created if needed

### Clerk API rate limits
- Implement exponential backoff
- Add caching layer for org data
- Consider batch operations where possible

## References

- Clerk Organizations API: https://clerk.com/docs/organizations/overview
- clerk-backend-api SDK: https://github.com/clerk/clerk-sdk-python
- Migration file: [alembic/versions/a607aeb66854_add_clerk_org_id_to_tenants.py](../alembic/versions/a607aeb66854_add_clerk_org_id_to_tenants.py)
