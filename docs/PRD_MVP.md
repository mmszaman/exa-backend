**SMB Hub v1.0 - Product Requirements**

---

**1. MVP**

---

# **1.1. Universal Object Model (the “SMB OS” foundation)**

**Non-negotiable rule:** multi-tenant from day 1 (`tenant_id` on every table)

### **Core entities (works for every SMB type)**

- **Tenant** (business)

- **User** (owner/staff/agent)

- **Role/Permission** (RBAC)

- **Contact** (customer / vendor / lead)

- **Conversation** (inbox thread: SMS/email/WhatsApp channel later)

- **Work Item** (single universal object)

  - types: `REQUEST | ORDER | JOB | SUPPORT | ADMIN | COLLECTION | BOOKKEEPING`

- **Quote/Estimate**

- **Invoice**

- **Payment**

- **Expense** (receipt capture)

- **File/Document** (attachments + templates)

- **Activity/Event Log** (audit + timeline)

- **Integration Connection** (POS/email/SMS provider)

### **Key relationships (simple + powerful)**

    Contact → has many Conversations

    Conversation → can create Work Items (Text-to-Task)

    Work Item → can generate Quote/Invoice/Expense tasks

    Quote → converts to Invoice

    Invoice → has Payments

    Any object → has Files + Activity Log

**Why this wins:** you avoid “module spaghetti.” Everything becomes a **Work Item** + **Money objects**.

---

# **1.2. Profile Engine (how you support retail/restaurants/service without branching code)**

You’re not building “different products.” You’re shipping **profiles** that set defaults:

### **What a profile controls**

- **Terminology**: “Job” vs “Order” vs “Ticket”

- **Required fields**: e.g., service address vs table # vs SKU line items

- **Workflow defaults**:

  - Service: `Request → Quote → Job → Invoice → Payment`

  - Retail: `Sale → Receipt/Invoice → Payment → Return/Exchange`

- **Feature flags** (capabilities on/off)

- **Templates** (quote/invoice/messages)

- **Automation recipes** (AR reminders, follow-ups)

- **Integration presets** (POS connector enabled for retail)

### **Minimal config shape (example)**

    {
      "profile_id": "retail_pos",
      "labels": { "work_item": "Order", "customer": "Customer" },
      "required_fields": {
        "invoice": ["line_items", "tax_code"],
        "work_item": ["source_channel"]
      },
      "capabilities": {
        "pos_sync": true,
        "inventory_lite": false,
        "scheduling_lite": false,
        "returns_lite": true
      },
      "automations": {
        "ar_reminders": { "enabled": true, "schedule_days": [3, 7, 14] }
      },
      "templates": {
        "invoice_default": "tpl_invoice_retail_v1",
        "message_payment_link": "tpl_msg_paylink_v1"
      }
    }

This matches your own thesis: **Shared Core + modular templates**

---

# **1.3. MVP Module Lock (what we build now vs later)**

### **MVP “Core OS” (ship this)**

1. **Inbox + Conversations** (start with Email + 1 SMS provider; expand later)

2. **Contacts + Timeline**

3. **Work Items (Requests/Tickets/Orders)** + minimal statuses

   - `New → In Progress → Needs Approval → Done`

4. **Quotes → Invoices → Payments** + Payment Links

5. **AR Reminders / Collections Work Items**

6. **Expense Capture (receipt upload/email-forward later)**

7. **Client Portal** (pay / approve / view docs / messages)

8. **Text-to-Task** (creates Work Items + drafts invoices/quotes)

9. **One-Click Export** (anti lock-in)

This aligns with your own MVP focus: **Unified Inbox + Billing & Collections + Request Service portal** and “sticky money data”

### **MVP “Profiles” (ship 2 profiles first)**

- **General Services (quote-to-invoice)**

