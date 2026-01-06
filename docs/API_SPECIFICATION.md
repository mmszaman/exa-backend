# SMB Backend - API Specification

**Version:** 1.0  
**Last Updated:** January 4, 2026  
**Base URL:** `https://your-domain.com/api/v1`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Database Models](#database-models)
3. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication-endpoints)
   - [Tenants](#tenant-endpoints)
   - [Businesses](#business-endpoints)
   - [Email](#email-endpoints)
4. [Error Responses](#error-responses)
5. [Data Types & Enums](#data-types--enums)

---

## Authentication

All API requests require authentication using Clerk JWT tokens.

### Headers
```
Authorization: Bearer <clerk-jwt-token>
```

### JWT Claims
- `sub`: Clerk user ID
- `org_id`: Clerk organization ID (required for tenant-scoped operations)
- `exp`: Token expiration timestamp

---

## Database Models

### 1. User Model

**Table:** `users`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `clerkUserId` | String(255) | Clerk user ID | ✓ |
| `email` | String(255) | Email address | ✓ |
| `username` | String(255) | Username | - |
| `fullName` | String(255) | Full name | - |
| `avatarUrl` | String(500) | Profile picture URL | - |
| `phoneNumber` | String(50) | Phone number | - |
| `isActive` | Boolean | Account status | ✓ (default: true) |
| `leadSource` | String(100) | Marketing source | - |
| `brand` | String(100) | Brand identifier | - |
| `referralCode` | String(50) | Referral code | - |
| `utmSource` | String(100) | UTM source | - |
| `utmMedium` | String(100) | UTM medium | - |
| `utmCampaign` | String(100) | UTM campaign | - |
| `newsletter` | Boolean | Newsletter subscription | ✓ (default: false) |
| `emailNotifications` | Boolean | Email notifications enabled | ✓ (default: true) |
| `marketingEmails` | Boolean | Marketing emails enabled | ✓ (default: false) |
| `clerkMetadata` | JSONB | Clerk metadata | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `lastLoginAt` | DateTime (TZ) | Last login timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `clerkUserId` (unique)
- `email` (unique)
- `username` (unique)
- `isActive`
- `brand`, `leadSource`

---

### 2. Tenant Model

**Table:** `tenants`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `clerkOrgId` | String(255) | Clerk organization ID | ✓ |
| `name` | String(255) | Organization name | ✓ |
| `slug` | String(255) | URL-friendly identifier | ✓ |
| `logoUrl` | String(500) | Logo URL | - |
| `brand` | String(100) | Brand identifier | - |
| `email` | String(255) | Contact email | - |
| `phone` | String(50) | Contact phone | - |
| `website` | String(255) | Website URL | - |
| `status` | Enum | Tenant status (active/inactive/suspended/trial) | ✓ |
| `settings` | JSONB | Tenant settings | - |
| `features` | JSONB | Feature flags | - |
| `clerkMetadata` | JSONB | Clerk metadata | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `clerkOrgId` (unique)
- `slug` (unique)
- `name`
- `status`
- `brand`, `status` (composite)

**Status Values:**
- `active`: Active tenant
- `inactive`: Inactive tenant
- `suspended`: Suspended tenant
- `trial`: Trial period

---

### 3. Membership Model

**Table:** `memberships`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `userId` | BigInteger | FK to users | ✓ |
| `role` | Enum | Member role (owner/admin/member/viewer) | ✓ |
| `permissions` | JSONB | Custom permissions | - |
| `isActive` | Boolean | Membership status | ✓ (default: true) |
| `joinedAt` | DateTime (TZ) | Join timestamp | ✓ |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `userId`, `tenantId` (unique composite)
- `tenantId`
- `userId`
- `role`
- `isActive`

**Role Values:**
- `owner`: Tenant owner
- `admin`: Administrator
- `member`: Regular member
- `viewer`: Read-only access

---

### 4. Business Model

**Table:** `businesses`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `ownerUserId` | BigInteger | FK to users | - |
| `name` | String(255) | Business name | ✓ |
| `legalName` | String(255) | Legal business name | ✓ |
| `type` | Enum | Business type | ✓ |
| `status` | Enum | Business status | ✓ |
| `taxId` | String(50) | Tax ID / EIN | - |
| `email` | String(255) | Business email | ✓ |
| `phone` | String(50) | Business phone | ✓ |
| `website` | String(255) | Website URL | - |
| `address` | JSONB | Business address | ✓ |
| `logoUrl` | String(500) | Logo URL | - |
| `description` | Text | Business description | - |
| `industry` | String(100) | Industry | - |
| `employeeCount` | BigInteger | Number of employees | - |
| `foundedYear` | BigInteger | Year founded | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `tenantId`, `status` (composite)
- `tenantId`, `type` (composite)
- `tenantId`
- `ownerUserId`
- `email`
- `name`
- `type`
- `status`

**Type Values:**
- `llc`: Limited Liability Company
- `corporation`: Corporation
- `partnership`: Partnership
- `sole_proprietorship`: Sole Proprietorship
- `nonprofit`: Nonprofit Organization
- `other`: Other

**Status Values:**
- `active`: Active business
- `inactive`: Inactive business
- `pending`: Pending verification
- `suspended`: Suspended business

**Address Schema (JSONB):**
```json
{
  "street": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001",
  "country": "USA"
}
```

---

### 5. Product Model

**Table:** `products`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `code` | String(50) | Product code | ✓ |
| `name` | String(100) | Product name | ✓ |
| `description` | String(500) | Product description | - |
| `version` | BigInteger | Version number | ✓ (default: 1) |
| `isCurrent` | Boolean | Current version flag | ✓ (default: true) |
| `priceMonthly` | Numeric(10,2) | Monthly price | - |
| `priceYearly` | Numeric(10,2) | Yearly price | - |
| `currency` | String(10) | Currency code | ✓ (default: USD) |
| `features` | JSONB | Product features | - |
| `limits` | JSONB | Product limits | - |
| `stripeProductId` | String(255) | Stripe product ID | - |
| `stripePriceMonthlyId` | String(255) | Stripe monthly price ID | - |
| `stripePriceYearlyId` | String(255) | Stripe yearly price ID | - |
| `isActive` | Boolean | Product status | ✓ (default: true) |
| `isPublic` | Boolean | Public visibility | ✓ (default: true) |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `code` (unique)
- `stripeProductId` (unique)
- `code`, `version` (composite)
- `isActive`, `isCurrent` (composite)

---

### 6. Subscription Model

**Table:** `subscriptions`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `billingProfileId` | BigInteger | FK to billing_profiles | - |
| `productId` | BigInteger | FK to products | ✓ |
| `status` | Enum | Subscription status | ✓ |
| `startsAt` | DateTime (TZ) | Start date | ✓ |
| `endsAt` | DateTime (TZ) | End date | - |
| `trialEndsAt` | DateTime (TZ) | Trial end date | - |
| `priceMonthly` | Numeric(10,2) | Monthly price | - |
| `priceYearly` | Numeric(10,2) | Yearly price | - |
| `featuresSnapshot` | JSONB | Features at subscription time | - |
| `limitsSnapshot` | JSONB | Limits at subscription time | - |
| `stripeSubscriptionId` | String(255) | Stripe subscription ID | - |
| `cancelAtPeriodEnd` | Boolean | Cancel at end flag | ✓ (default: false) |
| `canceledAt` | DateTime (TZ) | Cancellation timestamp | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `stripeSubscriptionId` (unique)
- `tenantId`, `status` (composite)
- `tenantId`
- `billingProfileId`
- `productId`

**Status Values:**
- `active`: Active subscription
- `trialing`: Trial period
- `past_due`: Payment overdue
- `canceled`: Canceled subscription
- `expired`: Expired subscription

---

### 7. RBAC Models

#### 7.1 Permission Model

**Table:** `permissions`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `key` | String(150) | Permission key (e.g., "contacts.read") | ✓ |
| `name` | String(200) | Permission name | ✓ |
| `description` | Text | Permission description | - |
| `resource` | String(100) | Resource type | ✓ |
| `action` | String(50) | Action type | ✓ |
| `isActive` | Boolean | Permission status | ✓ (default: true) |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |

**Indexes:**
- `publicId` (unique)
- `key` (unique)
- `resource`, `action` (composite)
- `isActive`

#### 7.2 Role Model

**Table:** `roles`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `key` | String(100) | Role key | ✓ |
| `name` | String(150) | Role name | ✓ |
| `description` | Text | Role description | - |
| `isSystem` | Boolean | System role flag | ✓ (default: false) |
| `isActive` | Boolean | Role status | ✓ (default: true) |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `tenantId`, `key` (unique composite)
- `tenantId`, `isActive` (composite)
- `isSystem`

#### 7.3 Role Permission Model

**Table:** `role_permissions`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `roleId` | BigInteger | FK to roles | ✓ |
| `permissionId` | BigInteger | FK to permissions | ✓ |
| `effect` | String(10) | Effect (allow/deny) | ✓ (default: allow) |
| `conditions` | JSONB | ABAC conditions | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |

**Indexes:**
- `roleId`, `permissionId` (unique composite)
- `roleId`, `effect` (composite)

#### 7.4 Member Role Model

**Table:** `member_roles`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `membershipId` | BigInteger | FK to memberships | ✓ |
| `roleId` | BigInteger | FK to roles | ✓ |
| `assignedByUserId` | BigInteger | FK to users | - |
| `isActive` | Boolean | Assignment status | ✓ (default: true) |
| `assignedAt` | DateTime (TZ) | Assignment timestamp | ✓ |
| `revokedAt` | DateTime (TZ) | Revocation timestamp | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |

**Indexes:**
- `publicId` (unique)
- `membershipId`, `roleId` (unique composite)
- `tenantId`, `isActive` (composite)
- `membershipId`, `isActive` (composite)

#### 7.5 Member Permission Override Model

**Table:** `member_permission_overrides`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `membershipId` | BigInteger | FK to memberships | ✓ |
| `permissionId` | BigInteger | FK to permissions | ✓ |
| `effect` | String(10) | Effect (allow/deny) | ✓ |
| `conditions` | JSONB | ABAC conditions | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `membershipId`, `permissionId` (unique composite)
- `tenantId`, `deletedAt` (composite)
- `membershipId`, `deletedAt` (composite)

#### 7.6 Team Model

**Table:** `teams`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `name` | String(150) | Team name | ✓ |
| `slug` | String(160) | URL-friendly identifier | ✓ |
| `description` | Text | Team description | - |
| `createdByUserId` | BigInteger | FK to users | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `tenantId`, `slug` (unique composite)
- `tenantId`, `deletedAt` (composite)

#### 7.7 Team Member Model

**Table:** `team_members`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `teamId` | BigInteger | FK to teams | ✓ |
| `membershipId` | BigInteger | FK to memberships | ✓ |
| `isActive` | Boolean | Membership status | ✓ (default: true) |
| `joinedAt` | DateTime (TZ) | Join timestamp | ✓ |
| `leftAt` | DateTime (TZ) | Leave timestamp | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |

**Indexes:**
- `teamId`, `membershipId` (unique composite)
- `tenantId`, `isActive` (composite)
- `teamId`, `isActive` (composite)
- `membershipId`, `isActive` (composite)

#### 7.8 Team Role Model

**Table:** `team_roles`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `teamId` | BigInteger | FK to teams | ✓ |
| `roleId` | BigInteger | FK to roles | ✓ |
| `assignedByUserId` | BigInteger | FK to users | - |
| `isActive` | Boolean | Assignment status | ✓ (default: true) |
| `assignedAt` | DateTime (TZ) | Assignment timestamp | ✓ |
| `revokedAt` | DateTime (TZ) | Revocation timestamp | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |

**Indexes:**
- `publicId` (unique)
- `teamId`, `roleId` (unique composite)
- `tenantId`, `isActive` (composite)
- `teamId`, `isActive` (composite)

#### 7.9 Resource Grant Model

**Table:** `resource_grants`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `subjectType` | String(20) | Subject type (membership/team) | ✓ |
| `subjectId` | BigInteger | Subject ID | ✓ |
| `resourceType` | String(50) | Resource type | ✓ |
| `resourceId` | UUID | Resource public ID | ✓ |
| `accessLevel` | String(30) | Access level (read/write/admin/full) | ✓ |
| `conditions` | JSONB | Access conditions | - |
| `createdByUserId` | BigInteger | FK to users | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `tenantId`, `deletedAt` (composite)
- `subjectType`, `subjectId`, `deletedAt` (composite)
- `resourceType`, `resourceId`, `deletedAt` (composite)
- `tenantId`, `subjectType`, `subjectId`, `resourceType` (composite)

---

### 8. Billing Models

#### 8.1 Billing Profile Model

**Table:** `billing_profiles`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants (unique) | ✓ |
| `provider` | String(50) | Payment provider | ✓ (default: stripe) |
| `stripeCustomerId` | String(255) | Stripe customer ID | - |
| `billingEmail` | String(255) | Billing email | - |
| `billingName` | String(255) | Billing name | - |
| `billingAddress` | JSONB | Billing address | - |
| `currency` | String(10) | Currency code | ✓ (default: USD) |
| `taxId` | String(100) | Tax ID | - |
| `taxExempt` | Boolean | Tax exempt flag | ✓ (default: false) |
| `defaultPaymentMethod` | String(255) | Default payment method ID | - |
| `paymentMethods` | JSONB | Payment methods | - |
| `providerMetadata` | JSONB | Provider metadata | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |
| `updatedAt` | DateTime (TZ) | Last update timestamp | - |
| `deletedAt` | DateTime (TZ) | Soft delete timestamp | - |

**Indexes:**
- `publicId` (unique)
- `tenantId` (unique)
- `stripeCustomerId` (unique)

#### 8.2 Invoice Model

**Table:** `invoices`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `billingProfileId` | BigInteger | FK to billing_profiles | - |
| `subscriptionId` | BigInteger | FK to subscriptions | - |
| `providerInvoiceId` | String(255) | Provider invoice ID | - |
| `status` | Enum | Invoice status | ✓ |
| `currency` | String(10) | Currency code | ✓ (default: USD) |
| `subtotalAmount` | Numeric(10,2) | Subtotal amount | ✓ (default: 0) |
| `taxAmount` | Numeric(10,2) | Tax amount | ✓ (default: 0) |
| `totalAmount` | Numeric(10,2) | Total amount | ✓ (default: 0) |
| `dueAt` | DateTime (TZ) | Due date | - |
| `paidAt` | DateTime (TZ) | Payment date | - |
| `invoicePdfUrl` | String(500) | PDF URL | - |
| `providerMetadata` | JSONB | Provider metadata | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |

**Indexes:**
- `publicId` (unique)
- `providerInvoiceId` (unique)
- `tenantId`
- `billingProfileId`
- `subscriptionId`
- `status`

**Status Values:**
- `draft`: Draft invoice
- `open`: Open/unpaid
- `paid`: Paid
- `void`: Voided
- `uncollectible`: Uncollectible

#### 8.3 Invoice Line Item Model

**Table:** `invoice_line_items`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `invoiceId` | BigInteger | FK to invoices | ✓ |
| `description` | Text | Line item description | - |
| `quantity` | BigInteger | Quantity | ✓ (default: 1) |
| `unitPrice` | Numeric(10,2) | Unit price | ✓ |
| `amount` | Numeric(10,2) | Total amount | ✓ |
| `lineMetadata` | JSONB | Line metadata | - |

**Indexes:**
- `invoiceId`

#### 8.4 Payment Model

**Table:** `payments`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `publicId` | UUID | Public identifier | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `billingProfileId` | BigInteger | FK to billing_profiles | - |
| `invoiceId` | BigInteger | FK to invoices | - |
| `providerPaymentId` | String(255) | Provider payment ID | - |
| `status` | Enum | Payment status | ✓ |
| `amount` | Numeric(10,2) | Payment amount | ✓ |
| `currency` | String(10) | Currency code | ✓ (default: USD) |
| `paymentMethod` | String(100) | Payment method | - |
| `failureReason` | Text | Failure reason | - |
| `providerMetadata` | JSONB | Provider metadata | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |

**Indexes:**
- `publicId` (unique)
- `providerPaymentId` (unique)
- `tenantId`
- `billingProfileId`
- `invoiceId`
- `status`

**Status Values:**
- `pending`: Pending
- `processing`: Processing
- `succeeded`: Succeeded
- `failed`: Failed
- `canceled`: Canceled
- `refunded`: Refunded

#### 8.5 Billing Credit Model

**Table:** `billing_credits`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `billingProfileId` | BigInteger | FK to billing_profiles | - |
| `amount` | Numeric(10,2) | Credit amount | ✓ |
| `currency` | String(10) | Currency code | ✓ (default: USD) |
| `reason` | String(255) | Credit reason | - |
| `expiresAt` | DateTime (TZ) | Expiration date | - |
| `createdAt` | DateTime (TZ) | Creation timestamp | ✓ |

**Indexes:**
- `tenantId`
- `billingProfileId`

#### 8.6 Usage Record Model

**Table:** `usage_records`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Primary key | ✓ |
| `tenantId` | BigInteger | FK to tenants | ✓ |
| `subscriptionId` | BigInteger | FK to subscriptions | - |
| `metric` | String(100) | Usage metric | ✓ |
| `quantity` | BigInteger | Usage quantity | ✓ (default: 0) |
| `recordedAt` | DateTime (TZ) | Record timestamp | ✓ |

**Indexes:**
- `tenantId`
- `subscriptionId`
- `metric`
- `recordedAt`

---

## API Endpoints

### Authentication Endpoints

Base Path: `/api/v1/auth`

#### 1. Get Current User

**GET** `/api/v1/auth/me`

Get authenticated user information from JWT token.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "clerkUserId": "user_abc123",
  "email": "john@example.com",
  "username": "john_doe",
  "fullName": "John Doe",
  "avatarUrl": "https://example.com/avatar.jpg",
  "phoneNumber": "+1234567890",
  "isActive": true,
  "role": "member",
  "leadSource": "google",
  "brand": "exateks",
  "referralCode": "REF123",
  "utmSource": "google",
  "utmMedium": "cpc",
  "utmCampaign": "summer-2026",
  "newsletter": true,
  "emailNotifications": true,
  "marketingEmails": false,
  "clerkMetadata": {},
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-04T12:00:00Z",
  "lastLoginAt": "2026-01-04T10:30:00Z"
}
```

---

#### 2. Health Check

**GET** `/api/v1/auth/health`

Check authentication service health.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "authProvider": "clerk"
}
```

---

### Tenant Endpoints

Base Path: `/api/v1/tenants`

#### 1. Create Tenant

**POST** `/api/v1/tenants`

Create a new tenant/organization.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "clerkOrgId": "org_abc123",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "logoUrl": "https://example.com/logo.png",
  "brand": "acme",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "website": "https://acme.com",
  "status": "trial",
  "settings": {
    "timezone": "America/New_York",
    "dateFormat": "MM/DD/YYYY"
  },
  "features": {
    "analytics": true,
    "advancedReporting": false
  },
  "clerkMetadata": {}
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "publicId": "550e8400-e29b-41d4-a716-446655440000",
  "clerkOrgId": "org_abc123",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "logoUrl": "https://example.com/logo.png",
  "brand": "acme",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "website": "https://acme.com",
  "status": "trial",
  "settings": {
    "timezone": "America/New_York",
    "dateFormat": "MM/DD/YYYY"
  },
  "features": {
    "analytics": true,
    "advancedReporting": false
  },
  "clerkMetadata": {},
  "createdAt": "2026-01-04T12:00:00Z",
  "updatedAt": null,
  "deletedAt": null
}
```

**Errors:**
- `400`: Tenant already exists or invalid slug
- `401`: Unauthorized
- `500`: Server error

---

#### 2. Get Current Tenant

**GET** `/api/v1/tenants/me`

Get current tenant from JWT org_id.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "publicId": "550e8400-e29b-41d4-a716-446655440000",
  "clerkOrgId": "org_abc123",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "logoUrl": "https://example.com/logo.png",
  "brand": "acme",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "website": "https://acme.com",
  "status": "active",
  "settings": {},
  "features": {},
  "clerkMetadata": {},
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-04T12:00:00Z",
  "deletedAt": null
}
```

**Errors:**
- `400`: No organization context in token
- `401`: Unauthorized
- `404`: Tenant not found

---

#### 3. Get Tenant by ID

**GET** `/api/v1/tenants/{tenantId}`

Get tenant by internal ID.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `tenantId` (integer): Tenant ID

**Response:** `200 OK` (same as Get Current Tenant)

**Errors:**
- `401`: Unauthorized
- `404`: Tenant not found

---

#### 4. Get Tenant by Slug

**GET** `/api/v1/tenants/slug/{slug}`

Get tenant by URL slug.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `slug` (string): Tenant slug

**Response:** `200 OK` (same as Get Current Tenant)

**Errors:**
- `401`: Unauthorized
- `404`: Tenant not found

---

#### 5. List Tenants

**GET** `/api/v1/tenants`

List tenants with pagination and filters (admin endpoint).

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 10, max: 100): Number of records to return
- `status` (string, optional): Filter by status (active/inactive/suspended/trial)
- `brand` (string, optional): Filter by brand
- `search` (string, optional): Search in name, slug, email

**Response:** `200 OK`
```json
{
  "tenants": [
    {
      "id": 1,
      "publicId": "550e8400-e29b-41d4-a716-446655440000",
      "clerkOrgId": "org_abc123",
      "name": "Acme Corporation",
      "slug": "acme-corp",
      "logoUrl": "https://example.com/logo.png",
      "brand": "acme",
      "email": "contact@acme.com",
      "phone": "+1234567890",
      "website": "https://acme.com",
      "status": "active",
      "settings": {},
      "features": {},
      "clerkMetadata": {},
      "createdAt": "2026-01-01T00:00:00Z",
      "updatedAt": "2026-01-04T12:00:00Z",
      "deletedAt": null
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 10
}
```

**Errors:**
- `401`: Unauthorized
- `403`: Insufficient permissions

---

#### 6. Update Tenant

**PUT** `/api/v1/tenants/{tenantId}`

Update tenant details.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters:**
- `tenantId` (integer): Tenant ID

**Request Body:**
```json
{
  "name": "Acme Inc",
  "logoUrl": "https://example.com/new-logo.png",
  "brand": "acme",
  "email": "info@acme.com",
  "phone": "+1987654321",
  "website": "https://acme.com",
  "status": "active",
  "settings": {
    "timezone": "America/Los_Angeles"
  },
  "features": {
    "analytics": true,
    "advancedReporting": true
  },
  "clerkMetadata": {}
}
```

**Response:** `200 OK` (returns updated tenant)

**Errors:**
- `401`: Unauthorized
- `403`: Insufficient permissions
- `404`: Tenant not found

---

#### 7. Suspend Tenant

**POST** `/api/v1/tenants/{tenantId}/suspend`

Suspend a tenant (admin only).

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `tenantId` (integer): Tenant ID

**Response:** `200 OK` (returns tenant with status: "suspended")

**Errors:**
- `401`: Unauthorized
- `403`: Insufficient permissions
- `404`: Tenant not found

---

#### 8. Activate Tenant

**POST** `/api/v1/tenants/{tenantId}/activate`

Activate a suspended tenant (admin only).

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `tenantId` (integer): Tenant ID

**Response:** `200 OK` (returns tenant with status: "active")

**Errors:**
- `401`: Unauthorized
- `403`: Insufficient permissions
- `404`: Tenant not found

---

#### 9. Delete Tenant

**DELETE** `/api/v1/tenants/{tenantId}`

Soft delete a tenant (admin only).

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `tenantId` (integer): Tenant ID

**Response:** `204 No Content`

**Errors:**
- `401`: Unauthorized
- `403`: Insufficient permissions
- `404`: Tenant not found

---

### Business Endpoints

Base Path: `/api/v1/businesses`

#### 1. List Businesses

**GET** `/api/v1/businesses`

Get paginated list of businesses with filters.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `page` (integer, default: 1, min: 1): Page number
- `limit` (integer, default: 10, min: 1, max: 100): Items per page
- `status` (string, optional): Filter by status (active/inactive/pending/suspended)
- `type` (string, optional): Filter by type (llc/corporation/partnership/sole_proprietorship/nonprofit/other)
- `search` (string, optional): Search in name, legal name, description

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "publicId": "550e8400-e29b-41d4-a716-446655440000",
      "tenantId": 1,
      "ownerUserId": 1,
      "name": "Tech Startup Inc",
      "legalName": "Tech Startup Incorporated",
      "type": "corporation",
      "status": "active",
      "taxId": "12-3456789",
      "email": "contact@techstartup.com",
      "phone": "+1234567890",
      "website": "https://techstartup.com",
      "address": {
        "street": "123 Innovation Dr",
        "city": "San Francisco",
        "state": "CA",
        "zipCode": "94105",
        "country": "USA"
      },
      "logoUrl": "https://example.com/logo.png",
      "description": "A cutting-edge tech company",
      "industry": "Technology",
      "employeeCount": 50,
      "foundedYear": 2020,
      "createdAt": "2026-01-01T00:00:00Z",
      "updatedAt": "2026-01-04T12:00:00Z",
      "deletedAt": null
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "totalPages": 1
}
```

**Errors:**
- `401`: Unauthorized
- `403`: No organization context

---

#### 2. Get Business by ID

**GET** `/api/v1/businesses/{businessId}`

Get a single business by ID.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `businessId` (integer): Business ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "publicId": "550e8400-e29b-41d4-a716-446655440000",
  "tenantId": 1,
  "ownerUserId": 1,
  "name": "Tech Startup Inc",
  "legalName": "Tech Startup Incorporated",
  "type": "corporation",
  "status": "active",
  "taxId": "12-3456789",
  "email": "contact@techstartup.com",
  "phone": "+1234567890",
  "website": "https://techstartup.com",
  "address": {
    "street": "123 Innovation Dr",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94105",
    "country": "USA"
  },
  "logoUrl": "https://example.com/logo.png",
  "description": "A cutting-edge tech company",
  "industry": "Technology",
  "employeeCount": 50,
  "foundedYear": 2020,
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-04T12:00:00Z",
  "deletedAt": null
}
```

**Errors:**
- `401`: Unauthorized
- `403`: No organization context
- `404`: Business not found

---

#### 3. Create Business

**POST** `/api/v1/businesses`

Create a new business.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Tech Startup Inc",
  "legalName": "Tech Startup Incorporated",
  "type": "corporation",
  "status": "active",
  "taxId": "12-3456789",
  "email": "contact@techstartup.com",
  "phone": "+1234567890",
  "website": "https://techstartup.com",
  "address": {
    "street": "123 Innovation Dr",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94105",
    "country": "USA"
  },
  "logoUrl": "https://example.com/logo.png",
  "description": "A cutting-edge tech company",
  "industry": "Technology",
  "employeeCount": 50,
  "foundedYear": 2020
}
```

**Response:** `201 Created` (returns created business)

**Errors:**
- `400`: Business with email already exists or validation error
- `401`: Unauthorized
- `403`: No organization context

---

#### 4. Update Business

**PUT** `/api/v1/businesses/{businessId}`

Update business details.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters:**
- `businessId` (integer): Business ID

**Request Body:**
```json
{
  "name": "Tech Startup Inc",
  "legalName": "Tech Startup Incorporated",
  "type": "corporation",
  "status": "active",
  "taxId": "12-3456789",
  "email": "newemail@techstartup.com",
  "phone": "+1987654321",
  "website": "https://techstartup.com",
  "address": {
    "street": "456 New St",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94105",
    "country": "USA"
  },
  "logoUrl": "https://example.com/new-logo.png",
  "description": "An innovative tech company",
  "industry": "Technology",
  "employeeCount": 75,
  "foundedYear": 2020
}
```

**Response:** `200 OK` (returns updated business)

**Errors:**
- `400`: Validation error
- `401`: Unauthorized
- `403`: No organization context
- `404`: Business not found

---

#### 5. Delete Business

**DELETE** `/api/v1/businesses/{businessId}`

Soft delete a business.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `businessId` (integer): Business ID

**Response:** `204 No Content`

**Errors:**
- `401`: Unauthorized
- `403`: No organization context
- `404`: Business not found

---

### Email Endpoints

Base Path: `/api/v1/email`

#### 1. Send Email

**POST** `/api/v1/email/send`

Send email to one or more recipients.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "recipients": ["user@example.com", "another@example.com"],
  "subject": "Welcome to Exa!",
  "fromName": "Exa Team",
  "fromEmail": "support@exateks.com",
  "bodyText": "Welcome to our platform!",
  "bodyHtml": "<h1>Welcome to our platform!</h1><p>We're excited to have you.</p>"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "totalSent": 2,
  "totalFailed": 0,
  "results": [
    {
      "recipient": "user@example.com",
      "success": true,
      "error": null,
      "sentAt": "2026-01-04T12:00:00Z"
    },
    {
      "recipient": "another@example.com",
      "success": true,
      "error": null,
      "sentAt": "2026-01-04T12:00:01Z"
    }
  ],
  "message": "Successfully sent email to all 2 recipient(s)"
}
```

