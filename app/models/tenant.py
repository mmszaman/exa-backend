from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class TenantModel(Base):
    __tablename__ = "tenants"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)
    
    # Organization Information
    name = Column(String(255), index=True, nullable=False)
    legal_name = Column(String(255), index=True, nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    logo_url = Column(String(500), nullable=True)
    tax_id = Column(String(50), nullable=True)
    type = Column(String(50), nullable=True, index=True)
    team_size = Column(BigInteger, nullable=True)
    
    # Contact Information
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="active", index=True)
    
    # Settings & Preferences
    settings = Column(JSONB, nullable=True)
    features = Column(JSONB, nullable=True)
    
    # Metadata
    clerk_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    businesses = relationship("BusinessModel", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("RoleModel", back_populates="tenant", cascade="all, delete-orphan")
    teams = relationship("TeamModel", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="tenant", cascade="all, delete-orphan")
    
    # Composite Indexes
    __table_args__ = (
        Index('idx_type_status', 'type', 'status'),
    )
