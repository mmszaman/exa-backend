"""Email service - handles SMTP communication and message construction."""

import logging
import json
from datetime import datetime
from email.message import EmailMessage
import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP or logging in dev mode."""

    @staticmethod
    def make_message(
        subject: str, html: str, text: str, from_addr: str, to_addr: str
    ) -> EmailMessage:
        """Construct an EmailMessage with both HTML and text parts."""
        msg = EmailMessage()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")
        return msg

    @staticmethod
    async def send_notification_email(user_email: str) -> bool:
        """
        Send notification emails (admin + user confirmation).
        Returns True on success, raises exception on failure.
        """

        # Dev mode: log to file instead of sending
        if settings.DEV_FAKE_EMAILS:
            log_entry = {
                "to": settings.ADMIN_TO,
                "user_email": user_email,
                "timestamp": datetime.utcnow().isoformat(),
            }
            try:
                with open(settings.DEV_FAKE_LOG, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
                logger.info(f"[DEV] Email logged to {settings.DEV_FAKE_LOG}: {user_email}")
                return True
            except IOError as e:
                logger.error(f"[DEV] Failed to write email log: {e}")
                raise

        # Production: send via SMTP
        if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
            logger.error("EMAIL_USER or EMAIL_PASSWORD not configured")
            raise ValueError("Email credentials not configured")

        # Build email messages
        timestamp = datetime.utcnow().isoformat()

        admin_html = f"""
            <h2>New Notification Request</h2>
            <p><strong>Email:</strong> {user_email}</p>
            <p><strong>Timestamp:</strong> {timestamp}Z</p>
        """
        admin_text = (
            f"New Notification Request\n\n"
            f"Email: {user_email}\n"
            f"Timestamp: {timestamp}Z\n"
        )

        user_html = """
            <h2>Thank You!</h2>
            <p>We've received your notification request. We'll send you an email as soon as our website is back online.</p>
            <p>Best regards,<br/>Exakeep Team</p>
        """
        user_text = (
            "Thank you! We've received your notification request. "
            "We'll notify you when we're back online.\n\n- Exakeep Team"
        )

        try:
            # Connect to SMTP server
            smtp = aiosmtplib.SMTP(
                hostname=settings.EMAIL_HOST, port=settings.EMAIL_PORT, start_tls=True
            )
            await smtp.connect()
            await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)

            # Send admin email
            admin_msg = EmailService.make_message(
                subject="New Notification Request - Exakeep",
                html=admin_html,
                text=admin_text,
                from_addr=settings.EMAIL_USER,
                to_addr=settings.ADMIN_TO,
            )
            await smtp.send_message(admin_msg)
            logger.info(f"Admin email sent to {settings.ADMIN_TO} for user {user_email}")

            # Send confirmation to user
            user_msg = EmailService.make_message(
                subject="Notification Request Confirmed - Exakeep",
                html=user_html,
                text=user_text,
                from_addr=settings.EMAIL_USER,
                to_addr=user_email,
            )
            await smtp.send_message(user_msg)
            logger.info(f"Confirmation email sent to {user_email}")

            await smtp.quit()
            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise
