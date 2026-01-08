from sqlalchemy import Column, BigInteger, String, DateTime, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class TenantModel(Base):
    __tablename__ = "tenants"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)
    
    # Clerk Integration
    clerk_org_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Organization Information
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="active", index=True)
    suspension_reason = Column(Text, nullable=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    businesses = relationship("BusinessModel", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("RoleModel", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="tenant", cascade="all, delete-orphan")
    
    # Composite Indexes
    __table_args__ = (
        Index('idx_tenant_status_deleted', 'status', 'deleted_at'),
    )

