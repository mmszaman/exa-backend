"""add_clerk_org_id_to_tenants

Revision ID: c83decc00fdb
Revises: 3650f8c219e2
Create Date: 2026-01-04 14:56:18.967246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c83decc00fdb'
down_revision: Union[str, Sequence[str], None] = '3650f8c219e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add clerk_org_id column to tenants table
    # Note: This allows NULL initially for existing records
    op.add_column('tenants', sa.Column('clerk_org_id', sa.String(length=255), nullable=True))
    
    # Create unique index on clerk_org_id
    op.create_index(op.f('ix_tenants_clerk_org_id'), 'tenants', ['clerk_org_id'], unique=True)
    
    # After data migration, you can make it NOT NULL:
    # op.alter_column('tenants', 'clerk_org_id', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index(op.f('ix_tenants_clerk_org_id'), table_name='tenants')
    
    # Drop column
    op.drop_column('tenants', 'clerk_org_id')
