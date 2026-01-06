# Schema Refactoring Summary

## Overview
This document summarizes the major schema refactoring completed in migration `4e27efd6c84b_major_schema_refactor_bigint_uuid_.py`.

## Key Changes

### 1. ID Type Changes
- **Changed all primary keys from `Integer` to `BigInteger`**
  - Affected tables: tenants, users, memberships, businesses, products, subscriptions
  - Provides support for larger datasets (2^63-1 vs 2^31-1 values)

### 2. UUID Public IDs
- **Added `public_id` UUID column to all main tables**
  - Auto-generated using PostgreSQL's `uuid_generate_v4()` function
  - Provides externally-safe, non-sequential identifiers for API responses
  - Indexed for fast lookups
  - Tables: tenants, users, memberships, businesses, products, subscriptions, billing_profiles, invoices, payments

### 3. Soft Deletes
- **Added `deleted_at` timestamp column**
  - Enables soft-delete functionality across the application
  - Indexed for efficient filtering of active records
  - Tables: tenants, users, memberships, businesses, products, subscriptions, billing_profiles

### 4. JSON to JSONB Migration
- **Upgraded all JSON columns to JSONB**
  - Better performance for JSON operations
  - Supports indexing on JSON fields
  - Native binary storage format
  - Columns: settings, features, clerk_metadata, permissions, address, limits, features_snapshot, etc.

### 5. New Enum Types
Created PostgreSQL enum types for better data integrity:
- `tenantstatus`: 'active', 'inactive', 'suspended', 'trial'
- `membershiprole`: 'owner', 'admin', 'member', 'viewer'
- `businesstype`: 'llc', 'corporation', 'partnership', 'sole_proprietorship', 'nonprofit', 'other'
- `businessstatus`: 'active', 'inactive', 'pending', 'suspended'
- `subscriptionstatus`: 'active', 'trialing', 'past_due', 'canceled', 'expired'
- `invoicestatus`: 'draft', 'open', 'paid', 'void', 'uncollectible'
- `paymentstatus`: 'pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded'

### 6. Removed Models
- **Deleted `SessionModel` and `UserHistoryModel`**
  - Session management moved to Clerk
  - User history functionality to be reimplemented differently

### 7. New Billing System
Created comprehensive billing infrastructure with 7 new tables:

#### BillingProfiles
- One-to-one relationship with tenants
- Stores Stripe customer information
- Manages payment methods and billing addresses

#### Invoices
- Tracks all invoices for tenants
- Links to billing profiles and subscriptions
- Stores amounts, status, and payment due dates

#### InvoiceLineItems
- Individual line items for invoices
- Quantity, unit price, and total amount
- Metadata stored as JSONB

#### Payments
- Payment transaction records
- Links to invoices and billing profiles
- Tracks payment status and methods

#### BillingCredits
- Store credits for tenants
- Expiration dates
- Reason tracking

#### UsageRecords
- Metered billing support
- Tracks usage by metric
- Links to subscriptions

### 8. Updated Core Models

#### TenantModel
- Removed: `stripe_customer_id`, `billing_email`, `trial_ends_at`, `subscription_ends_at`, `plan`, `limits`
- Added: `public_id` (UUID), `status` (enum), `deleted_at`, `logo_url`, `brand`, `settings` (JSONB), `features` (JSONB)
- Reasoning: Billing information moved to BillingProfile for better separation of concerns

#### UserModel
- Removed: `role`, `sessions` relationship
- Added: `public_id` (UUID), `deleted_at`, `brand`, `lead_source`, `referral_code`, `utm_*` fields, `newsletter`, `email_notifications`, `marketing_emails`
- Changed: `metadata` → `clerk_metadata` (JSONB)

#### MembershipModel
- Changed: `role` to use `membershiprole` enum
- Added: `public_id` (UUID), `permissions` (JSONB), `deleted_at`

