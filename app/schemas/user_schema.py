
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """Response model for user data."""
    id: int
    clerk_user_id: str
    tenant_id: Optional[str] = None
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    role: str = "member"
    lead_source: Optional[str] = None
    brand: Optional[str] = None
    referral_code: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    newsletter: bool = False
    email_notifications: bool = True
    marketing_emails: bool = False
    metadata: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Model for updating user preferences."""
    newsletter: Optional[bool] = None
    full_name: Optional[str] = None
    email_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    phone_number: Optional[str] = None


class Session(BaseModel):
    """Response model for session data."""
    id: int
    clerk_session_id: str
    user_id: int
    tenant_id: Optional[str] = None
    clerk_user_id: str
    status: str
    client_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    created_at: datetime
    last_active_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    metadata: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """Model for creating a session."""
    clerk_session_id: str
    user_id: int
    clerk_user_id: str
    tenant_id: Optional[str] = None
    status: str = "active"
    client_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[str] = None


class SessionUpdate(BaseModel):
    """Model for updating a session."""
    status: Optional[str] = None
    last_active_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    metadata: Optional[str] = None
