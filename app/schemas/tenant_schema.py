from pydantic import BaseModel, Field, field_serializer, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

# Tenant Schemas
# Tenant properties when retrieved from the system
class Tenant(BaseModel):
    id: int
    public_id: UUID = Field(..., alias="publicId")
    clerk_org_id: Optional[str] = Field(None, alias="clerkOrgId")
    name: str
    slug: Optional[str] = None
    status: str
    suspension_reason: Optional[str] = Field(None, alias="suspensionReason")
    suspended_at: Optional[datetime] = Field(None, alias="suspendedAt")
    deactivated_at: Optional[datetime] = Field(None, alias="deactivatedAt")
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

# Input model for creating or updating a tenant
class TenantInput(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default="active")
    suspension_reason: Optional[str] = Field(default=None, alias="suspensionReason")
    
    @field_validator('slug', 'suspension_reason', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional string fields."""
        if v == "" or v is None:
            return None
        return v
    
    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True
    }

# Tenant list response model
class TenantListResponse(BaseModel):
    tenants: list[Tenant]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    
    class Config:
        populate_by_name = True

