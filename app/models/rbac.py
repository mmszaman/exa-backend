"""
RBAC (Role-Based Access Control) Models

Multi-tenant RBAC with support for:
- Global permissions catalog
- Tenant-scoped roles (system + custom)
- Role-permission mappings with conditions
- Member role assignments
- Member permission overrides
- Teams for organizational hierarchy
- Resource-level grants (object-level access)
"""
import enum
from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey,
    Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


# ================== Enums ==================

class EffectType(str, enum.Enum):
    """Permission effect enumeration."""
    ALLOW = "allow"
    DENY = "deny"


class SubjectType(str, enum.Enum):
    """Resource grant subject type."""
    MEMBERSHIP = "membership"
    TEAM = "team"


class AccessLevel(str, enum.Enum):
    """Resource access level enumeration."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    FULL = "full"


# ================== 1) Permissions ==================

class PermissionModel(Base):
    """
    Global catalog of permissions.
    This is a stable, small table that defines all available permissions.
    """
    __tablename__ = "permissions"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Permission Identity
    key = Column(String(150), unique=True, nullable=False, index=True)  # e.g., "contacts.read"
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Permission Categorization
    resource = Column(String(100), nullable=False, index=True)  # e.g., "contacts", "billing"
    action = Column(String(50), nullable=False, index=True)      # e.g., "read", "write", "delete"

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    role_permissions = relationship("RolePermissionModel", back_populates="permission", cascade="all, delete-orphan")
    member_overrides = relationship("MemberPermissionOverrideModel", back_populates="permission", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_permission_resource_action', 'resource', 'action'),
        Index('idx_permission_active', 'is_active'),
    )


# ================== 2) Roles ==================

class RoleModel(Base):
    """
    Tenant-scoped roles supporting both system and custom roles.
    System roles are predefined (owner, admin, member, viewer).
    Custom roles can be created per tenant.
    """
    __tablename__ = "roles"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Role Identity
    key = Column(String(100), nullable=False)  # e.g., "owner", "custom:ops_manager"
    name = Column(String(150), nullable=False)
    description = Column(Text)

    # Role Type & Status
    is_system = Column(Boolean, default=False, nullable=False)  # True for built-in roles
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), index=True)

    # Relationships
    tenant = relationship("TenantModel", back_populates="roles")
    role_permissions = relationship("RolePermissionModel", back_populates="role", cascade="all, delete-orphan")
    member_roles = relationship("MemberRoleModel", back_populates="role", cascade="all, delete-orphan")
    team_roles = relationship("TeamRoleModel", back_populates="role", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'key', name='uq_tenant_role_key'),
        Index('idx_role_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_role_system', 'is_system'),
        Index('idx_role_deleted', 'deleted_at'),
    )


# ================== 3) Role Permissions ==================

class RolePermissionModel(Base):
    """
    Many-to-many mapping between roles and permissions.
    Supports ABAC-like conditions for fine-grained access control.
    """
    __tablename__ = "role_permissions"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)

    # Relationships
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Access Control
    effect = Column(String(10), nullable=False, default="allow")  # "allow" | "deny"
    conditions = Column(JSONB)  # Optional ABAC conditions

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    role = relationship("RoleModel", back_populates="role_permissions")
    permission = relationship("PermissionModel", back_populates="role_permissions")

    # Constraints
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
        CheckConstraint("effect IN ('allow', 'deny')", name='check_effect_valid'),
        Index('idx_role_permission_effect', 'role_id', 'effect'),
    )


# ================== 4) Member Role Assignments ==================

class MemberRoleModel(Base):
    """
    Assigns roles to tenant members (memberships).
    Supports multiple roles per member and tracks assignment/revocation.
    """
    __tablename__ = "member_roles"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(BigInteger, ForeignKey("memberships.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Assignment Tracking
    assigned_by_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel")
    membership = relationship("MembershipModel", back_populates="member_roles")
    role = relationship("RoleModel", back_populates="member_roles")
    assigned_by = relationship("UserModel", foreign_keys=[assigned_by_user_id])

    # Constraints
    __table_args__ = (
        UniqueConstraint('membership_id', 'role_id', name='uq_member_role'),
        Index('idx_member_role_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_member_role_membership', 'membership_id', 'is_active'),
        Index('idx_member_role_revoked', 'revoked_at'),
    )


# ================== 5) Member Permission Overrides ==================

class MemberPermissionOverrideModel(Base):
    """
    Per-member permission overrides.
    Allows granting/denying specific permissions without creating new roles.
    """
    __tablename__ = "member_permission_overrides"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(BigInteger, ForeignKey("memberships.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Access Control
    effect = Column(String(10), nullable=False)  # "allow" | "deny"
    conditions = Column(JSONB)  # Optional ABAC conditions

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), index=True)

    # Relationships
    tenant = relationship("TenantModel")
    membership = relationship("MembershipModel", back_populates="permission_overrides")
    permission = relationship("PermissionModel", back_populates="member_overrides")

    # Constraints
    __table_args__ = (
        UniqueConstraint('membership_id', 'permission_id', name='uq_member_permission_override'),
        CheckConstraint("effect IN ('allow', 'deny')", name='check_override_effect_valid'),
        Index('idx_member_override_tenant', 'tenant_id', 'deleted_at'),
        Index('idx_member_override_membership', 'membership_id', 'deleted_at'),
    )


# ================== 6) Teams ==================

class TeamModel(Base):
    """
    Optional organizational grouping layer.
    Supports departments, squads, or any hierarchical structure.
    """
    __tablename__ = "teams"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Team Identity
    name = Column(String(150), nullable=False)
    slug = Column(String(160), nullable=False)
    description = Column(Text)

    # Creation Tracking
    created_by_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), index=True)

    # Relationships
    tenant = relationship("TenantModel", back_populates="teams")
    created_by = relationship("UserModel", foreign_keys=[created_by_user_id])
    team_members = relationship("TeamMemberModel", back_populates="team", cascade="all, delete-orphan")
    team_roles = relationship("TeamRoleModel", back_populates="team", cascade="all, delete-orphan")
    resource_grants = relationship("ResourceGrantModel", 
                                   foreign_keys="ResourceGrantModel.subject_id",
                                   primaryjoin="and_(TeamModel.id==foreign(ResourceGrantModel.subject_id), ResourceGrantModel.subject_type=='team')",
                                   cascade="all, delete-orphan",
                                   viewonly=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'slug', name='uq_tenant_team_slug'),
        Index('idx_team_tenant_deleted', 'tenant_id', 'deleted_at'),
    )


# ================== 7) Team Members ==================

class TeamMemberModel(Base):
    """
    Membership in teams.
    Links memberships to teams with join/leave tracking.
    """
    __tablename__ = "team_members"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(BigInteger, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(BigInteger, ForeignKey("memberships.id", ondelete="CASCADE"), nullable=False, index=True)

    # Status & Tracking
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    left_at = Column(DateTime(timezone=True))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("TenantModel")
    team = relationship("TeamModel", back_populates="team_members")
    membership = relationship("MembershipModel", back_populates="team_memberships")

    # Constraints
    __table_args__ = (
        UniqueConstraint('team_id', 'membership_id', name='uq_team_member'),
        Index('idx_team_member_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_team_member_team_active', 'team_id', 'is_active'),
        Index('idx_team_member_membership', 'membership_id', 'is_active'),
    )


# ================== 8) Team Role Assignments ==================

class TeamRoleModel(Base):
    """
    Assigns roles at team scope.
    Members inherit team roles for simplified permission management.
    """
    __tablename__ = "team_roles"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(BigInteger, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Assignment Tracking
    assigned_by_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("TenantModel")
    team = relationship("TeamModel", back_populates="team_roles")
    role = relationship("RoleModel", back_populates="team_roles")
    assigned_by = relationship("UserModel", foreign_keys=[assigned_by_user_id])

    # Constraints
    __table_args__ = (
        UniqueConstraint('team_id', 'role_id', name='uq_team_role'),
        Index('idx_team_role_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_team_role_team_active', 'team_id', 'is_active'),
        Index('idx_team_role_revoked', 'revoked_at'),
    )


# ================== 9) Resource Grants ==================

class ResourceGrantModel(Base):
    """
    Object-level access control (row-level permissions).
    Grants specific members or teams access to individual resources.
    Avoids per-row ACL table explosion by using a polymorphic approach.
    """
    __tablename__ = "resource_grants"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Subject (who gets access)
    subject_type = Column(String(20), nullable=False)  # "membership" | "team"
    subject_id = Column(BigInteger, nullable=False)     # memberships.id or teams.id

    # Resource (what they access)
    resource_type = Column(String(50), nullable=False)  # e.g., "business", "project", "contact"
    resource_id = Column(UUID(as_uuid=True), nullable=False)  # public_id of resource

    # Access Level
    access_level = Column(String(30), nullable=False)   # "read", "write", "admin", "full"
    conditions = Column(JSONB)  # Optional conditions for access

    # Tracking
    created_by_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), index=True)

    # Relationships
    tenant = relationship("TenantModel")
    created_by = relationship("UserModel", foreign_keys=[created_by_user_id])

    # Constraints
    __table_args__ = (
        CheckConstraint("subject_type IN ('membership', 'team')", name='check_subject_type_valid'),
        Index('idx_resource_grant_tenant_deleted', 'tenant_id', 'deleted_at'),
        Index('idx_resource_grant_subject', 'subject_type', 'subject_id', 'deleted_at'),
        Index('idx_resource_grant_resource', 'resource_type', 'resource_id', 'deleted_at'),
        Index('idx_resource_grant_lookup', 'tenant_id', 'subject_type', 'subject_id', 'resource_type'),
    )