#### BusinessModel
- Changed: `created_by`/`updated_by` → `owner_user_id` (FK to users)
- Changed: `logo` → `logo_url`
- Added: `public_id` (UUID), `deleted_at`

#### ProductModel
- Added: `public_id` (UUID), `version`, `is_current`, `limits` (JSONB), `deleted_at`
- Supports product versioning for plan evolution

#### SubscriptionModel
- Added: `public_id` (UUID), `billing_profile_id` (FK), `status` (enum), `price_monthly`, `price_yearly`, `features_snapshot` (JSONB), `limits_snapshot` (JSONB), `deleted_at`
- Snapshots preserve product configuration at subscription time

## Field Name Changes

| Model | Old Name | New Name | Reason |
|-------|----------|----------|--------|
| Business | `logo` | `logo_url` | Clarity - it's a URL not binary data |
| Business | `created_by` | `owner_user_id` | Clearer semantics |
| Business | `updated_by` | _removed_ | Rely on updated_at timestamp |
| User | `metadata` | `clerk_metadata` | Avoid SQLAlchemy reserved word |
| InvoiceLineItem | `metadata` | `line_metadata` | Avoid SQLAlchemy reserved word |

## Schema Updates Summary

### Updated Files
1. `app/models/user.py` - BigInteger IDs, UUID, JSONB, new marketing fields
2. `app/models/tenant.py` - BigInteger IDs, UUID, status enum, removed billing fields
3. `app/models/membership.py` - BigInteger IDs, UUID, role enum, permissions
4. `app/models/business.py` - BigInteger IDs, UUID, owner_user_id, logo_url
5. `app/models/product.py` - BigInteger IDs, UUID, versioning, limits
6. `app/models/subscription.py` - BigInteger IDs, UUID, status enum, snapshots
7. `app/models/billing.py` - NEW FILE - 7 billing models
8. `app/schemas/business_schema.py` - Updated for logo_url, public_id, owner_user_id
9. `app/services/business_service.py` - Updated for new field names

### Migration Details
- **Migration ID**: `4e27efd6c84b`
- **Previous Migration**: `cf058fa7d0de`
- **Type**: Breaking change - drops and recreates all tables
- **UUID Extension**: Enabled `uuid-ossp` PostgreSQL extension

## Breaking Changes

⚠️ **WARNING: This migration drops all existing data!**

For production deployment, you would need to:
1. Create a data migration script to preserve existing data
2. Use ALTER TABLE statements instead of DROP/CREATE
3. Implement a phased rollout strategy

## Benefits

1. **Scalability**: BigInteger PKs support massive growth
2. **Security**: UUID public IDs prevent enumeration attacks
3. **Performance**: JSONB enables efficient JSON queries
4. **Data Integrity**: Enums prevent invalid status values
5. **Audit Trail**: Soft deletes preserve historical data
6. **Billing Flexibility**: Dedicated billing models support complex scenarios
7. **Multi-tenancy**: Clean separation of billing per tenant

## Next Steps

1. ✅ Migration applied successfully
2. ✅ All models updated
3. ✅ Business API updated
4. ✅ No errors detected
5. 🔄 Update remaining API endpoints to use `public_id` in responses
6. 🔄 Implement soft-delete filtering in all services
7. 🔄 Add billing service layer for new billing models
8. 🔄 Update API documentation to reflect new schema

## Testing Checklist

- [x] Migration runs without errors
- [x] App imports successfully
- [x] No Python errors detected
- [ ] Business API endpoints tested
- [ ] UUID public_ids returned in responses
- [ ] Soft delete functionality verified
- [ ] Enum values validated
- [ ] JSONB fields functional
- [ ] Billing models relationship tested

## Notes

- The migration creates all enum types explicitly before table creation
- UUID extension is enabled automatically
- All timestamps use `timezone=True` for proper UTC handling
- Indexes created on commonly queried fields (tenant_id, status, public_id, etc.)
- Foreign key constraints ensure referential integrity
- Cascade deletes configured where appropriate
