from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class Address(BaseModel):
    """Address schema for business location."""
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, alias="zipCode", max_length=20)
    country: Optional[str] = Field(default="USA", max_length=100)
    
    @field_validator('street', 'city', 'state', 'zip_code', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None."""
        if isinstance(v, str) and v.strip() == '':
            return None
        return v.strip() if isinstance(v, str) else v
    
    @model_validator(mode='after')
    def validate_address(self):
        """Validate that if address is provided, required fields are present."""
        if not self.street or not self.city or not self.state or not self.zip_code:
            return None
        return self
    
    class Config:
        populate_by_name = True


class BusinessBase(BaseModel):
    """Base model for business data."""
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, alias="legalName", max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    status: str = Field(default="active", max_length=50)
    tax_id: Optional[str] = Field(None, alias="taxId", max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[Address] = None
    logo_url: Optional[str] = Field(None, alias="logoUrl", max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, alias="employeeCount", ge=0)
    founded_year: Optional[int] = Field(None, alias="foundedYear")
    
    @field_validator('legal_name', 'email', 'phone', 'website', 'description', 'industry', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None for optional fields."""
        if isinstance(v, str) and v.strip() == '':
            return None
        return v
    
    @field_validator('founded_year')
    @classmethod
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                raise ValueError(f'Founded year must be between 1800 and {current_year}')
        return v
    
    @field_validator('name')
    @classmethod
    def trim_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
    class Config:
        populate_by_name = True


class Business(BaseModel):
    """Response model for business data."""
    id: int
    public_id: UUID = Field(..., alias="publicId")
    tenant_id: int = Field(..., alias="tenantId")
    owner_user_id: Optional[int] = Field(None, alias="ownerUserId")
    name: str
    legal_name: Optional[str] = Field(None, alias="legalName")
    type: Optional[str] = None
    status: str
    tax_id: Optional[str] = Field(None, alias="taxId")
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[Address] = None
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    description: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = Field(None, alias="employeeCount")
    founded_year: Optional[int] = Field(None, alias="foundedYear")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    deleted_at: Optional[datetime] = Field(None, alias="deletedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            UUID: str  # Convert UUID to string in JSON response
        }


class BusinessCreate(BusinessBase):
    """Model for creating a business."""
    pass


class BusinessUpdate(BaseModel):
    """Model for updating a business."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, alias="legalName", min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, alias="taxId", max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[Address] = None
    logo_url: Optional[str] = Field(None, alias="logoUrl", max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, alias="employeeCount", ge=0)
    founded_year: Optional[int] = Field(None, alias="foundedYear")
    
    @field_validator('founded_year')
    @classmethod
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                raise ValueError(f'Founded year must be between 1800 and {current_year}')
        return v
    
    @field_validator('name', 'legal_name')
    @classmethod
    def trim_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
    class Config:
        populate_by_name = True


class BusinessListResponse(BaseModel):
    """Response model for paginated business list."""
    data: list[Business]
    total: int
    page: int
    limit: int
    total_pages: int = Field(..., alias="totalPages")
    
    class Config:
        populate_by_name = True
