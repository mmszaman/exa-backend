from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os
import logging
from dotenv import load_dotenv
import aiosmtplib
from email.message import EmailMessage
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

# Load .env from backend folder if present
load_dotenv()

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="Exakeep Notify Backend")

# Allow requests from the Next.js dev server by default
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NotifyRequest(BaseModel):
    email: EmailStr


def make_message(subject: str, html: str, text: str, from_addr: str, to_addr: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    return msg


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/notify-email")
async def notify_email(payload: NotifyRequest):
    email = payload.email

    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ADMIN_TO = os.getenv("ADMIN_TO", "exateks@gmail.com")

    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("EMAIL_USER/EMAIL_PASSWORD missing in environment")
        raise HTTPException(status_code=500, detail="Server email configuration missing")

    # Dev mode: optionally log to file instead of sending
    if os.getenv("DEV_FAKE_EMAILS", "0") == "1":
        log_entry = {
            "to": ADMIN_TO,
            "user_email": email,
            "timestamp": datetime.utcnow().isoformat(),
        }
        logfile = os.getenv("DEV_FAKE_LOG", "sent_emails.log")
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        return {"success": True, "message": f"Saved to local log ({logfile})"}

    # Build messages
    admin_html = f"""
      <h2>New Notification Request</h2>
      <p><strong>Email:</strong> {email}</p>
      <p><strong>Timestamp:</strong> {datetime.utcnow().isoformat()}Z</p>
    """
    admin_text = f"New Notification Request\n\nEmail: {email}\nTimestamp: {datetime.utcnow().isoformat()}Z\n"

    user_html = """
      <h2>Thank You!</h2>
      <p>We've received your notification request. We'll send you an email as soon as our website is back online.</p>
      <p>Best regards,<br/>Exakeep Team</p>
    """
    user_text = "Thank you! We've received your notification request. We'll notify you when we're back online.\n\n- Exakeep Team"

    # Send via aiosmtplib
    try:
        smtp = aiosmtplib.SMTP(hostname=EMAIL_HOST, port=EMAIL_PORT, start_tls=True)
        await smtp.connect()
        # start_tls() will be called by aiosmtplib when start_tls=True during connect
        await smtp.login(EMAIL_USER, EMAIL_PASSWORD)

        # Send admin message
        admin_msg = make_message(
            subject="New Notification Request - Exakeep",
            html=admin_html,
            text=admin_text,
            from_addr=EMAIL_USER,
            to_addr=ADMIN_TO,
        )
        await smtp.send_message(admin_msg)

        # Send confirmation to user
        user_msg = make_message(
            subject="Notification Request Confirmed - Exakeep",
            html=user_html,
            text=user_text,
            from_addr=EMAIL_USER,
            to_addr=email,
        )
        await smtp.send_message(user_msg)

        await smtp.quit()

    except Exception as exc:
        logger.exception("Failed to send email")
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"success": True, "message": "Email notification request received"}
