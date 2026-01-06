from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class BusinessModel(Base):
    __tablename__ = "businesses"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    owner_user_id = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255), nullable=True)
    type = Column(String(50), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    
    # Tax & Legal
    tax_id = Column(String(50), nullable=True)
    
    # Contact Information
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address (stored as JSONB)
    address = Column(JSONB, nullable=True)
    
    # Branding & Identity
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Business Details
    industry = Column(String(100), nullable=True)
    employee_count = Column(BigInteger, nullable=True)
    founded_year = Column(BigInteger, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="businesses")
    owner = relationship("UserModel", backref="owned_businesses")
    
    # Composite Indexes for common queries
    __table_args__ = (
        Index('idx_tenant_status', 'tenant_id', 'status'),
        Index('idx_tenant_type', 'tenant_id', 'type'),
    )
