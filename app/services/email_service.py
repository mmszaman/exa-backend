"""
Email Service - Handles all email operations including SMTP and batch sending.
"""

import asyncio
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import List, Optional, Tuple
import aiosmtplib

from app.config import settings
from app.core.logger import get_logger
from app.schemas.email_schema import EmailSendResult

# Get logger for this service
logger = get_logger('email_service')


class EmailService:
    """
    Service for sending emails via SMTP.
    Handles connection, composition, and batch sending.
    """
    
    @staticmethod
    def _create_email_message(
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> EmailMessage:
        """
        Create an email message with text and optional HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            from_email: Sender email (defaults to config)
            from_name: Sender name (optional)
            
        Returns:
            EmailMessage: Configured email message
        """
        msg = EmailMessage()
        
        # Set sender - use SEND_FROM if available, otherwise EMAIL_USER
        from_email = from_email or settings.SEND_FROM or settings.EMAIL_USER
        if from_name:
            msg['From'] = f"{from_name} <{from_email}>"
        else:
            msg['From'] = from_email
        
        # Set recipient and subject
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Set plain text content
        msg.set_content(body_text)
        
        # Add HTML alternative if provided
        if body_html:
            msg.add_alternative(body_html, subtype='html')
        
        logger.debug(f"Created email message for {to_email}: {subject}")
        return msg
    
    @staticmethod
    async def _send_single_email(
        smtp: aiosmtplib.SMTP,
        message: EmailMessage,
        recipient: str
    ) -> EmailSendResult:
        """
        Send a single email via SMTP connection.
        
        Args:
            smtp: Active SMTP connection
            message: Email message to send
            recipient: Recipient email address
            
        Returns:
            EmailSendResult: Result of send attempt
        """
        try:
            await smtp.send_message(message)
            sent_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Email sent successfully to {recipient}")
            
            return EmailSendResult(
                recipient=recipient,
                success=True,
                error=None,
                sent_at=sent_at
            )
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"❌ Failed to send email to {recipient}: {error_msg}")
            
            return EmailSendResult(
                recipient=recipient,
                success=False,
                error=error_msg,
                sent_at=None
            )
    
    @staticmethod
    async def send_email(
        recipients: List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_name: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> List[EmailSendResult]:
        """
        Send email to multiple recipients via SMTP.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            from_name: Optional sender name
            from_email: Optional sender email (defaults to EMAIL_USER)
            
        Returns:
            List[EmailSendResult]: Results for each recipient
            
        Raises:
            ValueError: If email credentials not configured
            Exception: If SMTP connection fails
        """
        # Validate configuration
        if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
            error_msg = "Email credentials not configured (EMAIL_USER/EMAIL_PASSWORD)"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"📧 Starting email send to {len(recipients)} recipient(s)")
        logger.debug(f"Subject: {subject}")
        
        results = []
        
        try:
            # Connect to SMTP server
            logger.debug(f"Connecting to SMTP server {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            
            smtp = aiosmtplib.SMTP(
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                start_tls=True
            )
            
            await smtp.connect()
            logger.debug("SMTP connection established")
            
            # Login
            await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            logger.debug(f"Authenticated as {settings.EMAIL_USER}")
            
            # Send to each recipient
            for recipient in recipients:
                logger.debug(f"Sending to {recipient}...")
                
                # Create message for this recipient
                message = EmailService._create_email_message(
                    to_email=recipient,
                    subject=subject,
                    body_text=body_text,
                    body_html=body_html,
                    from_name=from_name,
                    from_email=from_email
                )
                
                # Send email
                result = await EmailService._send_single_email(smtp, message, recipient)
                results.append(result)
                
                # Small delay between emails to avoid rate limiting
                if len(recipients) > 1:
                    await asyncio.sleep(0.5)  # 500ms delay
            
            # Disconnect
            await smtp.quit()
            logger.debug("SMTP connection closed")
            
        except aiosmtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except aiosmtplib.SMTPConnectError as e:
            error_msg = f"Failed to connect to SMTP server: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Email service error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        logger.info(f"📊 Email send complete: {successful} successful, {failed} failed")
        
        return results
    
    @staticmethod
    async def send_notification_email(
        recipient: str,
        subject: str,
        message: str,
        results: List[EmailSendResult]
    ) -> bool:
        """
        Send notification email about batch send results.
        
        Args:
            recipient: Email to send notification to
            subject: Notification subject
            message: Base message
            results: List of send results to include
            
        Returns:
            bool: True if notification sent successfully
        """
        logger.info(f"📬 Sending notification to {recipient}")
        
        # Build notification body
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        body_text = f"{message}\n\n"
        body_text += f"Summary:\n"
        body_text += f"- Total: {len(results)}\n"
        body_text += f"- Successful: {successful}\n"
        body_text += f"- Failed: {failed}\n\n"
        
        if failed > 0:
            body_text += "Failed emails:\n"
            for result in results:
                if not result.success:
                    body_text += f"- {result.recipient}: {result.error}\n"
        
        # Build HTML version
        body_html = f"""
        <html>
        <body>
            <h2>Email Send Report</h2>
            <p>{message}</p>
            <h3>Summary</h3>
            <ul>
                <li>Total: {len(results)}</li>
                <li>Successful: {successful}</li>
                <li>Failed: {failed}</li>
            </ul>
        """
        
        if failed > 0:
            body_html += "<h3>Failed Emails</h3><ul>"
            for result in results:
                if not result.success:
                    body_html += f"<li>{result.recipient}: {result.error}</li>"
            body_html += "</ul>"
        
        body_html += "</body></html>"
        
        try:
            # Send notification
            notification_results = await EmailService.send_email(
                recipients=[recipient],
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                from_name="Email Service"
            )
            
            return notification_results[0].success if notification_results else False
            
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            return False