**Partial Success Response:** `200 OK`
```json
{
  "success": false,
  "totalSent": 1,
  "totalFailed": 1,
  "results": [
    {
      "recipient": "user@example.com",
      "success": true,
      "error": null,
      "sentAt": "2026-01-04T12:00:00Z"
    },
    {
      "recipient": "invalid@",
      "success": false,
      "error": "Invalid email address",
      "sentAt": null
    }
  ],
  "message": "Partially successful: 1 sent, 1 failed"
}
```

**Errors:**
- `500`: Email service configuration error

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no content to return |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## Data Types & Enums

### Tenant Status
```typescript
type TenantStatus = "active" | "inactive" | "suspended" | "trial";
```

### Membership Role
```typescript
type MembershipRole = "owner" | "admin" | "member" | "viewer";
```

### Business Type
```typescript
type BusinessType = "llc" | "corporation" | "partnership" | "sole_proprietorship" | "nonprofit" | "other";
```

### Business Status
```typescript
type BusinessStatus = "active" | "inactive" | "pending" | "suspended";
```

### Subscription Status
```typescript
type SubscriptionStatus = "active" | "trialing" | "past_due" | "canceled" | "expired";
```

### Invoice Status
```typescript
type InvoiceStatus = "draft" | "open" | "paid" | "void" | "uncollectible";
```

