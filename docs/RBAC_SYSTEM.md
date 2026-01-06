# RBAC System Documentation

## Overview
Production-ready, multi-tenant Role-Based Access Control (RBAC) system with support for:
- Global permissions catalog
- Tenant-scoped roles (system + custom)
- Role-permission mappings with ABAC conditions
- Member role assignments with tracking
- Member permission overrides
- Teams for organizational hierarchy
- Team roles for inherited access
- Resource-level grants (object-level access control)

## Architecture

### Design Improvements Applied
1. **Comprehensive Indexing**: Added indexes on all FK columns and frequently queried fields
2. **Proper Constraints**: UniqueConstraints and CheckConstraints for data integrity
3. **Soft Deletes**: `deleted_at` columns where appropriate for audit trails
4. **Relationship Tracking**: `assigned_by_user_id`, `created_by_user_id` for accountability
5. **Temporal Tracking**: `assigned_at`, `revoked_at`, `joined_at`, `left_at` for lifecycle management
6. **JSONB for Flexibility**: `conditions` column supports future ABAC implementation
7. **Cascade Rules**: Proper cascade delete/set null configurations

## Models

### 1. PermissionModel (`permissions`)
**Purpose**: Global catalog of all available permissions

**Key Features**:
- Stable, centralized permission definitions
- Resource-action pattern (e.g., "contacts.read")
- Hierarchical organization by resource and action
- Can be activated/deactivated without deletion

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID for external references
- `key` - Unique identifier (e.g., "billing.invoice.pay")
- `name` - Human-readable name
- `description` - Detailed explanation
- `resource` - Resource category (e.g., "contacts", "billing")
- `action` - Action type (e.g., "read", "write", "delete")
- `is_active` - Enable/disable without deletion

**Indexes**:
- Primary key on `id`
- Unique on `public_id`, `key`
- Composite on `(resource, action)`
- Single on `is_active`, `resource`, `action`

### 2. RoleModel (`roles`)
**Purpose**: Tenant-scoped roles supporting both system and custom roles

**Key Features**:
- Multi-tenant isolation via `tenant_id`
- System roles (owner, admin, member, viewer) are predefined
- Custom roles can be created per tenant (e.g., "custom:ops_manager")
- Soft deletes for audit trail
- Unique constraint on `(tenant_id, key)`

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID
- `tenant_id` - FK to tenants (CASCADE delete)
- `key` - Role identifier
- `name` - Display name
- `description` - Role purpose
- `is_system` - True for built-in roles
- `is_active` - Enable/disable
- `deleted_at` - Soft delete timestamp

**Indexes**:
- Unique on `(tenant_id, key)`
- Composite on `(tenant_id, is_active)`
- Single on `is_system`, `deleted_at`

### 3. RolePermissionModel (`role_permissions`)
**Purpose**: Many-to-many mapping between roles and permissions

**Key Features**:
- Grant or deny permissions to roles
- Supports ABAC-like conditions in JSONB
- Effect field: "allow" | "deny" (deny takes precedence)
- Unique constraint prevents duplicate assignments

**Fields**:
- `id` - BigInteger primary key
- `role_id` - FK to roles (CASCADE)
- `permission_id` - FK to permissions (CASCADE)
- `effect` - "allow" or "deny"
- `conditions` - JSONB for conditional access

**Indexes**:
- Unique on `(role_id, permission_id)`
- Composite on `(role_id, effect)`

### 4. MemberRoleModel (`member_roles`)
**Purpose**: Assigns roles to tenant members

**Key Features**:
- Multiple roles per member supported
- Tracks who assigned the role
- Assignment/revocation timestamps
- Active status for temporary disabling
- Unique constraint prevents duplicate role assignments

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID
- `tenant_id` - FK to tenants (CASCADE)
- `membership_id` - FK to memberships (CASCADE)
- `role_id` - FK to roles (CASCADE)
- `assigned_by_user_id` - FK to users (SET NULL)
- `is_active` - Enable/disable
- `assigned_at` - Assignment timestamp
- `revoked_at` - Revocation timestamp

**Indexes**:
- Unique on `(membership_id, role_id)`
- Composite on `(tenant_id, is_active)`, `(membership_id, is_active)`
- Single on `revoked_at`

### 5. MemberPermissionOverrideModel (`member_permission_overrides`)
**Purpose**: Per-member permission overrides without creating custom roles

