"""remove_subscription_fields_from_tenants

Revision ID: cf058fa7d0de
Revises: c83decc00fdb
Create Date: 2026-01-04 15:57:01.058960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf058fa7d0de'
down_revision: Union[str, Sequence[str], None] = 'c83decc00fdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop unique constraint on stripe_customer_id before dropping column
    op.drop_constraint('tenants_stripe_customer_id_key', 'tenants', type_='unique')
    
    # Drop subscription-related columns from tenants table
    op.drop_column('tenants', 'stripe_customer_id')
    op.drop_column('tenants', 'billing_email')
    op.drop_column('tenants', 'trial_ends_at')
    op.drop_column('tenants', 'subscription_ends_at')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back subscription-related columns to tenants table
    op.add_column('tenants', sa.Column('subscription_ends_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tenants', sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tenants', sa.Column('billing_email', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    
    # Recreate unique constraint on stripe_customer_id
    op.create_unique_constraint('tenants_stripe_customer_id_key', 'tenants', ['stripe_customer_id'])
