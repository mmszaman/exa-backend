import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class EmailSignupRequest(BaseModel):
    """Request to start signup process with email only."""
    email: EmailStr
    newsletter: bool = False

class EmailSignupResponse(BaseModel):
    """Response after email signup request."""
    message: str
    email: str

class VerifySignupTokenResponse(BaseModel):
    """Response after email verification."""
    message: str
    email: str
    verification_token: str
    is_verified: bool
    token_expiry: datetime.datetime

class ResendVerificationRequest(BaseModel):
    """Request to resend verification email."""
    email: EmailStr
