"""
Email Router - API endpoints for sending emails
"""

import asyncio
import aiosmtplib
from fastapi import APIRouter, HTTPException, status

from app.services.email_service import EmailService
from app.services.email_render import template_service
from app.core.logger import get_logger
from app.schemas.email_schema import (
    SendEmailRequest, 
    SendEmailResponse, 
    EmailSendResult,
    SendTemplateEmailRequest
)
from app.config import settings

# Create router
router = APIRouter(prefix="/api/email", tags=["email"])
logger = get_logger("email_router")


@router.post("/send", response_model=SendEmailResponse, status_code=status.HTTP_200_OK)
async def send_email(request: SendEmailRequest):
    """
    Send email to one or more recipients.
    
    **Features:**
    - Send to multiple recipients
    - HTML and plain text support
    - Custom sender name and email
    - Detailed results for each recipient
    - Automatic logging
    
    **Example Request:**
    ```json
    {
        "recipients": ["user@example.com"],
        "subject": "Welcome to Exa!",
        "from_name": "Exa Team",
        "from_email": "support@exateks.com"
        "body_text": "Welcome to our platform!",
        "body_html": "<h1>Welcome to our platform!</h1>"
    }
    ```
    """
    logger.info(f"📧 Email send request received for {len(request.recipients)} recipient(s)")
    logger.debug(f"Subject: {request.subject}")
    
    try:
        # Send emails using the email service
        results = await EmailService.send_email(
            recipients=request.recipients,
            subject=request.subject,
            from_name=request.from_name,
            from_email=request.from_email,
            body_text=request.body_text,
            body_html=request.body_html
        )
        
        # Convert results to response format
        email_results = [
            EmailSendResult(
                recipient=r.recipient,
                success=r.success,
                error=r.error,
                sent_at=r.sent_at
            )
            for r in results
        ]
        
        # Calculate totals
        total_sent = sum(1 for r in results if r.success)
        total_failed = len(results) - total_sent
        
        # Determine overall success
        all_successful = total_failed == 0
        
        # Build response message
        if all_successful:
            message = f"Successfully sent email to all {total_sent} recipient(s)"
        elif total_sent > 0:
            message = f"Partially successful: {total_sent} sent, {total_failed} failed"
        else:
            message = f"All emails failed to send"
        
        logger.info(f"✅ Email send completed: {message}")
        
        return SendEmailResponse(
            success=all_successful,
            total_sent=total_sent,
            total_failed=total_failed,
            results=email_results,
            message=message
        )
        
    except ValueError as e:
        # Configuration error (e.g., missing credentials)
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email service configuration error: {str(e)}"
        )
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error sending email: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.post("/send-template", response_model=SendEmailResponse, status_code=status.HTTP_200_OK)
async def send_template_email(request: SendTemplateEmailRequest):
    """
    Send template-based email to one or more recipients.
    
    **Features:**
    - Use pre-designed HTML email templates
    - Dynamic variable substitution
    - Custom subject and sender name
    - Template validation
    - Detailed results for each recipient
    
    **Available Templates:**
    - `welcome` - Welcome new users
    - `password_reset` - Password reset instructions
    - `email_verification` - Email verification link
    - `user_notification` - General notification with custom content
    
    **Example Request:**
    ```json
    {
        "recipients": ["user@example.com"],
        "template_name": "welcome",
        "context": {
            "user_name": "John Doe",
            "verify_url": "https://example.com/verify/abc123"
        }
    }
    ```
    
    **Context Variables by Template:**
    
    **welcome:**
    - `user_name` - User's display name
    - `verify_url` - Email verification link (optional)
    
    **password_reset:**
    - `user_name` - User's display name
    - `reset_url` - Password reset link
    - `expiry_hours` - Link expiry time (default: 1)
    
    **email_verification:**
    - `user_name` - User's display name
    - `verify_url` - Verification link
    - `verification_code` - Manual verification code (optional)
    - `expiry_hours` - Link expiry time (default: 24)
    
    **user_notification:**
    - `user_name` - User's display name
    - `title` - Title of notification
    - `message` - Main notification message
    - `website_url` - Website URL (optional)
    - `action_url` - Button link (optional)
    - `action_text` - Button text (optional)
    """
    logger.info(f"📧 Template email send request - Template: '{request.template_name}' to {len(request.recipients)} recipient(s)")
    logger.debug(f"Context variables: {list(request.context.keys())}")
    
    try:
        # Render template (simple - just get HTML and text bodies)
        try:
            body_html, body_text = template_service.render_template(
                template_name=request.template_name,
                context=request.context
            )
            
            logger.debug(f"Template rendered: HTML {len(body_html)} chars, Text {len(body_text)} chars")
            
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template error: {str(e)}"
            )
        
        # Get subject and from_name (passed by caller, just like EmailService)
        subject = request.subject
        from_name = request.from_name or "Exa"
        
        logger.debug(f"Subject: {subject}")
        logger.debug(f"From Name: {from_name}")
        
        # Send emails using the email service
        results = await EmailService.send_email(
            recipients=request.recipients,
            subject=subject,
            from_name=from_name,
            from_email=request.from_email,
            body_text=body_text,
            body_html=body_html
        )
        
        # Convert results to response format
        email_results = [
            EmailSendResult(
                recipient=r.recipient,
                success=r.success,
                error=r.error,
                sent_at=r.sent_at
            )
            for r in results
        ]
        
        # Calculate totals
        total_sent = sum(1 for r in results if r.success)
        total_failed = len(results) - total_sent
        
        # Determine overall success
        all_successful = total_failed == 0
        
        # Build response message
        if all_successful:
            message = f"Successfully sent '{request.template_name}' template to all {total_sent} recipient(s)"
        elif total_sent > 0:
            message = f"Partially successful: {total_sent} sent, {total_failed} failed"
        else:
            message = f"All template emails failed to send"
        
        logger.info(f"✅ Template email send completed: {message}")
        
        return SendEmailResponse(
            success=all_successful,
            total_sent=total_sent,
            total_failed=total_failed,
            results=email_results,
            message=message
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except ValueError as e:
        # Configuration or validation error
        logger.error(f"Configuration/validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error sending template email: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send template email: {str(e)}"
        )


@router.get("/check", status_code=status.HTTP_200_OK)
async def check_email_service():
    """
    Health check - validates configuration and tests SMTP connectivity.
    
    Checks:
        1. Are email credentials configured?
        2. Can we connect to SMTP server?
        3. Can we authenticate with credentials?
    
    Returns detailed health status including connection and authentication state.
    Response time: 1-3 seconds (includes SMTP connection test)
    """
    logger.info("🔍 Email service health check requested")
    
    # Check if configured
    is_configured = bool(settings.EMAIL_USER and settings.EMAIL_PASSWORD)
    
    health_status = {
        "service": "email",
        "configured": is_configured,
        "smtp_host": settings.EMAIL_HOST,
        "smtp_port": settings.EMAIL_PORT,
    }
    
    # If not configured, return early
    if not is_configured:
        health_status["status"] = "not_configured"
        health_status["ready"] = False
        health_status["message"] = "Email credentials not configured"
        logger.warning("⚠️ Email service not configured")
        return health_status
    
    # Test actual SMTP connection
    try:
        logger.debug(f"Testing SMTP connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        smtp = aiosmtplib.SMTP(
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            start_tls=True,
            timeout=5  # 5 second timeout
        )
        
        # Try to connect
        await smtp.connect()
        logger.debug("SMTP connection successful")
        
        # Try to authenticate
        await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        logger.debug("SMTP authentication successful")
        
        # Disconnect
        await smtp.quit()
        
        # All checks passed
        health_status["status"] = "healthy"
        health_status["ready"] = True
        health_status["smtp_connection"] = "connected"
        health_status["smtp_authentication"] = "authenticated"
        health_status["message"] = "Email service is fully operational"
        logger.info("✅ Email service health check passed - service is healthy")
        
    except aiosmtplib.SMTPConnectError as e:
        health_status["status"] = "unhealthy"
        health_status["ready"] = False
        health_status["smtp_connection"] = "failed"
        health_status["error"] = f"Cannot connect to SMTP server: {str(e)}"
        health_status["message"] = "SMTP server unreachable"
        logger.error(f"❌ SMTP connection failed: {str(e)}")
        
    except aiosmtplib.SMTPAuthenticationError as e:
        health_status["status"] = "unhealthy"
        health_status["ready"] = False
        health_status["smtp_connection"] = "connected"
        health_status["smtp_authentication"] = "failed"
        health_status["error"] = f"Authentication failed: {str(e)}"
        health_status["message"] = "Invalid email credentials"
        logger.error(f"❌ SMTP authentication failed: {str(e)}")
        
    except asyncio.TimeoutError:
        health_status["status"] = "unhealthy"
        health_status["ready"] = False
        health_status["smtp_connection"] = "timeout"
        health_status["error"] = "Connection timeout"
        health_status["message"] = "SMTP server not responding"
        logger.error("❌ SMTP connection timeout - server not responding")
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["ready"] = False
        health_status["error"] = f"{type(e).__name__}: {str(e)}"
        health_status["message"] = "Email service error"
        logger.error(f"❌ Unexpected error during health check: {type(e).__name__}: {str(e)}")
    
    return health_status
