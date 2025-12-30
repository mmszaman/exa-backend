from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserModel(Base):
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Clerk Integration
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Multi-tenancy
    tenant_id = Column(String(255), index=True, nullable=True)  # Clerk organization ID
    
    # Basic Information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone_number = Column(String(50), nullable=True)
    
    # Status & Role
    is_active = Column(Boolean, default=True, index=True)
    role = Column(String(50), default="member", index=True)  # admin, member, viewer, etc.
    
    # Marketing & Analytics
    lead_source = Column(String(100), index=True, nullable=True)  # google, facebook, referral, direct, etc.
    brand = Column(String(100), index=True, nullable=True)  # addvive, exakeep, smbhub, etc.
    referral_code = Column(String(50), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Preferences
    newsletter = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    
    # Additional Metadata (JSON stored as text)
    clerk_metadata = Column(Text, nullable=True)  # Store additional JSON data from Clerk
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    
    # Composite Indexes for common queries
    __table_args__ = (
        Index('idx_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_tenant_role', 'tenant_id', 'role'),
        Index('idx_brand_source', 'brand', 'lead_source'),
    )
    
    # Note: Authentication is handled by Clerk
    # Password, verification, and OTP fields removed
