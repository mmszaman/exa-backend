# SMB Hub – GitHub Copilot Development Context

This file defines the authoritative architectural and domain rules for SMB Hub.
GitHub Copilot should treat this as ground truth when generating code.

----------------------------------------------------------------

PRODUCT PHILOSOPHY

SMB Hub is a multi-tenant SMB Operating System, not a collection of modules.

Core loop:
Inbox -> Work Item -> Invoice -> Payment

Principles:
- One shared core for all SMBs
- Inbox is the front door
- One universal operational object
- AI drafts require human approval
- Trust over lock-in (export is mandatory)

----------------------------------------------------------------

HARD RULES

MULTI-TENANCY (NON-NEGOTIABLE)
- Every table must include tenant_id
- tenant_id is derived from auth token (Clerk org)
- Never accept tenant_id from client input
- Every query must be tenant-scoped

----------------------------------------------------------------

UNIVERSAL OBJECT MODEL

There is exactly one operational object:

WorkItem

Allowed WorkItem types:
REQUEST
ORDER
JOB
SUPPORT
ADMIN
COLLECTION
BOOKKEEPING

Do not create separate tables for tasks, tickets, jobs, orders, or cases.

----------------------------------------------------------------

CANONICAL DOMAIN OBJECTS

Allowed entities:
Tenant
TenantMember
Contact
Conversation
Message
WorkItem
Quote
Invoice
Payment
Expense
File
Template
AI_Draft
AuditLog

Do not invent new domain objects unless absolutely required.

----------------------------------------------------------------

RELATIONSHIP MODEL

Contact
 -> Conversation
    -> Message
       -> AI_Draft
          -> WorkItem

WorkItem
 -> Quote -> Invoice -> Payment
 -> Expense
 -> Files
 -> AuditLog

----------------------------------------------------------------

PROFILES (VERTICAL SUPPORT)

Profiles are configuration, not code forks.

Profiles control:
- Labels
- Required fields
- Workflow defaults
- Feature flags
- Templates
- Automations

Profiles are JSON-driven and must not be hardcoded.

----------------------------------------------------------------

INBOX RULES

Inbox is the system front door.
All inbound messages must be convertible into structured work quickly.

----------------------------------------------------------------

TEXT-TO-TASK (AI)

AI never creates production objects directly.

Pipeline:
Message or File
 -> AI_Draft
 -> Human review (optional)
 -> Apply to create WorkItem, Invoice, or Expense

AI apply must be idempotent and audited.

----------------------------------------------------------------

MONEY CORE

Invoice lifecycle:
DRAFT -> SENT -> PAID / PARTIALLY_PAID / OVERDUE

Rules:
- Deterministic totals
- Webhook-driven payments
- Audited state changes
- Tokenized, revocable client portal links

----------------------------------------------------------------

RBAC

Roles:
OWNER
ADMIN
STAFF
AGENT
VIEWER

Rules:
- AGENT limited to assigned items
- VIEWER is read-only
- Backend enforces permissions
- Export restricted to OWNER and ADMIN

----------------------------------------------------------------

API RULES

- REST under /v1
- Tenant resolved in backend middleware
- Pagination required on lists
- Idempotency for payments, AI apply, and webhooks

----------------------------------------------------------------

OUT OF SCOPE

Do not build:
- Accounting ledger
- Payroll
- Inventory system
- HRMS
- Marketing automation
- POS replacement

----------------------------------------------------------------

BUILD ORDER

1. Tenant and RBAC foundation
2. Contacts and Files
3. WorkItems
4. Invoices and Payments
5. Client Portal
6. Inbox
7. AI Drafts
8. Export and Hardening

----------------------------------------------------------------

COPILOT CHECKLIST

Before generating code, ensure:
- tenant_id handling is correct
- WorkItem is used where appropriate
- Logic is profile-driven
- Operations are idempotent
- Actions are audited
- No tenant data leakage is possible
