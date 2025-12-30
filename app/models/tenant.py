from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class TenantModel(Base):
    __tablename__ = "tenants"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Organization Information
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    
    # Branding & Identity
    logo_url = Column(String(500), nullable=True)
    brand = Column(String(100), index=True, nullable=True)  # addvive, exakeep, smbhub, etc.
    
    # Contact Information
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Status & Plan
    is_active = Column(Boolean, default=True, index=True)
    plan = Column(String(50), default="free", index=True)  # free, starter, pro, enterprise
    max_users = Column(Integer, default=5)
    max_projects = Column(Integer, default=3)
    
    # Billing (for future integration)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    billing_email = Column(String(255), nullable=True)
    
    # Settings & Preferences
    settings = Column(JSON, nullable=True)  # Store organization settings as JSON
    features = Column(JSON, nullable=True)  # Feature flags
    
    # Metadata
    clerk_metadata = Column(Text, nullable=True)  # Additional JSON data from Clerk
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Composite Indexes
    __table_args__ = (
        Index('idx_brand_active', 'brand', 'is_active'),
        Index('idx_plan_active', 'plan', 'is_active'),
    )
