"""add_businesses_table

Revision ID: 3650f8c219e2
Revises: bae947ba425b
Create Date: 2026-01-04 14:41:30.525558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3650f8c219e2'
down_revision: Union[str, Sequence[str], None] = 'bae947ba425b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create businesses table
    op.create_table('businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('llc', 'corporation', 'partnership', 'sole_proprietorship', 'nonprofit', 'other', name='businesstype'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'pending', 'suspended', name='businessstatus'), nullable=False),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('address', sa.JSON(), nullable=False),
        sa.Column('logo', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_businesses_id'), 'businesses', ['id'], unique=False)
    op.create_index(op.f('ix_businesses_tenant_id'), 'businesses', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_businesses_name'), 'businesses', ['name'], unique=False)
    op.create_index(op.f('ix_businesses_type'), 'businesses', ['type'], unique=False)
    op.create_index(op.f('ix_businesses_status'), 'businesses', ['status'], unique=False)
    op.create_index(op.f('ix_businesses_email'), 'businesses', ['email'], unique=False)
    op.create_index(op.f('ix_businesses_created_at'), 'businesses', ['created_at'], unique=False)
    
    # Create composite indexes
    op.create_index('idx_tenant_status', 'businesses', ['tenant_id', 'status'], unique=False)
    op.create_index('idx_tenant_type', 'businesses', ['tenant_id', 'type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_tenant_type', table_name='businesses')
    op.drop_index('idx_tenant_status', table_name='businesses')
    op.drop_index(op.f('ix_businesses_created_at'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_email'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_status'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_type'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_name'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_tenant_id'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_id'), table_name='businesses')
    
    # Drop foreign key constraint
    op.drop_constraint('businesses_tenant_id_fkey', 'businesses', type_='foreignkey')
    
    # Drop table
    op.drop_table('businesses')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS businesstype')
    op.execute('DROP TYPE IF EXISTS businessstatus')
