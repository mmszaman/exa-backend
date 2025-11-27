"""Notification endpoints - email subscriptions for maintenance notifications."""

import logging
from fastapi import APIRouter, HTTPException

from app.schemas.notification import NotifyEmailRequest, NotifyEmailResponse
from app.services.email_service import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/notify-email", response_model=NotifyEmailResponse)
async def notify_email(payload: NotifyEmailRequest):
    """
    Subscribe user email for website maintenance notifications.
    Sends confirmation email to user and notification to admin.

    Args:
        payload: NotifyEmailRequest with user email

    Returns:
        NotifyEmailResponse with success status and message

    Raises:
        HTTPException 500: If email service fails
    """
    try:
        # Use email service to send emails
        await EmailService.send_notification_email(payload.email)

        return {
            "success": True,
            "message": "Email notification request received",
        }

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=500, detail="Server email configuration missing"
        )
    except Exception as e:
        logger.error(f"Error sending notification email: {e}")
        raise HTTPException(status_code=500, detail="Failed to process notification request")