**Key Features**:
- Grant or deny specific permissions to individuals
- Conditions support for fine-grained control
- Soft deletes
- Unique constraint per member-permission pair

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID
- `tenant_id` - FK to tenants (CASCADE)
- `membership_id` - FK to memberships (CASCADE)
- `permission_id` - FK to permissions (CASCADE)
- `effect` - "allow" or "deny"
- `conditions` - JSONB
- `deleted_at` - Soft delete

**Indexes**:
- Unique on `(membership_id, permission_id)`
- Composite on `(tenant_id, deleted_at)`, `(membership_id, deleted_at)`

### 6. TeamModel (`teams`)
**Purpose**: Organizational grouping layer (departments, squads, etc.)

**Key Features**:
- Tenant-scoped teams
- Slug-based URLs
- Tracks creator
- Soft deletes
- Unique slug per tenant

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID
- `tenant_id` - FK to tenants (CASCADE)
- `name` - Team name
- `slug` - URL-friendly identifier
- `description` - Team purpose
- `created_by_user_id` - FK to users (SET NULL)
- `deleted_at` - Soft delete

**Indexes**:
- Unique on `(tenant_id, slug)`
- Composite on `(tenant_id, deleted_at)`

### 7. TeamMemberModel (`team_members`)
**Purpose**: Links memberships to teams

**Key Features**:
- Tracks join/leave dates
- Active status
- Unique constraint prevents duplicate team membership
- Tenant isolation

**Fields**:
- `id` - BigInteger primary key
- `tenant_id` - FK to tenants (CASCADE)
- `team_id` - FK to teams (CASCADE)
- `membership_id` - FK to memberships (CASCADE)
- `is_active` - Active status
- `joined_at` - Join timestamp
- `left_at` - Leave timestamp

**Indexes**:
- Unique on `(team_id, membership_id)`
- Multiple composite indexes for queries

### 8. TeamRoleModel (`team_roles`)
**Purpose**: Assign roles at team level for inherited access

**Key Features**:
- Members inherit team roles
- Assignment tracking
- Revocation support
- Unique constraint per team-role pair

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID
- `tenant_id` - FK to tenants (CASCADE)
- `team_id` - FK to teams (CASCADE)
- `role_id` - FK to roles (CASCADE)
- `assigned_by_user_id` - FK to users (SET NULL)
- `is_active` - Active status
- `assigned_at` - Assignment timestamp
- `revoked_at` - Revocation timestamp

**Indexes**:
- Unique on `(team_id, role_id)`
- Composite on `(tenant_id, is_active)`, `(team_id, is_active)`
- Single on `revoked_at`

### 9. ResourceGrantModel (`resource_grants`)
**Purpose**: Object-level access control (row-level permissions)

**Key Features**:
- Polymorphic subject (membership or team)
- Polymorphic resource (any resource type)
- Uses UUID public_id for resource reference
- Access levels: "read", "write", "admin", "full"
- Conditions for fine-grained control
- Soft deletes

**Fields**:
- `id` - BigInteger primary key
- `public_id` - UUID
- `tenant_id` - FK to tenants (CASCADE)
- `subject_type` - "membership" or "team"
- `subject_id` - ID of subject
- `resource_type` - e.g., "business", "project", "contact"
- `resource_id` - UUID public_id of resource
- `access_level` - "read", "write", "admin", "full"
- `conditions` - JSONB
- `created_by_user_id` - FK to users (SET NULL)
- `deleted_at` - Soft delete

**Indexes**:
- Composite on `(subject_type, subject_id, deleted_at)`
- Composite on `(resource_type, resource_id, deleted_at)`
- Composite on `(tenant_id, subject_type, subject_id, resource_type)` for lookups

## Permission Resolution Order

When determining if a user has permission to perform an action:

1. **Check Member Permission Overrides** (highest priority)
   - If DENY → access denied
   - If ALLOW → access granted (skip further checks)

2. **Check Member Roles**
   - Aggregate all active roles assigned to the member
   - For each role, check role_permissions
   - If any role has DENY → access denied
   - If any role has ALLOW → continue to step 3

3. **Check Team Roles** (if member belongs to teams)
   - Aggregate all teams the member belongs to
   - For each team, get team_roles
   - For each team role, check role_permissions
   - If any has DENY → access denied
   - If any has ALLOW → access granted

