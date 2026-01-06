from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class MembershipModel(Base):
    __tablename__ = "memberships"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Membership Details
    role = Column(String(50), nullable=False, default="member", index=True)
    permissions = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_primary = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="tenant_memberships")
    tenant = relationship("TenantModel", backref="members")
    member_roles = relationship("MemberRoleModel", back_populates="membership", cascade="all, delete-orphan")
    permission_overrides = relationship("MemberPermissionOverrideModel", back_populates="membership", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMemberModel", back_populates="membership", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant"),
        Index("ix_memberships_user_tenant_active", "user_id", "tenant_id", "is_active"),
    )
