"""
Email schemas - Data validation for email operations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


class EmailRecipient(BaseModel):
    """Single email recipient with validation."""
    
    email: EmailStr  # Validates email format automatically
    name: Optional[str] = None  # Optional recipient name
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }


class SendEmailRequest(BaseModel):
    """Request schema for sending emails. All fields required except HTML body."""
    
    recipients: List[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of email addresses to send to"
    )
    
    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Email subject line"
    )

    from_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sender display name"
    )
    
    from_email: EmailStr = Field(
        ...,
        description="Sender email address"
    )
    
    body_text: str = Field(
        ...,
        min_length=1,
        description="Plain text email body (required)"
    )
    
    body_html: Optional[str] = Field(
        None,
        description="HTML email body (optional, falls back to text)"
    )
    
    
    @field_validator('recipients')
    @classmethod
    def validate_recipients(cls, v):
        """Ensure recipients list is not empty and has no duplicates."""
        if not v:
            raise ValueError('At least one recipient is required')
        
        # Remove duplicates while preserving order
        unique_emails = list(dict.fromkeys(v))
        if len(unique_emails) != len(v):
            # Return deduplicated list
            return unique_emails
        return v
    
    @field_validator('subject', 'body_text')
    @classmethod
    def strip_whitespace(cls, v):
        """Remove leading/trailing whitespace."""
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["user1@example.com", "user2@example.com"],
                "subject": "Welcome to our platform",
                "from_name": "Exa Team",
                "from_email": "support@exateks.com",
                "body_text": "Hello! Welcome to our platform. We're glad to have you.",
                "body_html": "<h1>Hello!</h1><p>Welcome to our platform. We're glad to have you.</p>"
            }
        }


class EmailSendResult(BaseModel):
    """Result of a single email send attempt."""
    
    recipient: EmailStr
    success: bool
    error: Optional[str] = None
    sent_at: Optional[str] = None  # ISO format timestamp
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "user@example.com",
                "success": True,
                "error": None,
                "sent_at": "2025-11-28T14:30:15Z"
            }
        }


class SendTemplateEmailRequest(BaseModel):
    """Request schema for sending template-based emails. All top-level fields required except context which may be empty."""
    
    recipients: List[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Recipient email addresses"
    )

    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Email subject line"
    )
    
    from_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sender display name"
    )
    
    from_email: EmailStr = Field(
        ...,
        description="Sender email address"
    )
    
    template_name: str = Field(
        ...,
        min_length=1,
        description="Name of template to use (welcome, password_reset, email_verification, user_notification)"
    )
    
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables (user_name, verify_url, reset_url, etc.)"
    )
    
    @field_validator('recipients')
    @classmethod
    def validate_recipients(cls, v):
        """Ensure recipients list is not empty and has no duplicates."""
        if not v:
            raise ValueError('At least one recipient is required')
        
        # Remove duplicates while preserving order
        unique_emails = list(dict.fromkeys(v))
        if len(unique_emails) != len(v):
            return unique_emails
        return v
    
    @field_validator('template_name')
    @classmethod
    def validate_template_name(cls, v):
        """Validate template name is one of the allowed templates."""
        allowed_templates = ['welcome', 'password_reset', 'email_verification', 'user_notification', 'admin_notification']
        template_name = v.strip().lower()
        
        if template_name not in allowed_templates:
            raise ValueError(
                f"Invalid template name '{v}'. Must be one of: {', '.join(allowed_templates)}"
            )
        
        return template_name
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["user@example.com"],
                "subject": "Welcome to Exateks!",
                "from_name": "Exateks Team",
                "from_email": "support@exateks.com",
                "template_name": "welcome",
                "context": {
                    "user_name": "John Doe",
                    "verify_url": "https://example.com/verify/abc123",
                    "company_name": "Exateks"
                }
            }
        }


class SendEmailResponse(BaseModel):
    """Response schema for email sending operation."""
    
    success: bool
    total_sent: int
    total_failed: int
    results: List[EmailSendResult]
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_sent": 2,
                "total_failed": 0,
                "message": "Successfully sent email to all 2 recipient(s)",
                "results": [
                    {
                        "recipient": "user1@example.com",
                        "success": True,
                        "error": None,
                        "sent_at": "2025-11-28T14:30:15Z"
                    },
                    {
                        "recipient": "user2@example.com",
                        "success": True,
                        "error": None,
                        "sent_at": "2025-11-28T14:30:16Z"
                    }
                ]
            }
        }



