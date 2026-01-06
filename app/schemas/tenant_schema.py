from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional
from uuid import UUID


class Tenant(BaseModel):
    """Response model for tenant/organization data."""
    id: int
    public_id: UUID = Field(..., alias="publicId")
    name: str
    legal_name: Optional[str] = Field(None, alias="legalName")
    slug: str
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    tax_id: Optional[str] = Field(None, alias="taxId")
    type: Optional[str] = None
    team_size: Optional[int] = Field(None, alias="teamSize")
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    status: str
    settings: Optional[dict] = None
    features: Optional[dict] = None
    clerk_metadata: Optional[dict] = Field(None, alias="clerkMetadata")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    deleted_at: Optional[datetime] = Field(None, alias="deletedAt")
    
    @field_serializer('public_id')
    def serialize_public_id(self, value: UUID) -> str:
        return str(value)
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class TenantCreate(BaseModel):
    """Model for creating a tenant."""
    name: str
    legal_name: Optional[str] = Field(None, alias="legalName")
    slug: str
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    tax_id: Optional[str] = Field(None, alias="taxId")
    type: Optional[str] = None
    team_size: Optional[int] = Field(None, alias="teamSize")
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    status: str = "trial"
    settings: Optional[dict] = None
    features: Optional[dict] = None
    clerk_metadata: Optional[dict] = Field(None, alias="clerkMetadata")
    
    class Config:
        populate_by_name = True


class TenantUpdate(BaseModel):
    """Model for updating a tenant."""
    name: Optional[str] = None
    legal_name: Optional[str] = Field(None, alias="legalName")
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    tax_id: Optional[str] = Field(None, alias="taxId")
    type: Optional[str] = None
    team_size: Optional[int] = Field(None, alias="teamSize")
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    settings: Optional[dict] = None
    features: Optional[dict] = None
    clerk_metadata: Optional[dict] = Field(None, alias="clerkMetadata")
    
    class Config:
        populate_by_name = True


class TenantListResponse(BaseModel):
    """Response model for paginated tenant list."""
    tenants: list[Tenant]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    
    class Config:
        populate_by_name = True
