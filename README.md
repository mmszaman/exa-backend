# SMB Hub Backend - Multi-Tenant SaaS Platform

Professional, scalable FastAPI backend with **Clerk authentication** and multi-tenant architecture.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Clerk (see CLERK_SETUP_CHECKLIST.md)
cp .env.example .env
# Add your Clerk keys to .env

# 3. Run database migrations
alembic upgrade head

# 4. Start server
python server.py
```

## 🔐 Authentication

This backend uses **Clerk** for authentication with built-in multi-tenancy support.

- ✅ Email/password + social OAuth
- ✅ Organization-based multi-tenancy
- ✅ Automatic user provisioning via webhooks
- ✅ JWT token verification

**Setup Guide**: See [docs/CLERK_AUTHENTICATION.md](docs/CLERK_AUTHENTICATION.md)  
**Quick Checklist**: See [CLERK_SETUP_CHECKLIST.md](CLERK_SETUP_CHECKLIST.md)

## 📁 Folder Structure

```
smb-backend/
├── app/
│   ├── api/
│   │   ├── deps.py                  # Auth dependencies (CurrentUser, etc.)
│   │   └── v1/
│   │       ├── auth.py              # Clerk webhooks & user endpoints
│   │       └── email.py             # Email sending
│   ├── core/
│   │   ├── config.py                # Environment settings (incl. Clerk)
│   │   ├── database.py              # Database connection
│   │   ├── logger.py                # Logging setup
│   │   ├── rate_limit.py            # Rate limiting
│   │   └── security.py              # Utility functions
│   ├── middleware/
│   │   ├── clerk_auth.py            # Clerk JWT verification
│   │   └── csrf.py                  # CSRF protection
│   ├── models/
│   │   ├── user.py                  # User model (Clerk-integrated)
│   │   └── lead.py                  # Marketing leads
│   ├── schemas/
│   │   ├── user_schema.py           # User API schemas
│   │   └── email_schema.py          # Email schemas
│   ├── services/
│   │   ├── user_service.py          # User sync with Clerk
│   │   ├── email_service.py         # SMTP email sending
│   │   └── email_render.py          # Template rendering
│   └── templates/
│       └── email/                   # Email templates
├── alembic/
│   └── versions/                    # Database migrations
├── docs/
│   ├── CLERK_AUTHENTICATION.md      # Full Clerk setup guide
│   └── ...
├── .copilot/
│   └── copilot-context.md           # Project architecture rules
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── CLERK_SETUP_CHECKLIST.md         # Setup checklist
└── server.py                        # Entry point
```
- **Testable** — Services can be mocked; conftest provides fixtures
- **Maintainable** — Clear separation of concerns (schemas, logic, endpoints)
- **Scalable** — Add new routers (users, payments, etc.) without touching existing code
- **Professional** — Follows FastAPI docs & industry standards

## Quick Start

1. Create virtual environment & install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy env template and configure:

```powershell
copy .env.example .env
# Edit .env with real email creds or set DEV_FAKE_EMAILS=1 for testing
```

3. Run the server:

```powershell
python run.py
# OR
uvicorn app.main:app --reload --port 8000
```

4. Check health:

```
curl http://localhost:8000/health
```

## Development

Install dev dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run tests:

```powershell
pytest app/tests/ -v
```

Code formatting:

```powershell
black app/
```

Linting:

```powershell
flake8 app/
```

## API Endpoints

### Health & Monitoring
- `GET /health` — Application health check (status + timestamp)
- `GET /api/email/check` — Email service health check (SMTP connectivity test)

### Email Operations
- `POST /api/email/send` — Send plain or HTML emails to recipients
- `POST /api/email/send-template` — Send template-based emails with dynamic content

### Notifications
- `POST /api/notify-email` — Subscribe email for notifications

## Email API Usage

### Send Plain/HTML Email

```bash
POST /api/email/send
Content-Type: application/json

{
  "recipients": ["user@example.com"],
  "subject": "Welcome to Exa!",
  "from_name": "Exa Team",
  "from_email": "support@exateks.com",
  "body_text": "Welcome to our platform!",
  "body_html": "<h1>Welcome to our platform!</h1>"
}
```

### Send Template Email

```bash
POST /api/email/send-template
Content-Type: application/json

{
  "recipients": ["user@example.com"],
  "template_name": "welcome",
  "subject": "Welcome to Exateks!",
  "from_name": "Exateks Team",
  "context": {
    "user_name": "John Doe",
    "verify_url": "https://example.com/verify/abc123"
  }
}
```

### Available Email Templates

1. **welcome** - Welcome new users
   - Required: `user_name`
   - Optional: `verify_url`

2. **password_reset** - Password reset instructions
   - Required: `user_name`, `reset_url`
   - Optional: `expiry_hours` (default: 1)

3. **email_verification** - Email verification link
   - Required: `user_name`, `verify_url`
   - Optional: `verification_code`, `expiry_hours` (default: 24)

4. **user_notification** - General notification with custom content
   - Required: `user_name`, `title`, `message`
   - Optional: `website_url`, `action_url`, `action_text`

## Environment Variables

See `.env.example` for all available options. Key ones:

**Required for Email Sending:**
- `EMAIL_USER` — Gmail address (e.g., support@exateks.com)
- `EMAIL_PASSWORD` — Gmail app password ([How to create](https://support.google.com/accounts/answer/185833))
- `EMAIL_HOST` — SMTP server (default: smtp.gmail.com)
- `EMAIL_PORT` — SMTP port (default: 587)

**Optional:**
- `DEV_FAKE_EMAILS` — Set to 1 to log emails locally instead of sending (for development)
- `DEBUG` — Set to 1 for hot-reload during development
- `ALLOWED_ORIGINS` — CORS allowed origins (comma-separated)

## Future Expansion

To add new endpoints:

1. Create schema in `schemas/` (Pydantic models for validation)
2. Create service in `services/` (business logic)
3. Create router in `routers/` (API endpoints)
4. Include router in `app/main.py`
5. Add tests in `tests/`

**To add new email templates:**

1. Create HTML template in `app/templates/email/` (extend `base_template.html`)
2. Define context variables using Jinja2 syntax (`{{ variable_name }}`)
3. Add template name to validation in `email_schema.py`
4. Document template and required context variables

Example: adding user authentication would be `routers/auth.py` + `services/auth_service.py` + `schemas/auth.py`.

## Project Architecture

**Why This Structure?**

- **Modular** — Each feature gets its own router; easy to add new endpoints
- **Testable** — Services can be mocked; pytest fixtures in conftest
- **Maintainable** — Clear separation of concerns (schemas, logic, endpoints, templates)
- **Scalable** — Add new routers (users, payments, etc.) without touching existing code
- **Professional** — Follows FastAPI docs & industry standards

**Service Design:**

- **EmailService** - SMTP operations (single responsibility: sending)
- **EmailRender** - Template rendering (Jinja2 HTML + text conversion)
- **Router** - Combines services, handles HTTP layer and validation