- **Retail POS-led (integration-first)**Because POS is a full category; Square itself bundles POS + invoices + inventory + accounting integrations[ Square+1](https://squareup.com/ca/en/point-of-sale?utm_source=chatgpt.com).

### **Do as Service SKUs (NOT modules in MVP)**

- Bookkeeping cleanup

- Marketing/social posting

- Payroll handling

- Listing management

You already called the margin risk + solution: **AI handles 80%, humans QC 20%**

---

# **1.4.  Text-to-Task Spec (the universal killer feature)**

### **Inputs**

- Text message / email

- Photo (receipt, work done, product, jobsite)

- Voice note (later)

### **Outputs (structured drafts)**

- Create **Work Item**

- Draft **Quote**

- Draft **Invoice**

- Draft **Expense**

- Draft **AR follow-up message**

### **Execution pipeline (profit-safe)**

1. AI triage → classify intent + extract entities

2. Draft object(s)

3. Route to **human QC queue** (optional by tenant plan)

4. Owner approves (1 tap) → send/pay

This is exactly your “AI layer + human layer” operating model

---

# **1.5. PRD Skeleton (v1) — screens + flows**

### **Screens (client-facing)**

1. **Home**: “Today” (unpaid invoices, new requests, quick actions)

2. **Inbox**: conversations + “turn into” (Request/Invoice/Quote)

3. **Contacts**: list + contact timeline

4. **Work**: requests/orders/jobs (filters by status/type)

5. **Quotes**: draft → sent → approved

6. **Invoices**: draft → sent → paid/unpaid

7. **Payments**: payment list + reconciliation status

8. **Expenses**: capture + pending review

9. **Client Portal**: pay/approve/messages/docs

10. **Settings**: business profile, integrations, team, export

### **Screens (ops / your team)**

- **Command Center**: QC queue (AI drafts), SLA, assignment, completion log

### **Core flows (MVP)**

- **Inbox → Work Item** (1 tap)

- **Work Item → Quote → Invoice → Payment**

- **Retail POS Sync → Invoice/Receipt → Support/Returns Work Item**

- **Expense photo → Expense draft → approve**

- **AR automation → follow-up message → mark resolved**

### **Acceptance criteria (examples)**

- “Create invoice from message” in < 60 seconds

- “Send payment link” in 2 taps

- “Export all data” from Settings (contacts, invoices, payments, work items)

---

# **1.6 Why this plan fits the current market (profit lens)**

- **App sprawl is huge**, so “replace tools” is a real value proposition (Okta 2025 shows app counts crossing \~100 on average).[ okta.com](https://www.okta.com/newsroom/articles/businesses-at-work-2025/?utm_source=chatgpt.com)

- **AI adoption is now mainstream** among small businesses (U.S. Chamber 2025), so Text-to-Task isn’t “too early.”[ U.S. Chamber of Commerce+1](https://www.uschamber.com/technology/artificial-intelligence/u-s-chambers-latest-empowering-small-business-report-shows-majority-of-businesses-in-all-50-states-are-embracing-ai?utm_source=chatgpt.com)

- **Retail inclusion stays feasible** by integrating POS ecosystems first (Square’s own positioning includes POS + invoices + inventory + accounting integrations).[ Square+1](https://squareup.com/ca/en/point-of-sale?utm_source=chatgpt.com)

---

---

---

**2. PRD Step 1:\
Data Model, Permissions, API Map**

---

This Step -1 spec is built around your “**Shared Core + Modular Templates**” approach and the MVP focus on **Inbox + Billing/Collections + Request Portal** with **AI-first draft + human QC**and **One-Click Export** for trust

---

# **2.1. Core Objects and Fields**

## **Global conventions (apply to every table)**

### **Required columns**

- `id` (UUID)

- `tenant_id` (UUID) _(derived from Clerk org → mapped to tenant; never trusted from client)_

- `created_at`, `updated_at` (timestamptz)

- `created_by` (string Clerk user_id)

- `deleted_at` (nullable, for soft delete)

### **Indexing**

- `(tenant_id, created_at)`

- `(tenant_id, updated_at)`

- plus entity-specific indexes below

---

### **Tenant**

Represents a business account.

- `id`

- `clerk_org_id` (string, unique)

- `name`

- `profile_id` _(points to Profile config: general / retail_pos / restaurant, etc.)_

- `timezone`

- `currency`

- `settings_json` (jsonb)

---

### **TenantMember**

- `id`

- `tenant_id`

- `user_id` (Clerk user_id)

- `role` enum: `OWNER | ADMIN | STAFF | AGENT | VIEWER`

- `status` enum: `ACTIVE | INVITED | DISABLED`

- `last_seen_at`

**Unique:** `(tenant_id, user_id)`

---

### **Contact**

Used for customers + vendors + leads.

- `id`, `tenant_id`

- `type` enum: `CUSTOMER | VENDOR | LEAD | OTHER`

- `display_name` _(required)_

- `company_name` (optional)

- `email`, `phone`

- `address_line1/2`, `city`, `region`, `postal_code`, `country`

- `tags` (text\[])

- `notes` (text)

- `status` enum: `ACTIVE | ARCHIVED`

**Indexes:** `(tenant_id, type)`, `(tenant_id, phone)`, `(tenant_id, email)`, `(tenant_id, display_name)`

---

### **Conversation (Unified Inbox Thread)**

- `id`, `tenant_id`

- `channel` enum: `EMAIL | SMS | WHATSAPP | WEB_PORTAL`

- `external_thread_id` (string) _(provider thread id)_

- `contact_id` (nullable for unknown sender)

- `subject` (email)

- `last_message_at`

- `status` enum: `OPEN | CLOSED`

- `assigned_to` (nullable user_id)

---

### **Message**

- `id`, `tenant_id`

- `conversation_id`

- `direction` enum: `INBOUND | OUTBOUND`

- `from_address`, `to_address`

- `body_text`

- `body_html` (nullable)

- `attachments_count`

- `provider_message_id`

- `sent_at` / `received_at`

- `ai_parsed_status` enum: `PENDING | DONE | FAILED`

---

### **WorkItem (Universal “Request” Object)**

This is the operational backbone (job/order/ticket/etc. by profile).

- `id`, `tenant_id`

- `type` enum: `REQUEST | ORDER | JOB | SUPPORT | ADMIN | COLLECTION | BOOKKEEPING`

- `title` _(required)_

- `description` (text)

- `status` enum: `NEW | IN_PROGRESS | NEEDS_APPROVAL | WAITING | DONE | CANCELED`

- `priority` enum: `LOW | NORMAL | HIGH | URGENT`

- `contact_id` (nullable)

- `conversation_id` (nullable) _(link to originating inbox thread)_

- `due_at` (nullable)

- `assigned_to` (nullable user_id)

- `source` enum: `INBOX | PORTAL | MANUAL | POS_SYNC | AI`

- `labels_json` (jsonb) _(profile-specific fields: service address, table #, etc.)_

**Indexes:** `(tenant_id, status)`, `(tenant_id, type)`, `(tenant_id, assigned_to)`, `(tenant_id, due_at)`

---

### **Quote**

- `id`, `tenant_id`

- `quote_number` (string, unique per tenant)

- `status` enum: `DRAFT | SENT | APPROVED | REJECTED | EXPIRED | CONVERTED`

- `contact_id` _(required)_

- `work_item_id` (nullable)

- `issue_date`, `expiry_date`

- `currency`

- `subtotal`, `tax_total`, `discount_total`, `total`

- `notes` (text)

- `terms` (text)

- `line_items` (jsonb) _(MVP: store in jsonb; later normalize if needed)_

- `approval_token` (for portal approve link)

- `converted_invoice_id` (nullable)

---

### **Invoice**

- `id`, `tenant_id`

- `invoice_number` (string, unique per tenant)

- `status` enum: `DRAFT | SENT | PARTIALLY_PAID | PAID | OVERDUE | VOID`

- `contact_id` _(required)_

- `quote_id` (nullable)

- `work_item_id` (nullable)

- `issue_date`, `due_date`

- `currency`

- `subtotal`, `tax_total`, `discount_total`, `total`, `amount_paid`, `amount_due`

- `notes`, `terms`

- `line_items` (jsonb)

- `payment_link_url` (nullable)

- `last_sent_at`

- `ar_stage` enum: `NONE | REMINDER_1 | REMINDER_2 | FINAL | COLLECTIONS`

---

### **Payment**

- `id`, `tenant_id`

- `invoice_id` _(required)_

- `provider` enum: `STRIPE | CASH | BANK | OTHER`

- `provider_payment_id` (nullable)

- `status` enum: `PENDING | SUCCEEDED | FAILED | REFUNDED`

- `amount`

- `currency`

- `paid_at`

- `method_label` (e.g., “Card”, “Cash”)

- `receipt_url` (nullable)

---

### **Expense**

(MVP: capture + basic categorization; bookkeeping service can refine)

- `id`, `tenant_id`

- `status` enum: `DRAFT | SUBMITTED | APPROVED | REJECTED`

- `source` enum: `UPLOAD | EMAIL_FORWARD | MANUAL | AI`

- `vendor_contact_id` (nullable)

- `expense_date`

- `amount`, `currency`

- `category` (string) _(simple string in MVP)_

- `tax_total` (nullable)

- `notes`

- `receipt_file_id` (nullable)

- `ai_confidence` (nullable float 0–1)

---

### **File (Attachments / Receipts / PDFs)**

- `id`, `tenant_id`

- `storage_provider` enum: `R2 | S3`

- `bucket`, `object_key`

- `file_name`, `mime_type`, `size_bytes`

- `checksum_sha256` (nullable)

- `linked_entity_type` enum: `CONTACT | WORK_ITEM | MESSAGE | QUOTE | INVOICE | EXPENSE | TEMPLATE`

- `linked_entity_id`

- `uploaded_by`

---

### **Template (Docs + Messages)**

- `id`, `tenant_id`

- `type` enum: `INVOICE | QUOTE | MESSAGE | CHECKLIST | OTHER`

- `name`

- `content` (text/jsonb)

- `is_default` (bool)

- `profile_scopes` (text\[]) _(e.g., \[“general”, “retail_pos”])_

---

### **AI Draft (Text-to-Task output)**

Stores AI output before QC/approval (supports your AI→Human workflow

- `id`, `tenant_id`

- `source_type` enum: `MESSAGE | FILE | MANUAL`

- `source_id`

- `intent` enum: `CREATE_WORK_ITEM | DRAFT_QUOTE | DRAFT_INVOICE | DRAFT_EXPENSE | DRAFT_AR_MESSAGE`

- `draft_payload` (jsonb)

- `confidence` (float)

- `status` enum: `PENDING_QC | APPROVED | REJECTED | APPLIED`

- `reviewed_by` (nullable user_id)

- `review_notes` (text)

---

### **Audit Log**

- `id`, `tenant_id`

- `actor_user_id`

- `action` (string) _(e.g., “invoice.sent”, “payment.succeeded”)_

- `entity_type`, `entity_id`

- `before` (jsonb), `after` (jsonb)

- `ip_address` (nullable)

- `created_at`

---

# **2.2. Permissions Matrix (RBAC)**

Roles: `OWNER`, `ADMIN`, `STAFF`, `AGENT` (internal ops), `VIEWER`.

### **High-level rules**

- **OWNER**: everything, billing, exports, role management

- **ADMIN**: everything except billing ownership + deleting audit logs

- **STAFF**: day-to-day ops (contacts, work, invoices), limited settings

- **AGENT**: can view assigned work + create drafts; cannot send invoices unless allowed

- **VIEWER**: read-only

### **Core permissions (MVP)**

|                                |           |           |           |                       |            |
| :----------------------------: | :-------: | :-------: | :-------: | :-------------------: | :--------: |
|         **Capability**         | **OWNER** | **ADMIN** | **STAFF** |       **AGENT**       | **VIEWER** |
|      Manage team & roles       |    ✅     |    ✅     |    ❌     |          ❌           |     ❌     |
| Manage tenant settings/profile |    ✅     |    ✅     |    ❌     |          ❌           |     ❌     |
|         Contacts CRUD          |    ✅     |    ✅     |    ✅     |         ✅\*          |     👀     |
|       Inbox view/respond       |    ✅     |    ✅     |    ✅     |         ✅\*          |     👀     |
|        Work items CRUD         |    ✅     |    ✅     |    ✅     |         ✅\*          |     👀     |
|     Create quotes/invoices     |    ✅     |    ✅     |    ✅     |    ✅ (draft only)    |     👀     |
|       Send quote/invoice       |    ✅     |    ✅     |    ✅     | ❌ (unless delegated) |     ❌     |
|    Record payments/refunds     |    ✅     |    ✅     |    ✅     |          ❌           |     👀     |
|        Expense capture         |    ✅     |    ✅     |    ✅     |         ✅\*          |     👀     |
|       Approve AI drafts        |    ✅     |    ✅     |    ✅     |   ✅ (if assigned)    |     ❌     |
|        One-click export        |    ✅     |    ✅     |    ❌     |          ❌           |     ❌     |

\*AGENT access should be scoped to **assigned items** by default.

---

# **2.3. API Routes (v1) mapped to screens**

### **Auth & tenancy (Clerk + Neon)**

All requests:

- `Authorization: Bearer <clerk_session_jwt>
`Backend derives `user_id` + `org_id`, maps to `tenant_id` (never accept tenant_id from client).

---

### **Home (Snapshot)**

- `GET /v1/home/summary
`Returns: counts + money snapshot (unpaid, overdue, new work items, today’s payments)

---

### **Inbox**

- `GET /v1/conversations?status=&assigned_to=`

- `GET /v1/conversations/{id}`

- `GET /v1/conversations/{id}/messages`

- `POST /v1/conversations/{id}/messages` _(send outbound)_

- `POST /v1/messages/{id}/ai/parse` _(trigger Text-to-Task draft)_

---

### **Contacts**

- `GET /v1/contacts?type=&q=`

- `POST /v1/contacts`

- `GET /v1/contacts/{id}`

- `PATCH /v1/contacts/{id}`

- `DELETE /v1/contacts/{id}` _(soft delete)_

- `GET /v1/contacts/{id}/timeline` _(audit + linked objects summary)_

---

### **Work (WorkItems)**

- `GET /v1/work-items?status=&type=&assigned_to=`

- `POST /v1/work-items`

- `GET /v1/work-items/{id}`

- `PATCH /v1/work-items/{id}` _(status, assignment, fields)_

- `POST /v1/work-items/{id}/convert` _(create quote/invoice/etc.)_

---

### **Quotes**

- `GET /v1/quotes?status=&contact_id=`

- `POST /v1/quotes`

- `GET /v1/quotes/{id}`

- `PATCH /v1/quotes/{id}`

- `POST /v1/quotes/{id}/send`

- `POST /v1/quotes/{id}/approve` _(portal flow)_

- `POST /v1/quotes/{id}/convert-to-invoice`

---

### **Invoices**

- `GET /v1/invoices?status=&contact_id=`

- `POST /v1/invoices`

- `GET /v1/invoices/{id}`

- `PATCH /v1/invoices/{id}`

- `POST /v1/invoices/{id}/send`

- `POST /v1/invoices/{id}/void`

- `POST /v1/invoices/{id}/payment-link` _(Stripe link)_

- `POST /v1/invoices/{id}/remind` _(manual AR nudge)_

---

### **Payments**

- `GET /v1/payments?invoice_id=&status=`

- `POST /v1/payments` _(manual/cash entry)_

- `POST /v1/webhooks/stripe` _(provider webhook)_

- `POST /v1/payments/{id}/refund` _(later; optional)_

---

### **Expenses**

- `GET /v1/expenses?status=&month=`

- `POST /v1/expenses` _(manual)_

- `POST /v1/expenses/upload` _(receipt → file → expense draft)_

- `PATCH /v1/expenses/{id}`

- `POST /v1/expenses/{id}/submit`

- `POST /v1/expenses/{id}/approve`

---

### **Client Portal (external)**

- `GET /portal/invoices/{public_token}`

- `POST /portal/invoices/{public_token}/pay` _(redirect to Stripe checkout/link)_

- `GET /portal/quotes/{public_token}`

- `POST /portal/quotes/{public_token}/approve`

- `POST /portal/messages` _(optional: portal message thread)_

---

### **Settings / Templates / Export**

- `GET /v1/profile` _(effective profile config for tenant)_

- `GET /v1/templates`

- `POST /v1/templates`

- `PATCH /v1/templates/{id}`

- `POST /v1/export` _(one-click export requirement)_

---

### **Ops Command Center (internal team)**

- `GET /v1/ops/ai-drafts?status=PENDING_QC`

- `PATCH /v1/ops/ai-drafts/{id}` _(approve/reject)_

- `GET /v1/ops/work-queue?status=&assigned_to=`

---

# **2.4. MVP Field “Musts” (to avoid Zoho-bloat)**

To stay aligned with the “lean stack” MVP:

- Keep **WorkItem.labels_json** as the extension point (profile-specific data) instead of new tables early.

- Keep **line_items** in json for v1; normalize only when reporting needs force it.

- Enforce the **AI draft → QC → send** pipeline

---

---

---

**3. PRD Step 2:\
Screen-by-Screen Requirements (v1)**

Scope: **MVP user-facing app + client portal + ops command center**, with deep detail on the primary flow:

**Inbox → Work Item → Invoice → Send/Pay**

This step defines: **UI components, states, actions, validations, error handling, and analytics events** per screen.

---

# **3.1. Global UX Rules (apply everywhere)**

### **Navigation**

- Left nav (desktop): Home, Inbox, Work, Contacts, Quotes, Invoices, Expenses, Settings

- Bottom nav (mobile): Home, Inbox, Work, Money (Invoices), More

### **Universal UI patterns**

- Every list view supports: **search**, **status filter**, **assigned filter** (if role supports)

- Every object has:

  - **Status pill**

  - **Quick actions**

  - **Activity timeline**

  - **Files/attachments**

- “Create” actions always available via **+** button

### **Error & loading states**

- Skeleton loading for lists and detail panes

- Inline form validation + field-level errors

- Toasts for non-blocking success/failure

- “Retry” button for network failures

- Graceful “Not found / No access” screens

### **Permissions behavior**

- Hide actions user cannot do

- If deep link hits restricted action: show **read-only** + “Request access” (optional)

---

# **3.2. Primary Flow Requirements**

## **Flow A: Inbox → Convert to Work Item**

### **Success definition**

- User can take an inbound message and create a Work Item in **< 30 seconds**

- If AI is enabled: AI draft appears in QC/approval flow

### **Steps**

1. Open Inbox

2. Select conversation

3. Click **“Create Work Item”** or **“AI: Turn into…”**

4. Work Item created with linkage to conversation + contact

5. Work Item appears in Work list + detail view

---

## **Flow B: Work Item → Invoice Draft**

### **Success definition**

- From a Work Item, create invoice draft in **< 60 seconds**

- Draft pulls contact, context, attachments, and suggested line items (if AI enabled)

### **Steps**

1. Open Work Item

2. Click **Convert → Invoice**

3. Invoice draft opens

4. Add/edit line items

5. Generate payment link (optional)

6. Send invoice

---

## **Flow C: Send Invoice → Payment → Status Update**

### **Success definition**

- “Sent” status updates immediately

- On payment webhook, invoice status becomes **Paid**

- Payment appears in Payments view and invoice timeline

---

# **3.3. Screens (detailed)**

## **Home Screen (Snapshot)**

### **Purpose**

Fast “today view” with money + workload.

### **Components**

- KPI cards: Unpaid invoices, Overdue, New work items, Today’s payments

- Quick actions: New invoice, New request, Upload receipt, Compose message

- “Next actions” list: top 5 items (overdue invoices + urgent work items)

### **States**

- Empty: “No items yet” + quick action buttons

- Loading: skeleton cards

- Error: retry + log ref id

### **Analytics events**

    home.view



    home.quick_action.clicked

---

# **3.4. Inbox Screen (Conversations List)**

### **Purpose**

Be the “front door” for all work.

### **Components**

- Search box (name/number/email/subject)

- Filters: Status (Open/Closed), Channel, Assigned

- Conversation list items show:

  - Contact name (or “Unknown”)

  - Snippet + timestamp

  - Unread badge

  - Linked objects indicator (Work Item / Invoice icon)

- Floating “Compose” button

### **Actions**

- Select conversation → opens detail pane

- Assign conversation to self/teammate (if role allows)

- Mark closed/open

### **Validations**

- Compose requires at least one recipient route (email/phone)

- If contact missing: prompt “Create contact?” (one-click)

### **Edge cases**

- Unknown sender → allow creating contact from header

- Provider failure (SMS/email): show “Failed to send” + retry

### **Analytics**

    inbox.view



    conversation.opened



    conversation.assigned



    message.send_attempted



    message.send_failed



    message.sent

---

# **3.5. Conversation Detail (Thread View)**

### **Purpose**

Read and act: convert messages into structured work.

### **Components**

**Header**

- Contact chip (click to open contact)

- Channel badge

- Assign dropdown

- “Convert to” button group:

  - Create Work Item

  - Draft Invoice

  - Draft Quote

  - Draft Expense

  - (AI) “Turn into…” (if enabled)

**Body**

- Message bubbles with timestamps

- Attachment previews

**Composer**

- Text box + attachments + send

### **Actions**

- “Create Work Item” opens modal with prefilled fields

- “AI Turn into…” creates AI Draft record and shows progress

### **Validations**

- Work Item title required

- If drafting invoice/quote: must have contact (create if missing)

### **States**

- AI parsing: progress spinner + “Drafting…”

- AI failure: show error + “Create manually” fallback

### **Analytics**

- `convert.clicked` with `{target_type}`

- `ai.parse.started

  `

- `ai.parse.completed

  `

- `ai.parse.failed

  `

---

# **3.6. Create Work Item (Modal)**

### **Fields (MVP)**

- Type (default: REQUEST; profile may rename label)

- Title (required)

- Contact (prefilled; required if converting to invoice later)

- Priority

- Due date

- Description (optional)

- Assign to (optional)

- Attachments (optional)

- Source auto-set (INBOX/MANUAL/AI)

### **Validations**

- Title min length 3

- Due date cannot be in the past (warn; allow override)

- If type = COLLECTION: must link to invoice (optional MVP rule)

### **Buttons**

- Create

- Create + Draft Invoice (shortcut)

### **Analytics**

    work_item.create



    work_item.create_failed

---

# **3.7. Work Screen (Work Items List)**

### **Purpose**

Single operational queue across business types.

### **Components**

- Filters: Status, Type, Priority, Assigned, Due date

- List rows show: title, contact, status, due, assigned, linked invoice/quote icons

- Bulk actions (later; not MVP unless needed)

- “New Work Item” button

### **States**

- Empty: “No work items” + create button

- Error: retry

### **Analytics**

    work.view



    work.filter_applied

---

# **3.8. Work Item Detail**

### **Purpose**

Context hub: from request to billing and service execution.

### **Tabs/Sections**

1. **Overview**

- Status dropdown

- Contact

- Assignment

- Due date

- Notes

- Linked conversation

- Linked invoice/quote

- Activity timeline

2. **Actions**

- Convert → Quote

- Convert → Invoice

- Create task checklist (lite)

- Request Service (future, can be MVP if you want monetization early)

3. **Files**

- Upload/view attachments

### **Convert to Invoice (button behavior)**

- If no contact: prompt create/select contact

- If invoice exists: open invoice

### **Analytics**

    work_item.view



    work_item.status_changed



    work_item.convert_to_invoice

---

# **3.9. Invoice List Screen**

### **Purpose**

Manage billing pipeline.

### **Components**

- Filters: Status, overdue, contact, date range

- List: invoice #, contact, total, due date, status, amount due

- Quick actions: Send, Copy link, Mark paid (manual)

### **States**

- Empty: “No invoices yet” + create button

- Loading skeletons

### **Analytics**

    invoice.list.view



    invoice.quick_action

---

# **3.10. Invoice Editor (Draft)**

### **Purpose**

Create/edit invoice fast without accounting complexity.

### **Sections**

**Header**

- Invoice number (auto)

- Status (Draft/Sent)

- Contact (required)

- Issue date, due date

- Currency (default from tenant)

**Line Items**

- Add line item (name, qty, rate, tax toggle)

- Discount (optional)

- Totals auto-calculated

**Notes/Terms**

- Optional

**Payment**

- Generate payment link (Stripe)

- Toggle: “Allow partial payment” (later; optional)

**Send**

- Choose channel: email / SMS (if available)

- Message template picker

### **Validations**

- Contact required

- At least 1 line item

- Due date >= issue date

- Total must be > 0

- If sending via SMS: must have phone; via email: must have email

### **Error handling**

- Stripe link failure: show reason + retry, invoice still saves

- Send failure: invoice remains Draft/Sent?

  - Rule: status changes to **Sent only after provider confirms** (or optimistic + rollback with clear UI)

### **Analytics**

    invoice.create_draft



    invoice.update_draft



    invoice.payment_link.created



    invoice.send_attempted



    invoice.sent



    invoice.send_failed

---

# **3.11. Invoice Detail (Sent/Paid)**

### **Components**

- Status timeline (Draft→Sent→Paid)

- Payment link + “Copy”

- Payments list

- Activity log (sent events, reminders)

- “Send reminder” button

- “Void invoice” (role-gated)

### **AR reminders (MVP)**

- Manual reminder button always

- Automated reminders optional via settings:

  - schedule: 3/7/14 days after due date (config)

### **Analytics**

    invoice.view



    invoice.reminder_sent



    invoice.voided

---

# **3.12. Expenses Screen (Receipt Capture)**

### **Purpose**

Simple capture that enables bookkeeping service later.

### **Components**

- Upload receipt button

- List by status: Draft/Submitted/Approved

- Basic fields: vendor, date, category, amount

- “Submit” action

### **Validations**

- Amount required

- Date required

- Receipt optional but recommended

### **AI assist (optional MVP)**

- On upload: AI suggests vendor/amount/date/category with confidence

### **Analytics**

    expense.upload



    expense.ai_extracted



    expense.submitted

---

# **3.13. Client Portal (External)**

## **Invoice Payment Page (public token)**

### **Components**

- Invoice summary (business name, invoice #, due date, total)

- Pay button (Stripe checkout/link)

- Download PDF (optional MVP)

- Message business (optional)

### **Rules**

- No portal authentication required for MVP (token-based)

- Token must be revocable (void token if needed)

### **States**

- Invalid token: show “Link expired”

- Paid: show receipt/status

### **Analytics**

    portal.invoice.view



    portal.pay.clicked



    portal.pay.success



    portal.pay.failed

---

## **Quote Approval Page**

- View quote + approve/reject

- Optional signature later

- Approval creates event + notifies business

---

# **3.14. Ops Command Center (Internal Team)**

## **AI Draft Queue**

### **Components**

- List of drafts: intent, confidence, source, tenant, age, assigned reviewer

- Detail view shows:

  - original message/file

  - extracted fields

  - suggested object payload

  - buttons: Approve → Apply, Reject, Edit then apply

### **SLA / workflow**

- Default: low confidence → requires QC

- High confidence → can auto-apply (tenant setting, off by default)

### **Analytics**

    ops.ai_draft.view



    ops.ai_draft.approved



    ops.ai_draft.rejected



    ops.ai_draft.applied

---

# **3.15. MVP Acceptance Criteria (Step 2)**

### **A) Inbox → Work Item**

- Convert inbound message to work item with conversation link

- Work item appears in Work list immediately

### **B) Work Item → Invoice**

- From work item, generate invoice draft with contact prefilled

- Must send invoice via at least one channel (email or SMS)

### **C) Pay**

- Payment updates invoice status to Paid (via webhook)

- Payment record visible on invoice detail

### **D) Safety**

- Tenant isolation enforced (no cross-tenant data on any list/detail)

- Export endpoint exists (even if async job)

---

**4. PRD Step 3:\
Analytics & Telemetry, Non-Functional Requirements, MVP Build Sequence**

---

# **4.1. Analytics Plan**

## **4.1.1. What we’re trying to prove (PMF + profitability)**

You need instrumentation that answers 3 questions fast:

### **A) Adoption: “Do owners get value in week 1?”**

- **Time to First Value (TTFV):** signup → first invoice sent → first payment received

- **Activation rate:** % tenants who reach “invoice sent” within 7 days

- **Setup tax:** steps/time to connect channel + create first contact + send first invoice

### **B) Retention: “Do they come back weekly without forcing?”**

- Weekly active tenants

- Repeat usage of **Money Core** (invoices/payments) + **Inbox**

- “Core loop” completion frequency per tenant

### **C) Unit economics: “Does SwaS scale without margin collapse?”**

- AI draft acceptance rate

- Human QC minutes per request

- Cost per completed service request

- Service attach rate (who buys add-ons)

---

## **4.1.2. North-star metric (single score you optimize)**

Pick one that aligns with “replace other tools”:

### **Weekly Completed Business Actions (WCBA)**

Count per tenant per week:

- invoice sent

- payment received

- work item closed

- expense submitted/approved

- client portal action (pay/approve)

You want WCBA rising → retention rises.

---

## **4.1.3. Event tracking schema (standard format)**

Every event should include these base fields:

**Base properties**

- `event_name

  `

- `timestamp

  `

- `tenant_id

  `

- `user_id

  `

- `role

  `

- `profile_id` (general / retail_pos / etc.)

- `platform` (web/pwa/mobile)

- `source` (inbox/manual/ai/pos_sync/portal)

- `session_id

  `

- `request_id` (correlate API + UI)

**Object context (optional)**

- `conversation_id`, `work_item_id`, `invoice_id`, `quote_id`, `payment_id`, `expense_id

  `

- `amount`, `currency` (for money events)

- `ai_confidence` (for AI events)

---

## **4.1.4. Event taxonomy (MVP required)**

### **Identity & tenant**

    auth.signup_completed



    auth.login_completed



    tenant.created



    tenant.member_invited



    tenant.profile_selected

### **Inbox & messaging (core front door)**

- `inbox.view

  `

- `conversation.opened

  `

- `message.sent

  `

- `message.send_failed

  `

- `conversation.assigned

  `

- `convert.clicked` `{target_type: work_item|invoice|quote|expense}

  `

### **Work items (single operational object)**

    work.view



    work_item.created



    work_item.updated



    work_item.status_changed



    work_item.assigned



    work_item.closed



    work_item.convert_to_invoice



    work_item.convert_to_quote

### **Quotes**

- `quote.created

  `

- `quote.sent

  `

- `quote.approved` (portal)

- `quote.converted_to_invoice

  `

### **Invoices (retention anchor)**

- `invoice.draft_created

  `

- `invoice.updated

  `

- `invoice.payment_link_created

  `

- `invoice.sent

  `

- `invoice.send_failed

  `

- `invoice.reminder_sent

  `

- `invoice.voided

  `

- `invoice.paid` _(webhook confirms)_

### **Payments**

- `payment.succeeded

  `

- `payment.failed

  `

- `payment.refunded` _(optional)_

### **Expenses**

- `expense.uploaded

  `

- `expense.ai_extracted` `{confidence}

  `

- `expense.submitted

  `

- `expense.approved

  `

### **AI (Text-to-Task)**

- `ai.parse.started

  `

- `ai.parse.completed` `{intent, confidence}

  `

- `ai.parse.failed

  `

- `ai.draft.created

  `

- `ai.draft.approved

  `

- `ai.draft.rejected

  `

- `ai.draft.applied

  `

- `ai.draft.edited_before_apply

  `

### **Client portal**

    portal.invoice.view



    portal.pay.clicked



    portal.pay.success



    portal.pay.failed



    portal.quote.view



    portal.quote.approve

### **Reliability / trust**

- `export.started

  `

- `export.completed

  `

- `export.failed

  `

- `security.permission_denied

  `

- `tenant.isolation_violation_detected` _(internal test event)_

---

## **4.1.5. KPI dashboards (what you should see weekly)**

### **Funnel dashboard**

1. Tenant created

2. Connected channel (email/SMS)

3. Created contact

4. Sent invoice

5. Payment received

Track drop-off at each step.

### **Revenue dashboard**

- MRR (subscriptions)

- Service revenue

- Attach rate (% tenants buying service)

- AR days (time from invoice sent to paid)

### **AI & Ops dashboard**

- Draft confidence distribution

- Approval rate

- Avg QC time per draft

- % auto-applied (later)

- SLA breach rate

---

# **4.2. Non-Functional Requirements (NFRs)**

## **4.2.1. Performance targets (MVP)**

- App shell load: fast enough to feel “instant” on mobile

- Common actions:

  - open inbox thread: quick

  - create work item: quick

  - save invoice draft: quick

- Background tasks (AI parse, exports) must show progress + not block UI.

## **4.2.2. Availability & resilience**

- Payments/webhooks must be idempotent (replay-safe).

- Background jobs must retry with backoff.

- Queue failure must not break core CRUD flows.

## **4.2.3. Security baseline (MVP)**

- **Strict tenant isolation**:

  - tenant derived from Clerk org token on backend

  - every query filtered by tenant

  - add automated tests: “user from tenant A cannot access tenant B”

- RBAC enforced on backend (UI hiding is not enough).

- Rate limiting:

  - auth endpoints

  - AI endpoints

  - public portal token endpoints

- Audit logs:

  - invoice sent/edited/voided

  - payments succeeded/failed

  - membership/role changes

- Tokenized portal links must be revocable/rotatable.

## **4.2.4. Data protection & compliance posture (practical)**

- Encryption in transit (TLS)

- Sensitive secrets in env/secrets manager

- File storage via presigned upload (no public buckets)

- Backups:

  - scheduled DB backups

  - periodic export job for tenant trust

- “One-click export” must exist in MVP (even if async job).

## **4.2.5. Observability**

- Sentry for FE/BE errors

- Structured logs with request_id correlation

- Key alerts:

  - webhook failures

  - queue backlog growth

  - repeated tenant permission denials

  - high message send failures

---

# **4.5. MVP Build Sequence (minimal rework path)**

Below is the build order that keeps architecture stable and avoids building “fluff” early.

## **Sprint 0: Foundations**

- Repo setup + CI/CD + environments

- Clerk orgs + tenant mapping

- Neon schema + migrations

- RBAC middleware (tenant + role enforcement)

- Base UI layout + navigation

## **Sprint 1: Core Data + Contacts**

- Contacts CRUD + timeline skeleton

- File upload plumbing (R2/S3) + entity linking

- Audit log writes on key actions

## **Sprint 2: Work Items (universal operational object)**

- Work list + filters

- Work detail + status/assignment

- Convert buttons (placeholder targets)

## **Sprint 3: Invoices v1 (Money Core)**

- Invoice draft editor (line items json)

- Payment link generation (Stripe)

- Send invoice (email first; SMS if ready)

- Invoice list + detail + timeline

## **Sprint 4: Client Portal + Webhooks**

- Portal invoice view + pay flow

- Stripe webhook → payment record → invoice status update

- Basic AR reminder (manual button)

## **Sprint 5: Inbox v1 (front door)**

- Conversations list + thread view

- Send message outbound

- Convert message → create work item

- Link conversation ↔ work item

## **Sprint 6: Text-to-Task (AI + Drafts + QC)**

- AI parse pipeline creates AI Draft

- Ops Command Center: approve/reject/apply

- “Draft → invoice/work item” apply logic

- AI analytics events + confidence logging

## **Sprint 7: Trust & Production readiness**

- One-click export async job + downloadable archive

- Rate limiting + security hardening

- Tenant isolation automated test suite

- Monitoring dashboards + alerts

- Go-live checklist & smoke tests

---

## **Deliverable at end of Step 3**

1. Final event list + properties (locked)

2. KPI definitions (TTFV, activation, WCBA, attach rate, QC time)

3. NFR acceptance checklist

4. MVP sprint backlog sequence (above)

---

---

---

**5. PRD Step 4: Epics, User Stories, Acceptance Criteria (MVP)**

Below are **MVP epics** with **user stories + acceptance criteria**. This is written so your dev team can turn each story into tickets with minimal interpretation.

---

# **Epic 0: Multi-Tenancy + RBAC Foundation**

### **Story 0.1: Tenant resolution from Clerk org**

**As a** logged-in user, **I want** the app to automatically load my business (tenant) based on my active Clerk organization, **so that** I never pick the wrong company.

**Acceptance Criteria**

- Backend derives `tenant_id` from verified token (`org_id → tenants.clerk_org_id`) for every request.

- Client cannot override tenant via params/headers (ignored if provided).

- If org not mapped to tenant: API returns `403` with “Tenant not initialized”.

### **Story 0.2: Role-based access**

**As an** owner/admin, **I want** controlled access by role, **so that** staff/agents can’t do sensitive actions.

**Acceptance Criteria**

- Backend enforces permissions for create/update/send/export.

- UI hides restricted actions.

- Any restricted action via direct URL returns read-only + `403` for mutation.

---

# **Epic 1: Contacts (Customers/Vendors/Leads)**

### **Story 1.1: Create/edit contact**

**As a** business user, **I want** to create and edit contacts, **so that** I can invoice and track conversations.

**Acceptance Criteria**

- Create contact with `display_name` required.

- Phone/email optional but validated when present.

- Contacts searchable by name/phone/email.

- Soft delete supported; deleted contacts hidden from default lists.

### **Story 1.2: Contact timeline**

**As a** business user, **I want** a contact timeline, **so that** I can see invoices/messages/work in one view.

**Acceptance Criteria**

- Timeline shows recent: conversations, work items, invoices, payments, files.

- Clicking an item opens its detail.

- Timeline respects RBAC (viewer sees read-only).

---

# **Epic 2: Work Items (Universal Requests)**

### **Story 2.1: Create work item**

**As a** business user, **I want** to create a work item, **so that** I can track a request/order/job.

**Acceptance Criteria**

- Required: `title`, default `type=REQUEST`, default `status=NEW`.

- Optional: contact, due date, priority, assignment, description.

- Work item appears instantly in Work list and detail view.

### **Story 2.2: Update status/assignment**

**As a** business user, **I want** to update status and assign work, **so that** the team knows what’s happening.

**Acceptance Criteria**

- Status transitions allowed among: NEW, IN_PROGRESS, NEEDS_APPROVAL, WAITING, DONE, CANCELED.

- Assignment to any active tenant member.

- All changes recorded in Activity/Audit log.

### **Story 2.3: Convert work item to invoice/quote**

**As a** business user, **I want** to convert a work item into a quote or invoice, **so that** billing is fast.

**Acceptance Criteria**

- If no contact linked, system prompts to select/create contact before conversion.

- Conversion creates draft quote/invoice linked back to the work item.

- If draft already exists, “Convert” opens existing draft.

---

# **Epic 3: Inbox (Conversations + Messages)**

### **Story 3.1: View inbox and open conversation**

**As a** business user, **I want** to see conversations and open them, **so that** I can respond and create work.

**Acceptance Criteria**

- Conversation list supports search + status filter (open/closed).

- Conversation detail shows message history + attachments.

- Unknown sender shows “Create contact” action.

### **Story 3.2: Send a message**

**As a** business user, **I want** to send a message from a conversation, **so that** I can reply to customers.

**Acceptance Criteria**

- Outbound message requires a valid recipient route (email or phone depending on channel).

- Provider send failure shows retry and does not mark as sent.

- Sent messages appear in thread with timestamp.

### **Story 3.3: Convert conversation to work item (core loop)**

**As a** business user, **I want** one-click conversion from conversation to work item, **so that** messages become action.

**Acceptance Criteria**

- “Create Work Item” pre-fills title from message snippet.

- Links work item to `conversation_id` and `contact_id` (if known).

- Conversion completes in <30 seconds including UI.

---

# **Epic 4: Quotes**

### **Story 4.1: Create and send quote**

**As a** business user, **I want** to create and send a quote, **so that** clients can approve before invoicing.

**Acceptance Criteria**

- Quote requires contact + at least 1 line item + total > 0.

- Quote supports statuses: DRAFT, SENT, APPROVED, REJECTED, EXPIRED, CONVERTED.

- Sending triggers audit event and stores `last_sent_at`.

### **Story 4.2: Client approves quote (portal)**

**As a** client, **I want** to approve a quote from a link, **so that** I can confirm work without logging in.

**Acceptance Criteria**

- Portal link uses token; shows quote summary + approve/reject.

- Approval creates audit event + notifies tenant (in-app notification OK for MVP).

- Approved quote can be converted to invoice in 1 click.

---

# **Epic 5: Invoices + Payments (Money Core)**

### **Story 5.1: Create invoice draft**

**As a** business user, **I want** to create an invoice quickly, **so that** I can get paid.

**Acceptance Criteria**

- Invoice requires: contact, issue date, due date, >=1 line item, total > 0.

- Totals auto-calc (subtotal/tax/discount/total).

- Draft auto-saves (manual save acceptable for MVP if simpler).

### **Story 5.2: Generate payment link**

**As a** business user, **I want** a payment link, **so that** clients can pay instantly.

**Acceptance Criteria**

- Payment link created via Stripe and stored on invoice.

- If Stripe fails, invoice remains intact; UI shows retry.

### **Story 5.3: Send invoice**

**As a** business user, **I want** to send invoices via email/SMS, **so that** billing is frictionless.

**Acceptance Criteria**

- Send requires destination method exists (email/phone).

- Invoice status changes to SENT only when send succeeds (or optimistic + rollback on failure).

- “Copy payment link” available on invoice detail.

### **Story 5.4: Receive payment (webhook-driven)**

**As a** business user, **I want** invoice status to update when payment arrives, **so that** I don’t reconcile manually.

**Acceptance Criteria**

- Stripe webhook creates Payment record (idempotent).

- Invoice updates: amount_paid/amount_due, status becomes PAID or PARTIALLY_PAID.

- Payment visible in invoice detail + payments list.

### **Story 5.5: AR reminder**

**As a** business user, **I want** to send reminders, **so that** overdue invoices get paid.

**Acceptance Criteria**

- Manual “Send reminder” action exists.

- Reminder send is logged; invoice `ar_stage` optionally increments.

---

# **Epic 6: Expenses (Receipt Capture)**

### **Story 6.1: Upload receipt and create expense draft**

**As a** business user, **I want** to upload receipts, **so that** expenses are captured for bookkeeping.

**Acceptance Criteria**

- Upload creates File + Expense draft linked together.

- Expense draft requires: date + amount (or can be left blank if AI enabled; then status stays DRAFT).

- Expense can be submitted/approved.

### **Story 6.2: AI-assisted extraction (optional toggle)**

**As a** business user, **I want** AI to extract amount/vendor/date, **so that** I don’t type.

**Acceptance Criteria**

- AI extraction fills suggested fields + confidence score.

- Low confidence prompts manual review (no auto-approve by default).

---

# **Epic 7: Text-to-Task (AI Drafts + Apply)**

### **Story 7.1: Create AI draft from message/file**

**As a** user, **I want** AI to draft a work item/invoice/expense from text or photo, **so that** work is automated.

**Acceptance Criteria**

- Trigger AI parse from message or uploaded file.

- System creates `AI_DRAFT` record with intent + payload + confidence.

- User sees progress + completion/failure state.

### **Story 7.2: Approve/reject/apply AI draft (ops + owners)**

**As an** owner/agent, **I want** to approve and apply AI drafts, **so that** the system stays accurate.

**Acceptance Criteria**

- Draft can be approved (optionally edited) and applied to create/update target object.

- Apply action is idempotent (no duplicates on retry).

- All actions recorded in audit log.

---

# **Epic 8: Client Portal (Pay / Approve)**

### **Story 8.1: Client pays invoice via portal**

**As a** client, **I want** to pay from a link, **so that** payment is simple.

**Acceptance Criteria**

- Tokenized invoice page shows summary + pay button.

- Invalid/expired token shows friendly error.

- After payment success, page shows paid state/receipt.

---

# **Epic 9: Export (Trust)**

### **Story 9.1: One-click export**

**As an** owner/admin, **I want** to export my data, **so that** I feel safe using the platform.

**Acceptance Criteria**

- Export job produces a downloadable archive containing: contacts, work items, quotes, invoices, payments, expenses (+ file links or included files if feasible).

- Export is async; UI shows job status.

- Role-gated to OWNER/ADMIN only.

---

# **Epic 10: Observability + Audit (Production-readiness)**

### **Story 10.1: Audit critical actions**

**As a** business, **I want** key actions logged, **so that** changes are traceable.

**Acceptance Criteria**

- Audit logs created for: invoice send/void/edit, payment events, membership changes, AI apply.

- Logs are tenant-scoped and immutable (no delete in MVP UI).

---

# **Out of Scope (Explicitly Not MVP)**

- Full accounting ledger / payroll engine

- Full POS replacement (retail is integration-first)

- Full marketing automation suite

- Advanced HRMS/recruiting

- Enterprise SSO/SAML (can be later if needed)

---

---

---

**6. PRD Step 5 — Sprint-Ready Backlog, Definition of Done, Test Plan**

This turns Steps 1–4 into a **build plan you can execute** with minimal rework.

---

# **6.1. Sprint-Ready Backlog (MVP Build Order)**

**Assumption:** 2 devs (1 FE-heavy, 1 BE-heavy) + you.\
&#x20;If you have more devs, you can parallelize “Inbox” and “Invoices” earlier.

## **Sprint 0: Foundations (Repo + Tenancy + CI/CD)**

**Goal:** Everything after this is safe to build.

### **Tickets**

- S0-01 Repo mono setup (Next.js + FastAPI) with shared types folder

- S0-02 CI pipeline: lint/test/build for FE/BE

- S0-03 Environments: local/staging/prod config pattern (env vars)

- S0-04 Clerk integration (signin/signup, org context)

- S0-05 Tenant mapping: `clerk_org_id → tenant_id` middleware

- S0-06 RBAC middleware + role model (OWNER/ADMIN/STAFF/AGENT/VIEWER)

- S0-07 Neon DB init + migrations baseline (Alembic)

- S0-08 Error tracking (Sentry FE + BE)

- S0-09 Request correlation IDs + structured logging

**Exit criteria:** You can login, resolve tenant, hit a protected `/health` endpoint and see logs.

---

## **Sprint 1: Core Data + Contacts + Files**

**Goal:** Create the foundational objects and CRUD.

### **Tickets**

- S1-01 Contacts: list/search/create/edit/archive

- S1-02 Contact timeline endpoint (empty shell + basic events)

- S1-03 File service: presigned upload (R2/S3) + metadata table

- S1-04 Attach files to Contact/WorkItem/Invoice/Expense

- S1-05 AuditLog write helper (generic)

**Exit criteria:** A tenant can manage contacts and attach files safely.

---

## **Sprint 2: Work Items (Universal Operations)**

**Goal:** Single operational object works end-to-end.

### **Tickets**

- S2-01 Work Items: list with filters (status/type/assigned)

- S2-02 Create/Edit Work Item + status transitions + assignment

- S2-03 Work Item detail: overview + files + activity timeline

- S2-04 “Convert” buttons scaffold (no quote/invoice creation yet)

- S2-05 Activity timeline events for status/assignment changes

**Exit criteria:** Work queue becomes the operational hub.

---

## **Sprint 3: Invoices v1 (Money Core)**

**Goal:** Draft → send → track status (without portal yet).

### **Tickets**

- S3-01 Invoice model + numbering per tenant

- S3-02 Invoice editor: contact, dates, line items (jsonb), totals

- S3-03 Invoice list + filters (draft/sent/paid/overdue)

- S3-04 Send invoice via Email provider (Postmark/SendGrid)

- S3-05 Payment link creation (Stripe checkout/link) stored on invoice

- S3-06 Invoice activity log: created/updated/sent/link created

- S3-07 Manual “record payment” (cash/bank) for MVP fallback

**Exit criteria:** Business can create and send invoices and manually mark paid.

---

## **Sprint 4: Client Portal + Stripe Webhooks (Automation)**

**Goal:** Payments auto-update invoices.

### **Tickets**

- S4-01 Public portal invoice page (token)

- S4-02 Pay button → Stripe hosted checkout/link

- S4-03 Stripe webhook handler (idempotent): create Payment, update Invoice status

- S4-04 Invoice detail shows payments + paid state

- S4-05 Portal token revocation (invalidate link)

- S4-06 AR reminder manual button (send email reminder)

**Exit criteria:** Payment received updates invoice to PAID automatically.

---

## **Sprint 5: Inbox v1 (Front Door)**

**Goal:** Conversations → work items.

### **Tickets**

- S5-01 Conversations list + search + open/closed

- S5-02 Conversation thread view + messages list

- S5-03 Send message in-thread (email reply v1)

- S5-04 Create Work Item from conversation (prefill + link)

- S5-05 “Create contact” from unknown sender

- S5-06 Link indicators: conversation ↔ work item ↔ invoice

**Exit criteria:** Inbox becomes a usable front door.

---

## **Sprint 6: Quotes + Conversions**

**Goal:** Quote-to-invoice flow and conversions from Work Item.

### **Tickets**

- S6-01 Quote create/edit/send

- S6-02 Quote portal approve/reject (token)

- S6-03 Convert quote → invoice (linked)

- S6-04 Work Item convert → quote / invoice (creates draft and links)

- S6-05 Quote/invoice templates (basic)

**Exit criteria:** Pre-approval workflow works for most SMBs.

---

## **Sprint 7: Text-to-Task (AI Drafts + Ops QC)**

**Goal:** AI drafts + human QC pipeline.

### **Tickets**

- S7-01 AI Draft model + statuses

- S7-02 Trigger AI parse from message/file → create AI Draft

- S7-03 Ops Command Center: queue list + approve/reject/edit/apply

- S7-04 Apply draft creates/updates Work Item / Invoice / Expense

- S7-05 AI telemetry events + confidence logging

- S7-06 Rate limiting + token budget rules (plan-based)

**Exit criteria:** AI draft pipeline works without creating duplicates and supports QC.

---

## **Sprint 8: Export + Hardening + Go-Live**

**Goal:** Trust + stability + production readiness.

### **Tickets**

- S8-01 One-click export async job + downloadable archive

- S8-02 Tenant isolation test suite + security review fixes

- S8-03 Webhook replay tests + idempotency hardening

- S8-04 Monitoring dashboards + alerts (webhook failures, queue backlog)

- S8-05 Performance pass (indexes, list pagination, caching)

- S8-06 “5-minute deploy verification” checklist + smoke tests

**Exit criteria:** You can onboard real users safely.

---

# **6.2. Definition of Done (DoD)**

## **6.2.1 Global DoD (applies to every ticket)**

A ticket is “done” only if:

- ✅ Works in **staging** with real auth (Clerk) and DB (Neon)

- ✅ Tenant isolation enforced (backend filters by resolved tenant)

- ✅ RBAC enforced in backend (not only UI)

- ✅ Error handling + empty states implemented

- ✅ Logging added for failures (with request_id)

- ✅ Analytics event added (if user-visible action)

- ✅ Unit tests for core logic OR integration test for endpoints

- ✅ Code reviewed + merged + deployed

## **6.2.2 Epic-specific DoD**

### **Inbox DoD**

- Convert message → Work Item creates linkages (conversation_id/contact_id)

- Provider send failure does not mark message as sent

- Unknown sender contact creation works

### **Work Items DoD**

- Status + assignment updates logged in audit

- Convert to invoice/quote prevents duplicate drafts

### **Invoices/Payments DoD**

- Stripe webhooks idempotent (replay-safe)

- Paid updates reflected across list/detail/portal

- Invoice totals deterministic and validated

### **Portal DoD**

- Token-based access only to that entity

- Token revocable

- Safe error screens for invalid/expired links

### **AI Drafts DoD**

- Draft apply is idempotent

- QC actions logged

- Low confidence routing works (configurable)

### **Export DoD**

- Export is async + shows progress

- Includes all primary objects and relationships

- Role-gated to OWNER/ADMIN

---

# **6.3. Test Plan**

## **6.3.1 Test layers (what you must have)**

### **A) Unit tests (FastAPI)**

- tenant resolution function

- RBAC permission checks

- invoice total calculation

- status transition rules

- idempotency key logic (webhooks, AI apply)

### **B) Integration tests (API)**

Run against a test DB schema:

- create tenant + member

- CRUD contacts/work items/invoices

- conversion flows

- export job creation

### **C) End-to-End tests (Playwright)**

Critical user journeys:

1. Login → create contact → create invoice → send → portal pay → invoice shows paid

2. Inbox open → create work item → convert to invoice → send

3. Quote create → send → portal approve → convert to invoice

4. Upload receipt → expense draft created

5. AI draft queue approve → object created

---

## **6.3.2 High-risk test suites (must-pass gates)**

### **Tenant Isolation Suite (must pass before go-live)**

- User from Tenant A cannot:

  - read Tenant B lists

  - read Tenant B detail endpoints

  - mutate Tenant B resources

- Direct ID guessing returns 404/403 (no data leakage)

- Export only exports current tenant’s data

### **Webhook Idempotency Suite (Stripe)**

- Replay the same webhook payload 3x:

  - only one Payment record exists

  - invoice totals and status correct

- Out-of-order events don’t break state (e.g., payment succeeded before invoice marked sent)

### **Portal Security Suite**

- token cannot access other invoices/quotes

- token revocation works

- brute-force attempt rate-limited

- portal responses never leak internal IDs or tenant data

### **AI Draft Safety Suite**

- Apply draft twice doesn’t create duplicates

- Low confidence draft does not auto-send invoice

- Draft edits are tracked in audit log

---

## **6.3.3 Performance & reliability checks (MVP minimum)**

- Pagination on all lists (inbox/work/invoices/contacts)

- Index verification: `(tenant_id, status)`, `(tenant_id, updated_at)` etc.

- Background job retry with backoff (webhooks, AI parse, export)

- Queue backlog alerting threshold defined

---

# **6.4. Release Gates (to protect success probability)**

You don’t ship until these are true:

- ✅ Activation flow works end-to-end (invoice → paid)

- ✅ Tenant isolation suite passes

- ✅ Webhook idempotency suite passes

- ✅ Portal security suite passes

- ✅ Monitoring/alerts for payments + queue exist

- ✅ One-click export works (even if slow)

---

---

---

**7. PRD Step 6 — Ticket List With Estimates, Owners, Dependencies + Onboarding Checklist**

Assumption: **2 devs** (FE + BE) + you as PM/architect.\
Estimates are **relative**: **S (0.5–2d)**, **M (2–5d)**, **L (5–10d)** per ticket.

---

# **7.1. Sprint-by-Sprint Ticket List (with FE/BE split)**

## **Sprint 0: Foundations**

|        |                                                    |           |          |             |
| ------ | -------------------------------------------------- | --------- | -------- | ----------- |
| **ID** | **Ticket**                                         | **Owner** | **Size** | **Depends** |
| S0-01  | Monorepo setup (Next.js + FastAPI) + shared types  | BE        | M        | —           |
| S0-02  | CI: lint/test/build + staging deploy               | BE        | M        | S0-01       |
| S0-03  | Env var standard + config loader (dev/stage/prod)  | BE        | S        | S0-01       |
| S0-04  | Clerk auth pages + org switch UI                   | FE        | M        | S0-01       |
| S0-05  | FastAPI Clerk JWT verification + org_id extraction | BE        | M        | S0-01       |
| S0-06  | Tenant mapping middleware (org_id→tenant_id)       | BE        | M        | S0-05       |
| S0-07  | RBAC middleware + role checks                      | BE        | M        | S0-06       |
| S0-08  | Neon schema init + Alembic baseline migrations     | BE        | M        | S0-01       |
| S0-09  | Base layout shell (nav, routing, guards)           | FE        | M        | S0-04       |
| S0-10  | Sentry FE/BE + request_id correlation              | BE        | S        | S0-02       |

**Gate:** login works, tenant resolves, protected endpoint works, logs + Sentry work.

---

## **Sprint 1: Contacts + Files**

|        |                                              |           |          |             |
| ------ | -------------------------------------------- | --------- | -------- | ----------- |
| **ID** | **Ticket**                                   | **Owner** | **Size** | **Depends** |
| S1-01  | Contacts API CRUD + search                   | BE        | M        | S0-08       |
| S1-02  | Contacts UI list + create/edit drawer        | FE        | M        | S1-01       |
| S1-03  | Contact validations + form components        | FE        | S        | S1-02       |
| S1-04  | File metadata table + upload API (presigned) | BE        | M        | S0-08       |
| S1-05  | File upload UI component (dropzone)          | FE        | M        | S1-04       |
| S1-06  | Attach files to Contact (link entity)        | BE        | S        | S1-04       |
| S1-07  | Contact timeline API (basic linked objects)  | BE        | M        | S1-01       |
| S1-08  | Contact timeline UI (empty+items)            | FE        | M        | S1-07       |
| S1-09  | Audit log helper + write on contact changes  | BE        | S        | S0-08       |

**Gate:** create contacts, attach files, timeline shows activity.

---

## **Sprint 2: Work Items (Universal Ops)**

|        |                                           |           |          |             |
| ------ | ----------------------------------------- | --------- | -------- | ----------- |
| **ID** | **Ticket**                                | **Owner** | **Size** | **Depends** |
| S2-01  | WorkItem API CRUD + filters + pagination  | BE        | M        | S0-08       |
| S2-02  | Work list UI + filters                    | FE        | M        | S2-01       |
| S2-03  | Work detail UI (overview, status, assign) | FE        | M        | S2-01       |
| S2-04  | Status transition + assignment audit logs | BE        | S        | S2-01       |
| S2-05  | WorkItem create modal + validations       | FE        | M        | S2-02       |
| S2-06  | Convert actions scaffold endpoints        | BE        | S        | S2-01       |
| S2-07  | WorkItem ↔ File linking                   | BE        | S        | S1-04       |
| S2-08  | Work detail files tab UI                  | FE        | S        | S2-07       |

**Gate:** work queue usable end-to-end.

---

## **Sprint 3: Invoices v1 (Money Core)**

|        |                                               |           |          |             |
| ------ | --------------------------------------------- | --------- | -------- | ----------- |
| **ID** | **Ticket**                                    | **Owner** | **Size** | **Depends** |
| S3-01  | Invoice model + numbering per tenant          | BE        | M        | S0-08       |
| S3-02  | Invoice CRUD API + totals calc                | BE        | M        | S3-01       |
| S3-03  | Invoice list UI + filters                     | FE        | M        | S3-02       |
| S3-04  | Invoice editor UI (line items json)           | FE        | L        | S3-02       |
| S3-05  | Email sending integration (Postmark/SendGrid) | BE        | M        | S3-02       |
| S3-06  | “Send invoice” UI + templates picker (basic)  | FE        | M        | S3-05       |
| S3-07  | Stripe payment link creation endpoint         | BE        | M        | S3-02       |
| S3-08  | Payment link UI (generate/copy)               | FE        | S        | S3-07       |
| S3-09  | Manual payment entry endpoint + UI            | BE+FE     | M        | S3-02       |
| S3-10  | Invoice detail UI + timeline                  | FE        | M        | S3-02       |

**Gate:** create → send invoice works (manual payment optional fallback).

---

## **Sprint 4: Client Portal + Webhooks**

|        |                                       |           |          |             |
| ------ | ------------------------------------- | --------- | -------- | ----------- |
| **ID** | **Ticket**                            | **Owner** | **Size** | **Depends** |
| S4-01  | Portal invoice page (token) UI        | FE        | M        | S3-02       |
| S4-02  | Portal token model + revocation       | BE        | M        | S3-02       |
| S4-03  | Stripe webhook handler (idempotent)   | BE        | L        | S3-07       |
| S4-04  | Payment table + invoice status update | BE        | M        | S4-03       |
| S4-05  | Payment list UI (invoice detail)      | FE        | S        | S4-04       |
| S4-06  | Manual AR reminder send endpoint      | BE        | M        | S3-05       |
| S4-07  | Reminder UI + activity log            | FE        | S        | S4-06       |

**Gate:** pay via portal updates invoice automatically.

---

## **Sprint 5: Inbox v1**

|        |                                                   |           |          |              |
| ------ | ------------------------------------------------- | --------- | -------- | ------------ |
| **ID** | **Ticket**                                        | **Owner** | **Size** | **Depends**  |
| S5-01  | Conversation + Message schema                     | BE        | M        | S0-08        |
| S5-02  | Conversations list API + filters                  | BE        | M        | S5-01        |
| S5-03  | Inbox UI list + search                            | FE        | M        | S5-02        |
| S5-04  | Conversation detail UI thread                     | FE        | M        | S5-02        |
| S5-05  | Email threading integration (inbound/outbound) v1 | BE        | L        | S5-01        |
| S5-06  | Send message UI + failure states                  | FE        | M        | S5-05        |
| S5-07  | Convert conversation → WorkItem (API + UI)        | BE+FE     | M        | S2-01, S5-02 |
| S5-08  | Create contact from unknown sender                | BE+FE     | M        | S1-01, S5-04 |

**Gate:** inbox creates action (work item) fast.

---

## **Sprint 6: Quotes + Conversions**

|        |                                          |           |          |                     |
| :----: | :--------------------------------------: | :-------: | :------: | :-----------------: |
| **ID** |                **Ticket**                | **Owner** | **Size** |     **Depends**     |
| S6-01  |         Quote model + numbering          |    BE     |    M     |        S0-08        |
| S6-02  |          Quote editor UI + send          |    FE     |    L     |        S6-01        |
| S6-03  |       Quote portal approve/reject        |    FE     |    M     |        S6-02        |
| S6-04  |        Quote → invoice conversion        |    BE     |    M     |    S6-01, S3-02     |
| S6-05  | WorkItem → quote/invoice conversion real |    BE     |    M     | S2-06, S6-01, S3-02 |
| S6-06  |  Templates v1 (invoice/quote/messages)   |   BE+FE   |    M     |    S3-02, S6-01     |

**Gate:** quote approval loop works.

---

## **Sprint 7: Text-to-Task + Ops QC**

|        |                                                            |           |          |                     |
| ------ | ---------------------------------------------------------- | --------- | -------- | ------------------- |
| **ID** | **Ticket**                                                 | **Owner** | **Size** | **Depends**         |
| S7-01  | AI Draft model + statuses                                  | BE        | M        | S0-08               |
| S7-02  | AI parse worker pipeline (message/file → draft)            | BE        | L        | S7-01, S5-01, S1-04 |
| S7-03  | Ops Command Center UI (queue + detail)                     | FE        | L        | S7-01               |
| S7-04  | Approve/reject/edit/apply draft endpoints                  | BE        | L        | S7-01               |
| S7-05  | Apply creates WorkItem/Invoice/Expense safely (idempotent) | BE        | L        | S7-04               |
| S7-06  | Rate limiting + token budgets                              | BE        | M        | S7-02               |
| S7-07  | AI telemetry events (confidence, accept rate)              | BE+FE     | M        | S7-02               |

**Gate:** AI drafts produce real objects safely with QC.

---

## **Sprint 8: Export + Hardening + Launch**

|        |                                              |           |          |                  |
| ------ | -------------------------------------------- | --------- | -------- | ---------------- |
| **ID** | **Ticket**                                   | **Owner** | **Size** | **Depends**      |
| S8-01  | Export job (async) + archive builder         | BE        | L        | All core objects |
| S8-02  | Export UI + job status                       | FE        | M        | S8-01            |
| S8-03  | Tenant isolation automated tests             | BE        | M        | S0-06            |
| S8-04  | Webhook replay/idempotency tests             | BE        | M        | S4-03            |
| S8-05  | Portal security tests + rate limits          | BE        | M        | S4-01            |
| S8-06  | Performance pass (indexes/pagination)        | BE        | M        | Most APIs        |
| S8-07  | Go-live smoke tests + 5-min deploy checklist | PM+BE     | S        | —                |

**Gate:** safety + trust + monitoring ready for paid users.

---

# **7.2. Dependencies Summary (so you don’t get blocked)**

- **Invoices** depend on Contacts + Tenant/RBAC.

- **Portal + Webhooks** depend on Stripe integration and Invoice model.

- **Inbox** depends on provider integration decisions (start email first).

- **AI** depends on stable object schemas + file/message ingestion.

- **Export** depends on final schemas of core objects.

---

# **7.3. Onboarding Checklist (Go-to-Market “Crush Setup Tax”)**

This is how you maximize success % and paid conversion early.

## **Onboarding Goal**

Get each tenant to **First Value** fast:

- **First invoice sent within 30–60 minutes**

- ideally **first payment received within 24–72 hours**

## **7-Step onboarding flow (in-app)**

1. **Create/Select Business (Clerk Org)**

2. **Choose Profile** (General / Retail POS-led)

   - sets templates + terminology + feature flags

3. **Connect a channel** (Email first; SMS optional)

4. **Import contacts** (CSV upload or manual add 5)

5. **Create first invoice/quote** (guided)

6. **Enable payment link** (Stripe connect / payment setup)

7. **Send first invoice** (with preview message template)

### **Done-for-you wedge (your SwaS advantage)**

During onboarding, show:

- **“Do it for me”** button on:

  - contact import

  - invoice template setup

  - payment setup

  - AR reminder setup

These become **service SKUs** or free onboarding help.

## **“Do it for me” service SKUs (launch set)**

- Setup & cleanup:

  - “We import your contacts + templates”

  - “We set up your invoicing + payment links”

- Revenue acceleration:

  - “We send invoice reminders weekly”

- Bookkeeping starter:

  - “We categorize 50 receipts for you”

## **Onboarding success instrumentation (must track)**

- `tenant.profile_selected

  `

- `channel.connected

  `

- `contacts.imported` / `contacts.created

  `

- `invoice.sent` (activation milestone)

- `payment.succeeded` (value milestone)

- `service.requested` (service attach)

## **Human playbook (internal)**

- If no invoice sent by Day 2 → trigger outreach:

  - “Send us your last 10 customers and we’ll set it up”

- If invoice sent but no payment by Day 5 → offer AR follow-up service

---

# **7.4. Final “Success Gates” (for your calculative approach)**

Before charging money publicly, you must confirm with 5–10 pilots:

1. **TTFV**: 60%+ send an invoice within 7 days

2. **Core loop**: at least 2 invoices/month per tenant

3. **Churn signal**: they return weekly without reminders

4. **Ops efficiency**: QC time per AI draft stays within your target

5. **Support load**: onboarding questions are solvable via templates + “do it for me”

---

---

---

**8. PRD Step 7 — Schema Evolution Plan, Profile Engine Spec v1, POS Integration Blueprint**

---

# **8.1. Data Migrations + Versioning Plan**

## **8.1.1. Goals**

- **Zero-downtime schema changes**

- **Backward-compatible APIs**

- **Safe backfills** on large datasets

- **Predictable rollbacks**

- **Tenant-safe** at every step

## **8.1.2. Core Rules (non-negotiable)**

1. **Expand → Migrate/Backfill → Contract** (never “break then fix”)

2. Any new column is:

   - `NULL`able first, with a safe default behavior in code

3. No destructive changes without:

   - a shadow period + usage verification + rollout plan

4. All writes must include `tenant_id` (enforced in API layer)

## **8.1.3. Migration Workflow (standard)**

### **Step A — Expand (safe)**

- Add new columns/tables/indexes (non-blocking where possible)

- Keep old columns still supported

- Deploy backend that can read/write both (if needed)

### **Step B — Backfill (async)**

- Background job backfills old rows → new format

- Idempotent backfill (restart safe)

- Track progress per tenant:

  - `migration_jobs` table or job metadata in Redis

### **Step C — Switch reads**

- Feature flag flips reads to new format

- Monitor error rate + performance

### **Step D — Contract (cleanup)**

- Remove old fields/endpoints only after a full release cycle

- Drop columns/tables last

## **8.1.4. Backfill & Data Repair Patterns**

### **Pattern 1: Dual-write**

When you change structure (e.g., split a json field into normalized table):

- Write to **both** old and new for a period

- Read from old until backfill completes

- Then swap reads

### **Pattern 2: Versioned payloads**

For JSON fields like `line_items` or `labels_json`:

- Store as:

  - `payload_version: 1

    `

  - `payload: { … }

    `

- Backend can parse v1/v2 side-by-side

### **Pattern 3: Shadow validation**

During backfill:

- Compare old-derived value vs new-derived value

- If mismatch rate > threshold → stop and alert

## **8.1.5. API Versioning (keep it simple)**

- Keep API namespace: `/v1/\*

  `

- Use **backward-compatible changes** within v1:

  - add fields

  - add endpoints

  - never change meaning of existing fields

- If you must break: introduce `/v2/*` only when necessary

## **8.1.6. Rollback Strategy**

- **Code rollback** must still work with expanded schema

- Avoid schema changes that require reverting DB state

- Never drop columns until you’re certain rollback won’t need them

## **8.1.7. Migration Testing Checklist**

- Migration runs on empty DB + seeded DB

- Downgrade path tested (where feasible)

- Tenant isolation tests still pass

- Large table index creation uses safe method (or scheduled low-traffic window)

---

# **8.2. Profile Engine Spec v1 (Generalized SMB Support)**

## **8.2.1. What the Profile Engine does**

A **Profile** is a configuration object that controls:

- labels/terminology (Request vs Job vs Order)

- required fields per object

- feature flags (capabilities)

- workflow defaults (status model + conversions)

- templates and message presets

- automation rules (AR reminders, follow-ups)

- integration presets (POS connectors enabled)

**Key idea:** Same core objects; profile only changes behavior + defaults.

## **8.2.2. Where profiles live**

Recommended:

- `profiles` stored as versioned JSON (in DB)

- `tenants.profile_id` points to active profile

- Runtime merges:

  - `base_profile` + `selected_profile` + `tenant_overrides

    `

Tables:

    profiles (id, name, version, config_json, created_at)



    tenant_profile_overrides (tenant_id, overrides_json, updated_at)

## **8.2.3. Profile JSON Schema (v1)**

Below is the minimal schema you should lock:

    {
      "profile_id": "general",
      "version": 1,
      "labels": {
        "work_item": "Request",
        "work_item_plural": "Requests",
        "contact_customer": "Customer",
        "contact_vendor": "Vendor"
      },
      "capabilities": {
        "inbox": true,
        "quotes": true,
        "invoices": true,
        "payments": true,
        "expenses": true,
        "client_portal": true,

        "pos_sync": false,
        "scheduling_lite": false,
        "inventory_lite": false,
        "returns_lite": false
      },
      "required_fields": {
        "work_item": ["title"],
        "invoice": ["contact_id", "issue_date", "due_date", "line_items"],
        "quote": ["contact_id", "line_items"],
        "expense": ["expense_date", "amount"]
      },
      "workflows": {
        "work_item_statuses": ["NEW", "IN_PROGRESS", "NEEDS_APPROVAL", "WAITING", "DONE", "CANCELED"],
        "default_work_item_type": "REQUEST",
        "conversion_rules": {
          "work_item_to_invoice": true,
          "quote_to_invoice": true
        }
      },
      "extensions": {
        "work_item_fields": {
          "service_address": { "type": "string", "required": false },
          "location_note": { "type": "string", "required": false }
        }
      },
      "automations": {
        "ar_reminders": { "enabled": true, "days_after_due": [3, 7, 14] }
      },
      "templates": {
        "invoice_default_template_id": "tpl_invoice_default_v1",
        "quote_default_template_id": "tpl_quote_default_v1",
        "message_payment_link_template_id": "tpl_msg_paylink_v1"
      },
      "integrations": {
        "presets": []
      }
    }

## **8.2.4. Two MVP Profiles to ship**

### **Profile A:** `general` **(works for most SMBs)**

- capabilities: invoices/quotes/expenses/inbox/portal ON

- scheduling OFF by default

- no POS sync

### **Profile B:** `retail_pos` **(POS-led retail via integration)**

- `pos_sync: true

  `

- `returns_lite: true

  `

- invoices still exist (for receipts, special invoices, or B2B)

- AR reminders usually off (retail is instant pay), but keep for edge cases

Example delta (retail_pos overrides):

    {
      "profile_id": "retail_pos",
      "version": 1,
      "labels": { "work_item": "Order Issue" },
      "capabilities": {
        "pos_sync": true,
        "returns_lite": true,
        "inventory_lite": false
      },
      "required_fields": {
        "work_item": ["title", "labels_json.external_order_id"]
      },
      "integrations": {
        "presets": ["square", "shopify"]
      }
    }

## **8.2.5. Runtime behavior rules**

- UI reads `capabilities` to show/hide modules

- Backend validates using `required_fields` before state transitions like:

  - sending invoice

  - converting quote → invoice

- `extensions.work_item_fields` maps into `WorkItem.labels_json

  `

---

# **8.3. POS Integration Blueprint (Retail Inclusion Without Building a POS)**

## **8.3.1. POS Strategy (your success-safe approach)**

You do **not** try to be “the POS.”\
&#x20;You become the **SMB OS** that:

- pulls POS activity into your timeline

- connects sales to contacts

- handles customer communication + issues

- provides consolidated finance snapshot

- enables “done-for-you” back-office services

## **8.3.2. What to integrate (MVP scope)**

### **MVP POS Data You Need (minimum viable)**

1. **Orders / Sales** (completed transactions)

2. **Payments** (tenders)

3. **Refunds/Returns** (if supported)

4. **Customers** (if captured)

5. **Daily summaries** (optional but useful)

Skip for MVP:

- full inventory management

- employee/timeclock

- menu/table systems (restaurants later)

## **8.3.3. Integration architecture**

### **Components**

- **IntegrationConnection**

  - provider name (square/shopify/…)

  - tenant_id

  - auth tokens (encrypted)

  - status (connected/disconnected)

  - scopes granted

- **ExternalEntityMap**

  - maps provider IDs to internal IDs

- **SyncCursor**

  - last sync timestamp / cursor token per entity type

- **WebhookReceiver**

  - verifies signatures + enqueues jobs

- **SyncWorker**

  - pulls deltas on schedule (polling fallback)

### **Suggested DB tables**

    integration_connections(id, tenant_id, provider, status, auth_json, created_at)



    external_entity_map(id, tenant_id, provider, external_id, entity_type, internal_id, created_at)



    sync_cursors(id, tenant_id, provider, entity_type, cursor, updated_at)



    webhook_events(id, tenant_id, provider, event_id, payload_json, received_at, processed_at, status)

## **8.3.4. Mapping rules (POS → SMB Hub objects)**

### **Orders / Sales**

- Create internal **Receipt** representation.\
  &#x20;You have two options:

**Option 1 (recommended): store as a Work Item type**

- `WorkItem.type = ORDER

  `

- `labels_json` holds:

  - `external_order_id

    `

  - `location_id

    `

  - `items_summary

    `

  - `total

    `

  - `paid_at

    `

- Pros: single object model stays consistent

- Cons: money reporting needs aggregation

**Option 2: add** `sales_receipts` **table**

- cleaner financial reporting

- still links to contact + timeline

- recommended if retail becomes big early

**MVP recommendation:** Option 1 now, Option 2 later if needed.

### **Payments**

- For instant-pay retail, payments belong to the order/receipt.

- You can still create `Payment` records if:

  - you want unified payment reporting across non-retail

  - you want consolidated cashflow dashboard

- If you do create `Payment`:

  - mark `provider = POS_PROVIDER

    `

  - link to `invoice_id` nullable

  - link to `work_item_id` via `labels_json

    `

### **Refunds/Returns**

- Create `WorkItem.type = SUPPORT` or `ORDER` with `status=NEW

  `

- `labels_json.refund_id`, `labels_json.reason

  `

- This becomes your operational queue for retail issues

### **Customers**

- If customer has email/phone:

  - upsert into `Contacts

    `

  - map external customer id to contact id in `external_entity_map

    `

## **8.3.5. Sync methods (how data gets in)**

### **Primary: Webhooks**

- Receive webhook → verify signature → store webhook event → enqueue processing

- Make processing **idempotent**:

  - unique key = provider event id OR external order id

### **Fallback: Scheduled Polling**

- Every X minutes:

  - sync orders since cursor

  - sync refunds since cursor

- Polling is essential because webhooks can be missed.

## **8.3.6. Idempotency rules (critical)**

- Every external object must have a unique “natural key”

  - order_id, payment_id, refund_id

- Upserts must be safe if replayed 10 times

- Webhook processing must not create duplicates:

  - enforce unique constraints or idempotency keys

## **8.3.7. MVP Retail UX (how it appears in the app)**

When `profile_id = retail_pos`:

- Work module label becomes: **Orders / Issues**

- Work list shows:

  - recent orders

  - returns/refund issues (auto-created)

- Contact timeline shows:

  - receipts/orders and their totals

- Money dashboard shows:

  - daily totals (from POS sync) + expenses + invoices (if any)

This keeps retail owners inside your system without rebuilding POS.

## **8.3.8. Restaurant note (later, not MVP)**

Restaurants often need:

- table/reservations

- tips

- split bills

- kitchen routing\
  &#x20;That’s not “basic retail.” Keep restaurant as a **future profile** built on the same POS integration layer.

---

# **8.4. Deliverables Locked in Step 7**

✅ Zero-downtime migration process (expand/backfill/contract)\
✅ Profile Engine JSON schema v1 + two MVP profiles (general + retail_pos)\
✅ POS integration blueprint with safe sync + mapping + idempotency

---

---

---

\

**9. PRD Step 8 — Profile Engine Implementation Plan (Code Modules, Merge Rules, Validation Hooks, UI/API Behavior)**

Goal: implement Profiles as **configuration** that safely changes UI + validations + defaults without branching the codebase.

---

# **9.1. System Overview**

## **9.1.1. Where Profile Engine sits**

- **Backend is source of truth** for:

  - effective profile config

  - required field validations

  - workflow defaults

  - capability enforcement

- **Frontend consumes** “effective profile” to:

  - show/hide modules

  - rename labels

  - enforce light client-side validations (backend remains final gate)

## **9.1.2. Core requirements**

- Profiles are **versioned**

- Each tenant has:

  - `profile_id

    `

  - optional `tenant_overrides

    `

- Backend returns a single object:

  - `effective_profile = merge(base_profile, selected_profile, tenant_overrides)

    `

---

# **9.2 Backend Implementation (FastAPI)**

## **9.2.1. Backend modules (suggested folder structure)**

    app/
      core/
        auth_clerk.py
        tenancy.py
        rbac.py
        settings.py
      profile_engine/
        loader.py
        schema.py
        merger.py
        validator.py
        capabilities.py
        defaults.py
      domain/
        contacts/
        work_items/
        invoices/
        quotes/
        expenses/
        inbox/
      api/
        v1/
          routes_profile.py
          routes_contacts.py
          routes_work_items.py
          routes_invoices.py
          routes_quotes.py
          routes_expenses.py
          routes_inbox.py

### **Responsibilities**

- `loader.py
` Fetch profile config JSON by `tenant.profile_id` + overrides.

- `schema.py
` Pydantic models that validate profile JSON (and enforce version).

- `merger.py
` Merge base + profile + override into **effective profile**.

- `capabilities.py
` Helper checks: “is pos_sync enabled?”

- `defaults.py
` Provides default labels, default work item type, default templates, etc.

- `validator.py
` Enforces required fields and workflow rules during operations.

---

## **9.2.2. Profile storage options (choose one)**

### **Option A (recommended): DB-stored profiles + overrides**

- `profiles(config_json)

  `

- `tenant_profile_overrides(overrides_json)
` Pros: editable from admin UI later, versioning easy.\
  &#x20;Cons: more DB reads → cache it.

### **Option B: Profiles as JSON files in repo + overrides in DB**

Pros: simpler to start, controlled releases.\
&#x20;Cons: slower to “hot edit” profiles.

**MVP recommendation:** Option A + caching.

---

## **9.2.3. Caching strategy (important)**

Use Redis cache:

- key: `profile:tenant:{tenant_id}:effective

  `

- TTL: 5–15 minutes (or invalidate on update)

- Invalidation triggers:

  - profile changed

  - override changed

  - template defaults changed

---

# **9.3. Merge Rules (Base → Profile → Tenant Override)**

## **9.3.1. Merge priority**

1. `base_profile` (default safe settings)

2. `selected_profile` (e.g., retail_pos)

3. `tenant_overrides` (business-specific tweaks)

## **9.3.2. Merge semantics (rule by field type)**

### **Scalars (strings, bools, numbers)**

- override replaces value

### **Objects (maps)**

- deep merge by key

- keys not present remain from lower layer

### **Arrays**

Use explicit strategy per field:

- `capabilities`: merged by key (object not array)

- `work_item_statuses`: **replace** (so a profile can define a different set)

- `required_fields`: merge by object keys; each entity list **replace** unless explicitly additive

- `templates`: deep merge

### **Example: required fields merge**

- base: `invoice: [contact_id, line_items]

  `

- retail_pos: `invoice: [contact_id, line_items, tax_code]` → replace invoice list

- tenant override: `invoice: [contact_id, line_items]` → replace again

**Rule:** Lists are replaced, not appended, unless you define an `append_fields` mechanism (not needed in MVP).

---

# **9.4. Validation Hooks (Backend Enforcement)**

## **9.4.1. Validation timing**

Run profile validation at these moments:

### **A) Before state transitions**

- sending invoice

- converting quote → invoice

- applying AI draft

- closing work item (optional)

### **B) Before creating objects (light)**

- use required fields during create if fields must exist at creation

## **9.4.2. Validator API**

Create a single interface:

    validate(entity_type, payload, operation, effective_profile) -> errors[]

Where:

- `entity_type`: `invoice | quote | work_item | expense

  `

- `operation`: `create | update | send | convert | apply_ai

  `

- returns:

  - list of `{field, message, code}

    `

## **9.4.3. Capability enforcement**

Before route handler logic:

- `require_capability("quotes")` for quote endpoints

- `require_capability("pos_sync")` for POS routes\
  &#x20;If disabled:

- return `403` with structured error: `CAPABILITY_DISABLED

  `

## **9.4.4. Required fields enforcement examples**

### **Invoice send**

Profile says invoice requires:

- `contact_id`, `issue_date`, `due_date`, `line_items
` Validation:

- contact must exist and be ACTIVE

- line_items must have length >= 1

- total > 0

- channel send requires contact email or phone

### **Work item creation**

Profile requires:

- `title
` Retail profile may require:

- `labels_json.external_order_id` (for order issues)

---

# **9.5. Defaults System (How profiles influence behavior without adding code paths)**

## **9.5.1. Defaults to apply on create**

- default work item type

- default status

- default templates

- default AR reminder schedule (if enabled)

Backend `defaults.py` should provide:

    apply_defaults(entity_type, payload, effective_profile) -> payload

Example:

- If tenant profile is retail_pos:

  - `WorkItem.type default = ORDER

    `

  - label name = “Order Issue” in UI

- If general:

  - default = REQUEST

---

# **9.6. How Profile Affects UI Navigation (Frontend Plan)**

## **9.6.1. Fetch effective profile**

On app bootstrap:

- `GET /v1/profile` returns `effective_profile

  `

Cache client-side in:

- React context store (ProfileContext)

- refresh on tenant switch

## **9.6.2. UI gating rules**

Frontend shows/hides modules based on:

    effective_profile.capabilities

Example:

- If `quotes=false`: hide Quotes tab and conversion option

- If `pos_sync=true`: show “POS” section under Settings and “Orders/Issues” label on Work

## **9.6.3. Terminology**

Use `labels` in profile to render:

- “Work Items” label

- “Customers” label

- “Orders/Issues” label for retail profile

No UI hardcoding of industry terms.

## **9.6.4. Form behavior**

- Use `required_fields` for basic UI required markers

- Backend remains final validator (UI only helps user)

---

# **9.7. API Behavior Changes Driven by Profile**

## **9.7.1. API outputs include “UI hints”**

In many responses, include:

- `display_label` for types (optional)

- `allowed_actions` for an object based on:

  - role

  - status

  - capabilities

  - required fields satisfied

Example: invoice detail response:

    allowed_actions: ["send", "create_payment_link", "void"]

This reduces FE logic errors.

## **9.7.2. Conversion actions**

`POST /v1/work-items/{id}/convert`:

- backend checks profile conversion rules:

  - can convert to invoice?

  - requires fields?

- returns either:

  - created draft object id

  - or validation errors list

---

# **9.8. Admin UX for Overrides (MVP-lite)**

You can delay full admin UI, but you should support:

- setting profile at tenant creation

- basic override of:

  - AR reminder schedule

  - default templates

  - enable/disable quotes

Routes:

- `PATCH /v1/profile/tenant-overrides` (OWNER/ADMIN only)

---

# **9.9. Testing Plan for Profile Engine**

## **9.9.1. Unit tests**

- merge rules: base + profile + override determinism

- required fields validation works per profile

- capability enforcement blocks endpoints

## **9.9.2. Integration tests**

- same endpoint behaves differently under different profiles:

  - retail_pos requires external_order_id for ORDER work items

  - general does not

- invoice send forbidden if `payments=false` or missing required fields

## **9.9.3. Regression test pack**

- for each profile version:

  - run snapshot tests on `GET /v1/profile

    `

  - run conversion flows:

    - work_item → invoice

    - quote → invoice (if enabled)

---

# **9.10. Implementation Checklist (What “done” looks like)**

✅ `GET /v1/profile` returns merged effective profile\
✅ Frontend hides/shows nav and labels based on profile\
✅ Backend validators enforce required fields and capabilities\
✅ Conversions respect profile rules\
✅ Tenant overrides supported and cached\
✅ Tests cover merge + enforcement + regressions

---

---

---

**10. PRD Step 9 — MVP UX Blueprint (Layouts, Interaction Rules, Text-to-Task UX)**

Goal: make SMB Hub feel like “one-stop OS” with **fast actions, minimal clicks, and safe automation**.

---

# **10.1. UX Principles (MVP)**

1. **Front door = Inbox** (every message can become work or money)

2. **One universal object = Work Item** (request/order/job/ticket)

3. **Money is always one tap away** (invoice + pay link)

4. **Automation is safe** (AI drafts never send/charge without approval)

5. **Two-pane desktop, single-pane mobile** for speed

6. **3-second rule**: any core task starts in ≤3 seconds (create work item, draft invoice, send link)

---

# **10.2. App Information Architecture (Navigation)**

### **Desktop (left nav)**

- Home

- Inbox

- Work

- Contacts

- Quotes _(profile-gated)_

- Invoices

- Expenses

- Settings

### **Mobile (bottom nav)**

- Home

- Inbox

- Work

- Money _(Invoices)_

- More _(Contacts, Expenses, Settings)_

Profile-driven labels:

- Work label can be “Requests”, “Jobs”, “Orders/Issues” etc. via Profile Engine.

---

# **10.3. Layout Blueprint by Screen (Component Tree)**

## **10.3.1. Home (Snapshot)**

**Layout**

- Top row: KPI cards (Unpaid, Overdue, New Work, Today’s Payments)

- Middle: “Next actions” list (overdue invoices + urgent work)

- Bottom: Quick actions strip (New invoice, New request, Upload receipt, Compose)

**Components**

    KpiCardGrid



    NextActionsList



    QuickActionBar

**Interactions**

- Clicking KPI filters the target list (e.g., Overdue → Invoices list with overdue filter)

- Quick Action opens modal, not a new page (speed)

---

## **10.3.2. Inbox (Desktop two-pane)**

**Left pane (List)**

- Search

- Filters: Open/Closed, Assigned, Channel

- Conversation items: contact, snippet, time, badges (unread, linked work/invoice)

**Right pane (Thread)**

- Header: Contact chip + assign + status + **Convert actions**

- Thread: messages + attachments

- Composer: text + attach + send

**Convert actions in header (most important)**

- `Create Work Item

  `

- `Draft Invoice

  `

- `Draft Quote` _(if enabled)_

- `Draft Expense

  `

- `AI: Turn into…` _(opens AI panel)_

**Components**

    ConversationListPane



    ConversationThreadPane



    ConvertActionGroup



    MessageComposer

**Speed rules**

- “Create Work Item” opens a **mini modal** with only: title, type, due, assign.

- “Draft Invoice” opens invoice drawer prefilled with contact + message context.

---

## **10.3.3. Work (List + Detail)**

**Desktop**

- Left: Work list with filters

- Right: Work detail

**Work detail sections**

1. Header: title + status + priority + due + assigned

2. Context: linked contact + linked conversation

3. Notes (editable)

4. Linked objects: quote/invoice/payment

5. Files

6. Activity timeline

**Primary actions**

- Convert → Invoice (top right)

- Convert → Quote

- “Send Update” (message from here; optional MVP)

**Components**

    WorkList



    WorkDetailHeader



    WorkContextPanel



    LinkedObjectsPanel



    FilePanel



    ActivityTimeline

---

## **10.3.4. Contacts (List + Detail)**

**List**

- Search

- Tabs: Customers / Vendors / Leads (or filter dropdown)

**Detail**

- Contact profile (phone/email/address/tags)

- Timeline feed (messages, invoices, work items, files)

- Quick actions: New invoice, New work item, Message

**Components**

    ContactList



    ContactProfileCard



    ContactTimeline

---

## **10.3.5. Invoices (List + Drawer Editor)**

**List**

- Filters: Draft/Sent/Paid/Overdue

- Inline quick actions:

  - Send

  - Copy pay link

  - Mark paid (manual)

- Bulk actions NOT in MVP

**Invoice editor opens as a drawer**

- Header: contact + dates + invoice #

- Line items: quick add

- Totals: auto

- Payment: generate link

- Send: channel + template

**Components**

    InvoiceList



    InvoiceEditorDrawer



    LineItemTable



    PaymentLinkCard



    SendInvoicePanel

**Key UX rule**

- Invoice stays “Draft” until:

  - send succeeded OR you explicitly mark “Sent” (if manual)

- Payment link can be created without sending.

---

## **10.3.6. Expenses (Capture-first)**

**Top**

- Big “Upload receipt” button

- Recent uploads preview

**List**

- Draft/Submitted/Approved tabs

**Draft editor (drawer)**

- vendor/date/amount/category + receipt preview

- Submit button

**Components**

    ReceiptUploader



    ExpenseList



    ExpenseDrawer

---

# **10.4. Universal Interaction Rules (MVP)**

## **10.4.1. Global command bar (optional but powerful)**

- Shortcut: `/` or `Ctrl+K

  `

- Actions:

  - create work item

  - create invoice

  - search contact

  - upload receipt\
    &#x20;This is huge for “easy to operate”.

## **10.4.2. One-tap conversions everywhere**

From:

- Inbox thread

- Work item detail

- Contact detail\
  &#x20;You can:

- draft invoice

- draft quote

- create work item\
  &#x20;No complex wizard.

## **10.4.3. Allowed actions are server-driven**

Backend returns `allowed_actions[]` for objects.\
&#x20;Frontend renders buttons based on that list to reduce logic bugs.

---

# **10.5. Text-to-Task UX (Magical but Safe)**

## **10.5.1. Entry points**

- Inbox: **AI: Turn into…**

- Receipt upload: “Extract details”

- Work item: “Generate invoice from notes”

- Portal (later): client message triggers draft work item

## **10.5.2. AI panel design (side panel)**

When triggered, open an AI panel with 3 steps:

### **Step 1 — “What should this become?”**

AI shows 2–3 suggested intents:

- Create Work Item

- Draft Invoice

- Draft Expense\
  &#x20;(Quote if enabled)

User chooses or accepts default.

### **Step 2 — Draft preview (editable)**

AI presents a structured draft:

- For Work Item: title, type, due, priority, notes

- For Invoice: line items, totals, due date, notes

- For Expense: vendor/date/amount/category

Include:

- **Confidence indicator** (High/Med/Low)

- Highlight extracted fields from text

### **Step 3 — Apply**

Buttons:

- **Apply as Draft** (creates object in DRAFT state)

- Apply + Assign (for work item)

- Reject / Create manually

**Safety rule**

- AI can **never**:

  - send invoice

  - charge payment

  - message the customer\
    &#x20;without explicit user action.

## **10.5.3. Human QC mode (SwaS)**

If tenant has “Do it for me” enabled:

- “Send to team for review” button appears

- Draft status becomes `PENDING_QC

  `

- Ops Command Center sees it and can edit/apply

## **10.5.4. Anti-duplicate guard**

When applying drafts:

- show “This seems similar to existing invoice/work item” if:

  - same contact + same day + similar amount/title

- user chooses:

  - merge

  - create anyway

---

# **10.6. Microcopy & UI Text (MVP)**

Use short business-friendly language:

- “Turn into Work”

- “Draft invoice”

- “Copy payment link”

- “Send reminder”

- “Upload receipt”

Avoid “tickets”, “pipelines”, “workflows” in UI unless profile requires.

---

# **10.7. Accessibility & Mobile Usability (must-have)**

- keyboard navigation for lists/drawers

- visible focus states

- large tap targets on mobile

- offline tolerance: view cached lists (optional)

---

# **10.8. MVP UX Acceptance Criteria**

1. Inbox → Work Item created in ≤30s

2. Work Item → Invoice draft created in ≤60s

3. Invoice → Payment link copied in ≤10s

4. Client pays → invoice status updates automatically

5. AI draft preview is editable + safe (never auto-send)

---

---

---

**11. PRD Step 10 — Wireframe-Level Screen Specs + UI Component Library**

# **11.1. Global UI Components (build once, reuse everywhere)**

### **Layout**

- `AppShell` (nav + header + content)

- `TwoPaneLayout` (list left, detail right)

- `Drawer` (right-side editor)

- `Modal` (quick create)

### **Data display**

- `DataTableLite` (simple list rows, not heavy tables)

- `FilterBar` (chips + dropdowns)

- `SearchInput

  `

- `StatusPill

  `

- `AssigneeChip

  `

- `TagChips

  `

- `EmptyState

  `

- `SkeletonList

  `

- `Toast

  `

### **Forms**

    FormField



    DatePicker



    MoneyInput



    PhoneInput



    Select



    InlineError

### **Files**

- `FileDropzone

  `

- `AttachmentList

  `

- `FilePreview` (image/pdf)

### **Timeline**

    ActivityTimeline

### **AI**

- `AIPanel` (side panel)

- `ConfidenceBadge

  `

- `DiffHighlighter` (shows what AI extracted/changed)

### **Portal**

    PortalPageShell



    PublicTokenErrorState

---

# **11.2. Screen Specs (exact layout + fields + states)**

## **Screen 1: Home**

**Route:** `/home`

**Sections**

1. KPI Cards (4)

- Unpaid Invoices (count + total due)

- Overdue (count + total overdue)

- New Work Items (count)

- Today’s Payments (count + total)

2. Next Actions (list max 8)

- Overdue invoices sorted by due date

- Urgent/high priority work items sorted by due date

3. Quick Actions

- New Invoice

- New Work Item

- Upload Receipt

- Compose Message

**Empty state**

- If no data: show onboarding CTA buttons (create contact, create invoice)

---

## **Screen 2: Inbox List (Two-pane)**

**Route:** `/inbox`

### **Left Pane — Conversation List**

**Filters**

- Status: Open / Closed

- Channel: Email / SMS

- Assigned: Me / Unassigned / Anyone (role-gated)\
  &#x20;**Search**

- contact name, email, phone, subject

**Row fields**

- Contact display name (or “Unknown”)

- Last message snippet (1 line)

- Timestamp

- Badges: unread, linked WorkItem, linked Invoice

**States**

- Loading skeleton

- Empty “No conversations yet”

- Error with retry

### **Right Pane — Conversation Thread**

**Header**

- Contact chip (click → contact detail)

- Channel badge

- Assign dropdown (role-gated)

- Open/Close toggle

- Convert group:

  - Create Work Item

  - Draft Invoice

  - Draft Quote (profile)

  - Draft Expense

  - AI Turn into…

**Thread**

- Message cards:

  - direction, timestamp

  - body (text)

  - attachments preview list

**Composer**

- Textarea

- Attach button

- Send button

**Validation**

- Send requires a route (email for email thread, phone for sms thread)

- Attachment size/type restrictions

---

## **Screen 3: Create Work Item (Quick Modal)**

**Launch from:** Inbox header, Work list, Contact detail

**Fields**

- Type (default from profile; hidden if only one type in profile)

- Title (required)

- Contact (optional / required if launched from invoice flow)

- Priority (default Normal)

- Due date (optional)

- Assign to (optional)

- Description (optional)

**Buttons**

- Create

- Create + Draft Invoice (if invoices enabled)

**Errors**

- Title empty

- Due date invalid (warning)

---

## **Screen 4: Work List + Work Detail**

**Route:** `/work`

### **Work List**

**Filters**

- Status

- Type

- Priority

- Assigned

- Due date (overdue / today / this week)

**Row fields**

- Title

- Contact name

- Status pill

- Due date

- Assignee

- Icons for linked quote/invoice

### **Work Detail**

**Header**

- Title

- Status dropdown

- Priority dropdown

- Due date picker

- Assignee dropdown

- Primary actions:

  - Convert → Invoice

  - Convert → Quote

**Body sections**

- Contact summary (mini card)

- Linked conversation (clickable)

- Notes editor (plain text)

- Files (upload + list)

- Activity timeline

**States**

- If deleted/not allowed: read-only error

---

## **Screen 5: Contacts List + Contact Detail**

**Route:** `/contacts`

### **List**

**Filters**

- Type: Customer/Vendor/Lead\
  &#x20;**Search**

- name/email/phone

**Row fields**

- Display name

- Company

- Email/Phone

- Tags

### **Detail**

**Header**

- Name + type

- Quick actions: New Invoice, New Work Item, Message

**Sections**

- Contact fields (editable)

- Timeline (messages, invoices, work items, payments, files)

---

## **Screen 6: Invoice List + Invoice Editor Drawer**

**Route:** `/invoices`

### **List**

**Filters**

- Status: Draft/Sent/Paid/Overdue

- Contact

- Date range

**Row**

- Invoice #

- Contact

- Total

- Due date

- Status

- Amount due

- Quick actions:

  - Send (if draft)

  - Copy Pay Link (if exists)

  - Mark Paid (manual)

### **Invoice Editor (Drawer)**

**Header**

- Invoice # (readonly)

- Status (Draft/Sent)

- Contact (required)

- Issue date (required)

- Due date (required)

- Currency (readonly default; editable only by owner/admin)

**Line Items**

- Add line

  - Item name (required)

  - Qty (default 1)

  - Rate (required)

  - Tax toggle (optional)

- Discount (optional)

- Totals panel (readonly): subtotal, tax, total

**Notes/Terms**

- Notes (optional)

- Terms (optional)

**Payment**

- Create payment link button

- Copy link button (after created)

**Send**

- Channel select (Email/SMS available)

- Template picker

- Message preview

- Send button

**Validations**

- Contact exists + has email/phone for chosen channel

- ≥1 line item

- Total > 0

- due_date ≥ issue_date

**States**

- Stripe link failed → show retry

- Send failed → show retry, do not mark “Sent”

---

## **Screen 7: Invoice Detail (Read)**

**Route:** `/invoices/{id}` (or opens from list)

**Sections**

- Summary card (status, totals, due, pay link)

- Payments list (amount, date, method)

- Activity timeline (sent/reminders/webhook events)

- Actions:

  - Send reminder

  - Void invoice (role-gated)

---

## **Screen 8: Expenses (Receipt Capture)**

**Route:** `/expenses`

**Top action**

- Upload receipt

**List**

- Tabs: Draft/Submitted/Approved

- Row: vendor, date, amount, category, status

**Expense Drawer**

- Receipt preview

- Vendor (optional)

- Date (required unless AI pending)

- Amount (required unless AI pending)

- Category (simple string)

- Notes

- Buttons: Save, Submit, Approve (role-gated)

---

## **Screen 9: AI Panel (Side Panel UX)**

**Opens from:** Inbox thread, receipt upload, work item

**Step 1 (Intent)**

- Suggested: Work Item / Invoice / Expense / Quote (if enabled)

**Step 2 (Draft Preview)**

- Structured fields editable

- Confidence badge

- Highlight extracted values

**Step 3 (Apply)**

- Apply as Draft (default)

- Send to QC (if service enabled)

- Reject

**Safety**

- No “send invoice” inside AI panel (must go through invoice send)

---

## **Screen 10: Ops Command Center (QC Queue)**

**Route:** `/ops/ai-drafts` (internal)

**List**

- Filters: status, tenant, confidence

- Row: intent, contact, created time, confidence, assigned reviewer

**Detail**

- Source message/file preview

- Draft payload editor

- Buttons: Approve+Apply, Reject, Save notes

**Rules**

- Apply is idempotent

- All actions logged

---

# **11.3. Client Portal Wireframes**

## **Portal Invoice Pay**

**Route:** `/portal/invoices/{token}
` **Fields**

- Business name/logo

- Invoice #, due date, total, status

- Pay button

- “Already paid” state

**Error states**

- Invalid token

- Expired token

- Payment failed

## **Portal Quote Approve**

**Route:** `/portal/quotes/{token}`

- Quote summary

- Approve/Reject buttons

- Confirmation state

---

---

---

**12. PRD Step 11 — Technical Execution Spec**

Scope: **API contracts (request/response), state machines, webhook + idempotency rules, background jobs, error model, and integration contracts** for the MVP.

---

# **12.1. Cross-Cutting Standards**

## **Auth & Tenancy (Clerk + Neon)**

**Client → API**

- Header: `Authorization: Bearer <clerk_session_jwt>

  `

**Backend rules**

- Verify JWT (JWKS)

- Extract `user_id`, `org_id

  `

- Resolve `tenant_id` by `tenants.clerk_org_id = org_id

  `

- Never accept `tenant_id` from client.

## **Response Envelope (standard)**

All endpoints return:

    {
      "data": {},
      "meta": { "request_id": "req_...", "cursor": null }
    }

## **Error Format (standard)**

    {
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invoice cannot be sent",
        "details": [
          { "field": "contact.email", "message": "Email is required for sending via email" }
        ]
      },
      "meta": { "request_id": "req_..." }
    }

Common `code` values:

- `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND

  `

- `CAPABILITY_DISABLED

  `

- `VALIDATION_ERROR

  `

- `PROVIDER_ERROR

  `

- `CONFLICT` (idempotency / duplicate)

- `RATE_LIMITED

  `

## **Pagination (lists)**

Query:

- `limit` (default 20, max 100)

- `cursor` (opaque string)

Response:

    {
      "data": [ ... ],
      "meta": { "cursor": "next_cursor", "request_id": "req_..." }
    }

## **Idempotency (client → API)**

For write endpoints that may be retried:

- Header: `Idempotency-Key: <uuid>
` Rules:

- Server stores `(tenant_id, endpoint, idempotency_key) → response_hash + object_id

  `

- Replay returns same response, no duplicate objects.

---

# **12.2. State Machines (Locked)**

## **A) WorkItem**

**Statuses**

- `NEW → IN_PROGRESS → DONE

  `

- Optional: `NEEDS_APPROVAL`, `WAITING

  `

- Any → `CANCELED

  `

**Rules**

- Only OWNER/ADMIN/STAFF can change status freely.

- AGENT can change status only on assigned items (default).

- Closing (`DONE`) requires:

  - `title` present

  - (optional profile rules) required labels present

**Events**

    work_item.created



    work_item.status_changed



    work_item.assigned

---

## **B) Quote**

**Statuses**

- `DRAFT → SENT → (APPROVED | REJECTED | EXPIRED)

  `

- `APPROVED → CONVERTED` (when invoice created)

**Rules**

- `SENT` requires `contact` + at least 1 line item + `total > 0

  `

- Portal approval requires valid token and quote is `SENT

  `

---

## **C) Invoice**

**Statuses**

    DRAFT → SENT



    SENT → (PARTIALLY_PAID | PAID | OVERDUE)



    DRAFT|SENT → VOID

**Rules**

- `SENT` requires:

  - `contact_id

    `

  - `issue_date`, `due_date` with `due_date >= issue_date

    `

  - `line_items` length >= 1

  - `total > 0

    `

  - delivery method exists (email/phone depending on channel)

- `OVERDUE` is derived (cron/job or query-time): `status=SENT` and `now > due_date` and `amount_due > 0

  `

- `VOID` disallows payment link usage and portal pay page returns “voided”

---

## **D) Conversation**

- `OPEN | CLOSED
` Rules:

- Closing does not delete, just hides from “Open” filter

---

## **E) AI Draft**

- `PENDING_QC | APPROVED | REJECTED | APPLIED
` Rules:

- `APPLIED` must be idempotent (apply again returns same target object id)

---

# **12.3. API Contracts (Key Endpoints)**

## **12.3.1. Profile**

### **GET** `/v1/profile`

Returns effective profile (base + profile + overrides).

    {
      "data": {
        "profile_id": "general",
        "version": 1,
        "labels": { "work_item": "Request" },
        "capabilities": { "quotes": true, "pos_sync": false },
        "required_fields": { "invoice": ["contact_id", "line_items"] }
      },
      "meta": { "request_id": "req_..." }
    }

---

## **12.3.2. Contacts**

### **POST** `/v1/contacts`

Request:

    {
      "display_name": "John Smith",
      "type": "CUSTOMER",
      "email": "john@example.com",
      "phone": "+1416..."
    }

Response:

    { "data": { "id": "uuid", "display_name": "John Smith" }, "meta": { "request_id": "req_..." } }

### **GET** `/v1/contacts?type=CUSTOMER&q=john&limit=20&cursor=...`

Returns list.

### **GET** `/v1/contacts/{id}/timeline`

Returns timeline items:

    {
      "data": [
        { "type": "invoice", "id": "inv_uuid", "title": "Invoice #INV-1002", "at": "..." },
        { "type": "message", "id": "msg_uuid", "title": "Inbound SMS", "at": "..." }
      ],
      "meta": { "request_id": "req_..." }
    }

---

## **12.3.3. Work Items**

### **POST** `/v1/work-items`

Request:

    {
      "type": "REQUEST",
      "title": "Fix leaking faucet",
      "contact_id": "uuid",
      "priority": "NORMAL",
      "due_at": "2026-01-02T18:00:00Z",
      "assigned_to": "user_x",
      "description": "Customer says leak under sink",
      "labels_json": { "service_address": "123 King St" }
    }

Response includes `allowed_actions`:

    {
      "data": {
        "id": "uuid",
        "status": "NEW",
        "allowed_actions": ["update", "convert_to_invoice", "convert_to_quote"]
      },
      "meta": { "request_id": "req_..." }
    }

### **PATCH** `/v1/work-items/{id}`

Partial updates; server validates per profile.

### **POST** `/v1/work-items/{id}/convert`

Request:

    { "target": "INVOICE" }

Response:

    {
      "data": { "invoice_id": "uuid", "created": true },
      "meta": { "request_id": "req_..." }
    }

If missing required fields (like contact), return `VALIDATION_ERROR`.

---

## **12.3.4. Quotes**

### **POST** `/v1/quotes`

Request:

    {
      "contact_id": "uuid",
      "issue_date": "2025-12-28",
      "expiry_date": "2026-01-05",
      "line_items": [{ "name": "Service", "qty": 1, "rate": 120 }],
      "notes": "Thanks!"
    }

### **POST** `/v1/quotes/{id}/send`

Request:

    { "channel": "EMAIL", "message": "Please approve this quote." }

### **POST** `/portal/quotes/{public_token}/approve`

Response:

    { "data": { "status": "APPROVED" }, "meta": { "request_id": "req_..." } }

---

## **12.3.5. Invoices**

### **POST** `/v1/invoices`

Request:

    {
      "contact_id": "uuid",
      "issue_date": "2025-12-28",
      "due_date": "2026-01-05",
      "line_items": [{ "name": "Repair", "qty": 1, "rate": 200 }],
      "notes": "Payment due in 7 days"
    }

### **POST** `/v1/invoices/{id}/payment-link`

Response:

    {
      "data": { "payment_link_url": "https://..." },
      "meta": { "request_id": "req_..." }
    }

### **POST** `/v1/invoices/{id}/send`

Request:

    { "channel": "EMAIL", "message": "Here is your invoice. Pay with the link." }

Rules:

- If provider fails → `PROVIDER_ERROR`, invoice remains DRAFT (or remains SENT only if you explicitly choose optimistic mode; recommended: set SENT only on success)

### **POST** `/v1/invoices/{id}/void`

Sets status VOID; logs audit.

---

## **12.3.6. Payments**

### **POST** `/v1/payments` **(manual)**

    {
      "invoice_id": "uuid",
      "provider": "CASH",
      "amount": 200,
      "paid_at": "2025-12-28T14:00:00Z"
    }

### **POST** `/v1/webhooks/stripe`

Handled by webhook processor (see 11.5).

---

## **12.3.7. Files**

### **POST** `/v1/files/presign`

Request:

    { "file_name": "receipt.jpg", "mime_type": "image/jpeg", "size_bytes": 123456 }

Response:

    {
      "data": {
        "file_id": "uuid",
        "upload_url": "https://presigned...",
        "object_key": "tenant/.../uuid"
      }
    }

### **POST** `/v1/files/{file_id}/link`

Request:

    { "linked_entity_type": "EXPENSE", "linked_entity_id": "uuid" }

---

## **12.3.8. Export**

### **POST** `/v1/export`

Returns job:

    { "data": { "job_id": "uuid", "status": "QUEUED" } }

### **GET** `/v1/export/{job_id}`

Returns status + download link when ready.

---

# **12.4. Background Jobs (Workers) + Retry Rules**

## **Job Queue Types**

- `AI_PARSE` (message/file → AI Draft)

- `EXPORT_BUILD

  `

- `AR_REMINDER_SEND

  `

- `POS_SYNC` (later)

- `WEBHOOK_PROCESS` (Stripe, email provider events)

## **Retry Policy (standard)**

- Max retries: 8

- Backoff: exponential (e.g., 30s, 2m, 5m, 15m, 1h…)

- Permanent failure → mark job FAILED with reason, alert if payment-related.

## **Idempotency in jobs**

Every job must have a deterministic idempotency key:

- Stripe: `(provider_event_id)`

- Export: `(tenant_id, date_bucket, requested_by, job_kind)`

- AI Apply: `(ai_draft_id)`

- AR Reminder: `(invoice_id, reminder_stage)`

---

# **12.5. Webhooks + Idempotency (Stripe)**

## **Stripe Webhook Handler Rules**

1. Verify signature.

2. Store raw event in `webhook_events` table:

   - `provider_event_id` unique

   - status = RECEIVED

3. Enqueue `WEBHOOK_PROCESS` with `provider_event_id`.

4. Worker loads event and applies changes idempotently:

   - If already PROCESSED → no-op

## **Event handling (MVP minimal)**

- `checkout.session.completed` OR `payment_intent.succeeded` (depending on integration)\
  &#x20;Actions:

- Find invoice via metadata (recommended: store `invoice_id` in Stripe metadata)

- Create Payment row if not exists:

  - unique key `(tenant_id, provider, provider_payment_id)`

- Update invoice aggregates:

  - `amount_paid`, `amount_due`

  - set status `PAID` if `amount_due == 0` else `PARTIALLY_PAID`

- Write audit logs.

**Hard rule:** webhook processing must be replay-safe 10x.

---

# **12.6. Portal Token Security (Invoice/Quote)**

## **Token requirements**

- Random, high-entropy tokens (not sequential)

- Stored hashed (recommended) OR stored raw with strict access controls

- Must be revocable:

  - `portal_tokens` table with `revoked_at

    `

## **Rate limits**

- Portal endpoints: e.g., 30 req/min/IP (tune later)

- Invalid token attempts should be throttled.

## **Portal responses**

- Never expose internal `tenant_id` or user identifiers

- Only show business name + invoice/quote details relevant to the token.

---

# **12.7. “Allowed Actions” Computation (Server-driven UI)**

Each object detail endpoint returns:

- `allowed_actions[]` computed from:

  - role permissions

  - object status

  - profile capabilities

  - required fields satisfied

Example invoice:

- If status DRAFT and has contact email: `["send", "create_payment_link", "update", "void"]

  `

- If PAID: `["download_receipt"]` (optional)

This reduces frontend logic bugs.

---

# **12.8. Concurrency + Data Integrity Rules**

## **Optimistic concurrency (recommended)**

- Use `updated_at` or `version` integer

- PATCH requests include `if_match_version

  `

- If mismatch → `409 CONFLICT` and return latest object

## **Unique constraints (must-have)**

- `tenants.clerk_org_id` unique

- `tenant_members (tenant_id, user_id)` unique

- `invoices (tenant_id, invoice_number)` unique

- `quotes (tenant_id, quote_number)` unique

- `webhook_events.provider_event_id` unique

- `payments (tenant_id, provider, provider_payment_id)` unique (when provider_payment_id exists)

---

# **12.9. Logging + Analytics Correlation**

Every API request:

- generate/propagate `request_id

  `

- include in logs + response meta\
  &#x20;Every key action emits analytics event (Step 3 list), including `request_id` to correlate UI ↔ API.

---

---

---

**13. PRD Step 12 — MVP Scope Lock + Launch Readiness Pack (Final)**

This is the **final PRD step**. After this, you have everything needed to build, pilot, and launch without scope creep.

---

# **13.1. MVP Scope Lock (What we ship, and what we don’t)**

## **13.1.1. MVP Modules (LOCKED)**

### **Core Platform**

- Clerk auth + organizations (tenant)

- RBAC (OWNER/ADMIN/STAFF/AGENT/VIEWER)

- Profile Engine v1 (general + retail_pos)

- Audit logs (critical actions)

- One-click export (trust)

### **Inbox (Email-first)**

- Conversations list + thread view

- Send message (email reply)

- Convert conversation → Work Item

- Create contact from unknown sender

### **Work Items (Universal Ops)**

- Work list + filters

- Work detail + status + assignment

- Files + timeline

- Convert Work Item → invoice/quote

### **Money Core**

- Invoices: draft, totals, payment link, send

- Client portal invoice pay (token)

- Stripe webhook → auto-update invoice paid/partial

- AR reminder (manual)

### **Quotes**

- Quote create/send

- Portal approve/reject (token)

- Convert quote → invoice

### **Expenses (Capture-first)**

- Upload receipt → expense draft

- Edit + submit/approve (simple)

### **Text-to-Task (Safe automation)**

- AI Draft creation from message/file/manual

- Ops QC queue approve/reject/edit/apply

- No auto-send, no auto-charge

---

## **13.1.2. Explicitly Out of Scope (LOCKED)**

(You will not build these in MVP)

- Full accounting ledger, payroll, full HRMS

- Full CRM pipeline / marketing automation suite

- Full POS replacement (retail is integration-first, phase later)

- Scheduling engine (unless minimal “due date + assignment” only)

- WhatsApp, SMS outbound (optional Phase 1.5 after email is stable)

- Inventory management, time tracking, restaurant table systems

- Enterprise SSO/SAML

**Rule:** Any new request must map to a locked epic OR goes to Phase 2 backlog.

---

# **13.2. Definition of “Launch-Ready” (Hard Gates)**

You launch only when these pass in staging AND one pilot tenant in prod.

## **Security & data**

- ✅ Tenant isolation suite passes (no cross-tenant reads/writes)

- ✅ RBAC enforced server-side for all endpoints

- ✅ Portal token security suite passes (rate limits + revocation)

- ✅ Stripe webhook idempotency suite passes (replays safe)

## **Reliability**

- ✅ Email send failures handled + retry path exists

- ✅ Background jobs retry with backoff

- ✅ Monitoring alerts exist for:

  - webhook failure rate

  - queue backlog

  - repeated permission denials

  - message send failures

## **Product**

- ✅ Activation loop works:

  - create contact → create invoice → send → client pays → paid status updates

- ✅ Inbox → Work conversion works under 30 seconds

- ✅ One-click export works (async ok)

---

# **13.3. Go-Live Checklist (5-minute deploy verification)**

Run this after every production deploy.

1. **Auth**

- Login works

- Org switch loads correct tenant

2. **Core CRUD**

- Create a contact

- Create a work item

3. **Invoice loop**

- Create invoice draft

- Create payment link

- Send invoice email (to test email)

- Open portal link works

4. **Webhook**

- Trigger test payment → invoice becomes PAID (or run webhook replay test)

5. **Telemetry**

- Sentry receives a test error (optional)

- Logs show request_id + tenant_id

6. **Export**

- Start export job → shows queued/running state

---

# **13.4. Pilot Plan (to maximize success probability)**

## **Pilot size & timeline**

- 5–10 SMBs, 30 days

- Mix:

  - 70% “general” (service + solo + small teams)

  - 30% retail POS-led (integration later, but profile UX tested now)

## **Pilot selection criteria**

Choose SMBs that:

- invoice at least **2–10 times per month**

- have at least **one pain**: scattered tools / slow billing / AR issues

- will use email daily (since Inbox is email-first)

## **Pilot onboarding script (your “done-for-you” wedge)**

Day 0 (30–45 min call):

- Set up business profile + templates

- Import 20 contacts

- Create and send 2 invoices together

- Turn on payment links

Day 2 follow-up:

- If no invoice sent → offer “we set it up for you” service

Day 7:

- Review:

  - payments received

  - overdue invoices

  - friction points

## **Pilot success criteria (must-hit)**

- **Activation:** 60%+ send invoice within 7 days

- **Value:** 40%+ receive at least one payment through portal within 14 days

- **Retention:** 30%+ return weekly without reminders

- **Support load:** onboarding issues solvable with templates/services

---

# **13.5. Pricing Skeleton (MVP positioning)**

You can refine later, but you need a simple structure for launch.

## **Recommended model: SaaS + Services (your core strategy)**

### **Plan A: Starter (Owner-only)**

- Invoices + portal + contacts + expenses capture

- Limited AI drafts/month

- Export included (trust)

### **Plan B: Team**

- Multi-users (org members)

- Inbox + work assignments

- Higher AI limits

- AR reminders

### **Plan C: Pro**

- Advanced templates + automations

- QC queue + “done-for-you” lane

- Priority support

### **Services (add-ons)**

- “Onboarding setup” (contacts + templates + payment setup)

- “Weekly AR follow-up”

- “Monthly bookkeeping starter” (receipt cleanup)

**Key:** Don’t compete on “more features.” Compete on “less effort + faster cash.”

---

# **13.6. Support Playbooks (Launch essentials)**

## **Playbook 1 — “Invoice not sending”**

Checklist:

- contact has email?

- provider status page (if applicable)

- retry send

- check logs by request_id\
  &#x20;Resolution:

- keep invoice in DRAFT until success

- show “Send failed” with retry

## **Playbook 2 — “Payment made but invoice not marked paid”**

Checklist:

- webhook event received?

- webhook signature valid?

- idempotency conflict?

- invoice_id metadata present?\
  &#x20;Resolution:

- reprocess webhook event

- manual reconcile fallback

- alert if repeated failures

## **Playbook 3 — “Portal link not working”**

Checklist:

- token revoked/expired?

- invoice voided?

- rate limited?\
  &#x20;Resolution:

- regenerate token

- resend invoice

## **Playbook 4 — “Wrong business data showing”**

Checklist:

- Clerk org mismatch?

- tenant mapping missing?

- user belongs to multiple orgs?\
  &#x20;Resolution:

- force org switch

- re-run tenant mapping

- audit tenant_id in logs

---

# **13.7. Phase 2 Backlog (parking lot, not now)**

Only after MVP proves traction:

- SMS/WhatsApp channels

- POS sync (Square/Shopify ingestion)

- Scheduling lite (appointments)

- CRM lite (pipeline)

- Basic bookkeeping workflows (rules + categorization)

- Multi-location support (retail/service)

- “App marketplace” for add-on services
