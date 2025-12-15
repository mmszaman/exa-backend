
import asyncio
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import List, Optional, Tuple
import aiosmtplib
from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.email_schema import EmailSendResult

# Get logger for this service
logger = get_logger('email_service')


class EmailService:
    """
    Service for sending emails via SMTP.
    Handles connection, composition, and batch sending.
    """
    
    # Static method to create email message
    # Input: to_email, subject, from_name, from_email, body_text, body_html (optional)
    # Output: EmailMessage
    @staticmethod
    def _create_email_message(
        to_email: str,
        subject: str,
        from_name: str,
        from_email: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> EmailMessage:
        """
        Create an email message with text and optional HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            from_email: Sender email
            from_name: Sender name
            body_text: Plain text body
            body_html: Optional HTML body
            
        Returns:
            EmailMessage: Configured email message
        """
        msg = EmailMessage()
        
        # Set headers
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        
        # Set plain text content
        msg.set_content(body_text)
        
        # Add HTML alternative if provided
        if body_html:
            msg.add_alternative(body_html, subtype='html')
        
        logger.debug(f"Created email message for {to_email}: {subject}")
        return msg
    
    # Static method to send a single email
    # Input: smtp connection, message, recipient
    # Output: EmailSendResult
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
    
    # Public method to send email to multiple recipients
    # Input: recipients list, subject, body_text, body_html (optional), from_name (optional), from_email (optional)
    # Output: List of EmailSendResult
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
                    from_name=from_name,
                    from_email=from_email,
                    body_text=body_text,
                    body_html=body_html
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