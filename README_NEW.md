# Exakeep Backend - FastAPI

Professional, scalable backend following FastAPI best practices.

## Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # App initialization & middleware
│   ├── config.py                    # Environment settings
│   ├── core/
│   │   ├── __init__.py
│   │   └── logger.py                # Logging setup
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── notification.py          # Pydantic models (validation)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py                # Health check endpoint
│   │   └── notifications.py         # /notify-email endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   └── email_service.py         # Email business logic
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py              # Pytest fixtures
│       └── test_notifications.py    # Unit tests
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── run.py                           # Entry point
└── README.md
```

## Why This Structure?

- **Modular** — Each feature gets its own router; easy to add new endpoints
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

## Endpoints

- `GET /health` — Health check (status + timestamp)
- `POST /api/notify-email` — Subscribe email for notifications

## Environment Variables

See `.env.example` for all available options. Key ones:

- `EMAIL_USER` — Gmail address
- `EMAIL_PASSWORD` — Gmail app password
- `DEV_FAKE_EMAILS` — Set to 1 to log emails locally instead of sending
- `DEBUG` — Set to 1 for hot-reload during development

## Future Expansion

To add new endpoints:

1. Create schema in `schemas/`
2. Create service in `services/` (business logic)
3. Create router in `routers/`
4. Include router in `app/main.py`
5. Add tests in `tests/`

Example: adding user authentication would be `routers/auth.py` + `services/auth_service.py` + `schemas/auth.py`.
