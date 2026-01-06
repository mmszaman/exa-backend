"""add_rbac_models

Revision ID: aa9c09f95d55
Revises: 4e27efd6c84b
Create Date: 2026-01-04 16:52:59.877966

Adds comprehensive RBAC system:
- Permissions catalog
- Tenant-scoped roles
- Role-permission mappings
- Member role assignments
- Member permission overrides
- Teams for organizational hierarchy
- Team members and team roles
- Resource grants for object-level access
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = 'aa9c09f95d55'
down_revision: Union[str, Sequence[str], None] = '4e27efd6c84b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add RBAC models."""
    
    # 1) Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('key', sa.String(150), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_permissions_id', 'permissions', ['id'])
    op.create_index('ix_permissions_public_id', 'permissions', ['public_id'], unique=True)
    op.create_index('ix_permissions_key', 'permissions', ['key'], unique=True)
    op.create_index('ix_permissions_resource', 'permissions', ['resource'])
    op.create_index('ix_permissions_action', 'permissions', ['action'])
    op.create_index('ix_permissions_active', 'permissions', ['is_active'])
    op.create_index('idx_permission_resource_action', 'permissions', ['resource', 'action'])
    
    # 2) Create roles table
    op.create_table('roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_system', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'key', name='uq_tenant_role_key')
    )
    op.create_index('ix_roles_id', 'roles', ['id'])
    op.create_index('ix_roles_public_id', 'roles', ['public_id'], unique=True)
    op.create_index('ix_roles_tenant_id', 'roles', ['tenant_id'])
    op.create_index('ix_roles_deleted_at', 'roles', ['deleted_at'])
    op.create_index('idx_role_tenant_active', 'roles', ['tenant_id', 'is_active'])
    op.create_index('idx_role_system', 'roles', ['is_system'])
    op.create_index('idx_role_deleted', 'roles', ['deleted_at'])
    
    # 3) Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.Column('effect', sa.String(10), nullable=False, server_default='allow'),
        sa.Column('conditions', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
        sa.CheckConstraint("effect IN ('allow', 'deny')", name='check_effect_valid')
    )
    op.create_index('ix_role_permissions_id', 'role_permissions', ['id'])
    op.create_index('ix_role_permissions_role_id', 'role_permissions', ['role_id'])
    op.create_index('ix_role_permissions_permission_id', 'role_permissions', ['permission_id'])
    op.create_index('idx_role_permission_effect', 'role_permissions', ['role_id', 'effect'])
    
    # 4) Create member_roles table
    op.create_table('member_roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('membership_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('assigned_by_user_id', sa.BigInteger()),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['memberships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('membership_id', 'role_id', name='uq_member_role')
    )
    op.create_index('ix_member_roles_id', 'member_roles', ['id'])
    op.create_index('ix_member_roles_public_id', 'member_roles', ['public_id'], unique=True)
    op.create_index('ix_member_roles_tenant_id', 'member_roles', ['tenant_id'])
    op.create_index('ix_member_roles_membership_id', 'member_roles', ['membership_id'])
    op.create_index('ix_member_roles_role_id', 'member_roles', ['role_id'])
    op.create_index('idx_member_role_tenant_active', 'member_roles', ['tenant_id', 'is_active'])
    op.create_index('idx_member_role_membership', 'member_roles', ['membership_id', 'is_active'])
    op.create_index('idx_member_role_revoked', 'member_roles', ['revoked_at'])
    
    # 5) Create member_permission_overrides table
    op.create_table('member_permission_overrides',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('membership_id', sa.BigInteger(), nullable=False),
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.Column('effect', sa.String(10), nullable=False),
        sa.Column('conditions', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['memberships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('membership_id', 'permission_id', name='uq_member_permission_override'),
        sa.CheckConstraint("effect IN ('allow', 'deny')", name='check_override_effect_valid')
    )
    op.create_index('ix_member_permission_overrides_id', 'member_permission_overrides', ['id'])
    op.create_index('ix_member_permission_overrides_public_id', 'member_permission_overrides', ['public_id'], unique=True)
    op.create_index('ix_member_permission_overrides_tenant_id', 'member_permission_overrides', ['tenant_id'])
    op.create_index('ix_member_permission_overrides_membership_id', 'member_permission_overrides', ['membership_id'])
    op.create_index('ix_member_permission_overrides_permission_id', 'member_permission_overrides', ['permission_id'])
    op.create_index('ix_member_permission_overrides_deleted_at', 'member_permission_overrides', ['deleted_at'])
    op.create_index('idx_member_override_tenant', 'member_permission_overrides', ['tenant_id', 'deleted_at'])
    op.create_index('idx_member_override_membership', 'member_permission_overrides', ['membership_id', 'deleted_at'])
    
    # 6) Create teams table
    op.create_table('teams',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('slug', sa.String(160), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_by_user_id', sa.BigInteger()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'slug', name='uq_tenant_team_slug')
    )
    op.create_index('ix_teams_id', 'teams', ['id'])
    op.create_index('ix_teams_public_id', 'teams', ['public_id'], unique=True)
    op.create_index('ix_teams_tenant_id', 'teams', ['tenant_id'])
    op.create_index('ix_teams_deleted_at', 'teams', ['deleted_at'])
    op.create_index('idx_team_tenant_deleted', 'teams', ['tenant_id', 'deleted_at'])
    
    # 7) Create team_members table
    op.create_table('team_members',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('team_id', sa.BigInteger(), nullable=False),
        sa.Column('membership_id', sa.BigInteger(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['memberships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'membership_id', name='uq_team_member')
    )
    op.create_index('ix_team_members_id', 'team_members', ['id'])
    op.create_index('ix_team_members_tenant_id', 'team_members', ['tenant_id'])
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'])
    op.create_index('ix_team_members_membership_id', 'team_members', ['membership_id'])
    op.create_index('idx_team_member_tenant_active', 'team_members', ['tenant_id', 'is_active'])
    op.create_index('idx_team_member_team_active', 'team_members', ['team_id', 'is_active'])
    op.create_index('idx_team_member_membership', 'team_members', ['membership_id', 'is_active'])
    
    # 8) Create team_roles table
    op.create_table('team_roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('team_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('assigned_by_user_id', sa.BigInteger()),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'role_id', name='uq_team_role')
    )
    op.create_index('ix_team_roles_id', 'team_roles', ['id'])
    op.create_index('ix_team_roles_public_id', 'team_roles', ['public_id'], unique=True)
    op.create_index('ix_team_roles_tenant_id', 'team_roles', ['tenant_id'])
    op.create_index('ix_team_roles_team_id', 'team_roles', ['team_id'])
    op.create_index('ix_team_roles_role_id', 'team_roles', ['role_id'])
    op.create_index('idx_team_role_tenant_active', 'team_roles', ['tenant_id', 'is_active'])
    op.create_index('idx_team_role_team_active', 'team_roles', ['team_id', 'is_active'])
    op.create_index('idx_team_role_revoked', 'team_roles', ['revoked_at'])
    
    # 9) Create resource_grants table
    op.create_table('resource_grants',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('subject_type', sa.String(20), nullable=False),
        sa.Column('subject_id', sa.BigInteger(), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', UUID(as_uuid=True), nullable=False),
        sa.Column('access_level', sa.String(30), nullable=False),
        sa.Column('conditions', JSONB),
        sa.Column('created_by_user_id', sa.BigInteger()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("subject_type IN ('membership', 'team')", name='check_subject_type_valid')
    )
    op.create_index('ix_resource_grants_id', 'resource_grants', ['id'])
    op.create_index('ix_resource_grants_public_id', 'resource_grants', ['public_id'], unique=True)
    op.create_index('ix_resource_grants_tenant_id', 'resource_grants', ['tenant_id'])
    op.create_index('ix_resource_grants_deleted_at', 'resource_grants', ['deleted_at'])
    op.create_index('idx_resource_grant_tenant_deleted', 'resource_grants', ['tenant_id', 'deleted_at'])
    op.create_index('idx_resource_grant_subject', 'resource_grants', ['subject_type', 'subject_id', 'deleted_at'])
    op.create_index('idx_resource_grant_resource', 'resource_grants', ['resource_type', 'resource_id', 'deleted_at'])
    op.create_index('idx_resource_grant_lookup', 'resource_grants', ['tenant_id', 'subject_type', 'subject_id', 'resource_type'])


def downgrade() -> None:
    """Downgrade schema - Remove RBAC models."""
    op.drop_table('resource_grants')
    op.drop_table('team_roles')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('member_permission_overrides')
    op.drop_table('member_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
