from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class UserModel(Base):
    __tablename__ = "users"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)
    
    # Clerk Integration
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Basic Information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone_number = Column(String(50), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Marketing & Analytics
    lead_source = Column(String(100), index=True, nullable=True)
    brand = Column(String(100), index=True, nullable=True)
    referral_code = Column(String(50), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Preferences
    newsletter = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    
    # Additional Metadata
    clerk_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="user", cascade="all, delete-orphan")
    
    # Composite Indexes for common queries
    __table_args__ = (
        Index('idx_brand_source', 'brand', 'lead_source'),
    )
