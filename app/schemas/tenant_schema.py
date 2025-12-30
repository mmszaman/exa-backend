from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Tenant(BaseModel):
    """Response model for tenant/organization data."""
    id: int
    clerk_org_id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    brand: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True
    plan: str = "free"
    max_users: int = 5
    max_projects: int = 3
    stripe_customer_id: Optional[str] = None
    billing_email: Optional[str] = None
    settings: Optional[dict] = None
    features: Optional[dict] = None
    metadata: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TenantCreate(BaseModel):
    """Model for creating a tenant."""
    clerk_org_id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    brand: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    plan: str = "free"
    metadata: Optional[str] = None


class TenantUpdate(BaseModel):
    """Model for updating a tenant."""
    name: Optional[str] = None
    logo_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None
    plan: Optional[str] = None
    max_users: Optional[int] = None
    max_projects: Optional[int] = None
    billing_email: Optional[str] = None
    settings: Optional[dict] = None
    features: Optional[dict] = None
    metadata: Optional[str] = None