4. **Check Resource Grants**
   - Check if member or their teams have grants for specific resource
   - Verify access_level is sufficient for the action

5. **Default** → Access denied (fail-safe)

## Usage Examples

### Creating System Roles
```python
# In a seed script
owner_role = RoleModel(
    tenant_id=tenant.id,
    key="owner",
    name="Owner",
    description="Full access to all resources",
    is_system=True,
    is_active=True
)
```

### Assigning Multiple Roles to a Member
```python
# Assign admin role
member_role_1 = MemberRoleModel(
    tenant_id=tenant.id,
    membership_id=membership.id,
    role_id=admin_role.id,
    assigned_by_user_id=current_user.id
)

# Assign billing manager role
member_role_2 = MemberRoleModel(
    tenant_id=tenant.id,
    membership_id=membership.id,
    role_id=billing_manager_role.id,
    assigned_by_user_id=current_user.id
)
```

### Creating a Team and Assigning Roles
```python
# Create team
sales_team = TeamModel(
    tenant_id=tenant.id,
    name="Sales Team",
    slug="sales-team",
    created_by_user_id=current_user.id
)

# Assign role to team
team_role = TeamRoleModel(
    tenant_id=tenant.id,
    team_id=sales_team.id,
    role_id=sales_role.id,
    assigned_by_user_id=current_user.id
)

# Add member to team
team_member = TeamMemberModel(
    tenant_id=tenant.id,
    team_id=sales_team.id,
    membership_id=membership.id
)
```

### Granting Resource-Level Access
```python
# Grant a specific member write access to a business
grant = ResourceGrantModel(
    tenant_id=tenant.id,
    subject_type="membership",
    subject_id=membership.id,
    resource_type="business",
    resource_id=business.public_id,
    access_level="write",
    created_by_user_id=current_user.id
)
```

### Permission Override Example
```python
# Deny a specific member from deleting contacts
override = MemberPermissionOverrideModel(
    tenant_id=tenant.id,
    membership_id=membership.id,
    permission_id=contacts_delete_permission.id,
    effect="deny"
)
```

## Database Migration

Migration: `aa9c09f95d55_add_rbac_models.py`

**Applied**: ✅ Successfully applied

Creates all 9 RBAC tables with:
- Proper foreign key constraints
- Comprehensive indexes for performance
- Unique constraints for data integrity
- Check constraints for valid enum values
- Soft delete support where appropriate

## Next Steps

1. **Create Permission Seeder**
   - Define standard permissions for all resources
   - Seed database with initial permission catalog

2. **Create Role Seeder**
   - Define system roles (owner, admin, member, viewer)
   - Assign default permissions to each role

3. **Implement Permission Service**
   - Check user permissions
   - Resolve effective permissions
   - Cache permission checks

4. **Create RBAC API Endpoints**
   - Role management (CRUD)
   - Permission assignment
   - Team management
   - Resource grants

5. **Add Permission Decorators**
   - `@require_permission("contacts.read")`
   - `@require_role("admin")`
   - `@require_access_level("business", business_id, "write")`

6. **Implement Permission Caching**
   - Cache user effective permissions
   - Invalidate on role/permission changes
   - Use Redis for distributed caching

## Performance Considerations

1. **Indexes**: All foreign keys and frequently queried columns are indexed
2. **Denormalization**: Consider caching effective permissions per user
3. **Batch Queries**: Use eager loading for permission checks
4. **Database Views**: Consider materialized views for complex permission queries
5. **Caching Strategy**: Cache permission resolution results with TTL

## Security Best Practices

1. **Fail-Safe**: Default to deny if no permission found
2. **Deny Priority**: DENY effect always overrides ALLOW
3. **Audit Trail**: All assignments track who made them
4. **Soft Deletes**: Maintain history of access changes
5. **Tenant Isolation**: All queries must filter by tenant_id
6. **Public IDs**: Use UUIDs for external references to prevent enumeration

## Scalability Features

1. **Multi-Tenant**: Full isolation at database level
2. **Custom Roles**: Unlimited tenant-specific roles
3. **Hierarchical Teams**: Support for complex org structures
4. **Resource Grants**: Efficient object-level permissions
5. **ABAC Ready**: Conditions column supports attribute-based access
6. **Indexed Lookups**: Optimized for common permission check patterns
