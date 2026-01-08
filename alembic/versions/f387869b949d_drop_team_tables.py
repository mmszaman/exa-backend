"""drop_team_tables

Revision ID: f387869b949d
Revises: a607aeb66854
Create Date: 2026-01-08 07:59:38.584722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f387869b949d'
down_revision: Union[str, Sequence[str], None] = 'a607aeb66854'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop team tables if they exist (use raw SQL for IF EXISTS)
    op.execute('DROP TABLE IF EXISTS team_roles CASCADE')
    op.execute('DROP TABLE IF EXISTS team_members CASCADE')
    op.execute('DROP TABLE IF EXISTS teams CASCADE')
    
    # Update resource_grants check constraint to remove 'team' option
    op.drop_constraint('check_subject_type_valid', 'resource_grants', type_='check')
    op.create_check_constraint(
        'check_subject_type_valid',
        'resource_grants',
        "subject_type IN ('membership')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Update resource_grants check constraint to add 'team' back
    op.drop_constraint('check_subject_type_valid', 'resource_grants', type_='check')
    op.create_check_constraint(
        'check_subject_type_valid',
        'resource_grants',
        "subject_type IN ('membership', 'team')"
    )
    
    # Recreate teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('slug', sa.String(length=160), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'slug', name='uq_tenant_team_slug')
    )
    op.create_index('idx_team_tenant_deleted', 'teams', ['tenant_id', 'deleted_at'])
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'])
    op.create_index(op.f('ix_teams_public_id'), 'teams', ['public_id'], unique=True)
    op.create_index(op.f('ix_teams_tenant_id'), 'teams', ['tenant_id'])
    
    # Recreate team_members table
    op.create_table(
        'team_members',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('team_id', sa.BigInteger(), nullable=False),
        sa.Column('membership_id', sa.BigInteger(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['membership_id'], ['memberships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'membership_id', name='uq_team_member')
    )
    op.create_index('idx_team_member_membership', 'team_members', ['membership_id', 'is_active'])
    op.create_index('idx_team_member_team_active', 'team_members', ['team_id', 'is_active'])
    op.create_index('idx_team_member_tenant_active', 'team_members', ['tenant_id', 'is_active'])
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'])
    op.create_index(op.f('ix_team_members_membership_id'), 'team_members', ['membership_id'])
    op.create_index(op.f('ix_team_members_team_id'), 'team_members', ['team_id'])
    op.create_index(op.f('ix_team_members_tenant_id'), 'team_members', ['tenant_id'])
    
    # Recreate team_roles table
    op.create_table(
        'team_roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('team_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('assigned_by_user_id', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'role_id', name='uq_team_role')
    )
    op.create_index('idx_team_role_revoked', 'team_roles', ['revoked_at'])
    op.create_index('idx_team_role_team_active', 'team_roles', ['team_id', 'is_active'])
    op.create_index('idx_team_role_tenant_active', 'team_roles', ['tenant_id', 'is_active'])
    op.create_index(op.f('ix_team_roles_id'), 'team_roles', ['id'])
    op.create_index(op.f('ix_team_roles_public_id'), 'team_roles', ['public_id'], unique=True)
    op.create_index(op.f('ix_team_roles_role_id'), 'team_roles', ['role_id'])
    op.create_index(op.f('ix_team_roles_team_id'), 'team_roles', ['team_id'])
    op.create_index(op.f('ix_team_roles_tenant_id'), 'team_roles', ['tenant_id'])

