# Exakeep Backend (FastAPI)

This small backend implements a `/notify-email` endpoint used by the Next.js frontend to request notification when the website is back online.

## Quick start (local)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy the example env and update values:

```powershell
copy .env.example .env
# then edit backend/.env and put real creds (or leave DEV_FAKE_EMAILS=1 for local testing)
```

4. Run the server:

```powershell
uvicorn main:app --reload --port 8000
```

The endpoint will be available at `http://localhost:8000/notify-email`.

## Notes
- For development you can set `DEV_FAKE_EMAILS=1` to save requests to `sent_emails.log` instead of actually sending email.
- For production use a transactional email provider (SendGrid, Mailgun, SES) and keep credentials in a secure secret store.