### Payment Status
```typescript
type PaymentStatus = "pending" | "processing" | "succeeded" | "failed" | "canceled" | "refunded";
```

### Permission Effect
```typescript
type PermissionEffect = "allow" | "deny";
```

### Subject Type
```typescript
type SubjectType = "membership" | "team";
```

### Access Level
```typescript
type AccessLevel = "read" | "write" | "admin" | "full";
```

---

## Common Patterns

### Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` or `skip`: Starting point
- `limit` or `pageSize`: Number of items

**Response Format:**
```json
{
  "data": [],
  "total": 100,
  "page": 1,
  "limit": 10,
  "totalPages": 10
}
```

### Filtering

Most list endpoints support filtering:
- `status`: Filter by status
- `type`: Filter by type
- `brand`: Filter by brand
- `search`: Full-text search

### Soft Deletes

All models support soft deletes:
- Resources are not permanently deleted
- `deletedAt` timestamp is set
- Soft-deleted records excluded from queries by default

### Timestamps

All models include:
- `createdAt`: Creation timestamp (UTC)
- `updatedAt`: Last update timestamp (UTC)
- `deletedAt`: Soft delete timestamp (UTC)

### Field Naming

**Database/Backend:** snake_case (`user_id`, `created_at`)  
**API Responses:** camelCase (`userId`, `createdAt`)

Pydantic schemas use `alias` for automatic conversion.

---

## Notes for Frontend Implementation

1. **Authentication**: All requests require `Authorization: Bearer <jwt-token>` header
2. **Organization Context**: Most endpoints require JWT to contain `org_id` claim
3. **UUIDs**: Use `publicId` for client-side references, not `id`
4. **Timestamps**: All timestamps are UTC in ISO 8601 format
5. **Currency**: All amounts in Numeric(10,2) format (e.g., "99.99")
6. **JSONB Fields**: Accept/return any valid JSON structure
7. **Soft Deletes**: Check `deletedAt` to determine if record is active
8. **Error Handling**: Always check `detail` field in error responses
9. **Pagination**: Use `page` and `limit` for consistent pagination
10. **Search**: Use `search` parameter for full-text search across multiple fields

---

**End of API Specification**
