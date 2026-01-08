"""add_cascade_delete_to_tenant_foreign_keys

Revision ID: 782e1b57ed96
Revises: 13835dab6b8e
Create Date: 2026-01-06 15:46:33.747758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '782e1b57ed96'
down_revision: Union[str, Sequence[str], None] = '13835dab6b8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CASCADE delete to all tenant_id foreign keys."""
    
    # Drop and recreate foreign keys with CASCADE delete
    
    # 1. subscriptions.tenant_id
    op.drop_constraint('subscriptions_tenant_id_fkey', 'subscriptions', type_='foreignkey')
    op.create_foreign_key('subscriptions_tenant_id_fkey', 'subscriptions', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 2. products.tenant_id
    op.drop_constraint('products_tenant_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key('products_tenant_id_fkey', 'products', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 3. billing_profiles.tenant_id
    op.drop_constraint('billing_profiles_tenant_id_fkey', 'billing_profiles', type_='foreignkey')
    op.create_foreign_key('billing_profiles_tenant_id_fkey', 'billing_profiles', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 4. invoices.tenant_id
    op.drop_constraint('invoices_tenant_id_fkey', 'invoices', type_='foreignkey')
    op.create_foreign_key('invoices_tenant_id_fkey', 'invoices', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 5. payments.tenant_id
    op.drop_constraint('payments_tenant_id_fkey', 'payments', type_='foreignkey')
    op.create_foreign_key('payments_tenant_id_fkey', 'payments', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 6. billing_credits.tenant_id
    op.drop_constraint('billing_credits_tenant_id_fkey', 'billing_credits', type_='foreignkey')
    op.create_foreign_key('billing_credits_tenant_id_fkey', 'billing_credits', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 7. usage_records.tenant_id
    op.drop_constraint('usage_records_tenant_id_fkey', 'usage_records', type_='foreignkey')
    op.create_foreign_key('usage_records_tenant_id_fkey', 'usage_records', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # 8. conversations.tenant_id (change from SET NULL to CASCADE)
    op.drop_constraint('conversations_tenant_id_fkey', 'conversations', type_='foreignkey')
    op.create_foreign_key('conversations_tenant_id_fkey', 'conversations', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Remove CASCADE delete from tenant_id foreign keys."""
    
    # Restore original foreign keys without CASCADE (or with SET NULL for conversations)
    
    # 1. subscriptions.tenant_id
    op.drop_constraint('subscriptions_tenant_id_fkey', 'subscriptions', type_='foreignkey')
    op.create_foreign_key('subscriptions_tenant_id_fkey', 'subscriptions', 'tenants', ['tenant_id'], ['id'])
    
    # 2. products.tenant_id
    op.drop_constraint('products_tenant_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key('products_tenant_id_fkey', 'products', 'tenants', ['tenant_id'], ['id'])
    
    # 3. billing_profiles.tenant_id
    op.drop_constraint('billing_profiles_tenant_id_fkey', 'billing_profiles', type_='foreignkey')
    op.create_foreign_key('billing_profiles_tenant_id_fkey', 'billing_profiles', 'tenants', ['tenant_id'], ['id'])
    
    # 4. invoices.tenant_id
    op.drop_constraint('invoices_tenant_id_fkey', 'invoices', type_='foreignkey')
    op.create_foreign_key('invoices_tenant_id_fkey', 'invoices', 'tenants', ['tenant_id'], ['id'])
    
    # 5. payments.tenant_id
    op.drop_constraint('payments_tenant_id_fkey', 'payments', type_='foreignkey')
    op.create_foreign_key('payments_tenant_id_fkey', 'payments', 'tenants', ['tenant_id'], ['id'])
    
    # 6. billing_credits.tenant_id
    op.drop_constraint('billing_credits_tenant_id_fkey', 'billing_credits', type_='foreignkey')
    op.create_foreign_key('billing_credits_tenant_id_fkey', 'billing_credits', 'tenants', ['tenant_id'], ['id'])
    
    # 7. usage_records.tenant_id
    op.drop_constraint('usage_records_tenant_id_fkey', 'usage_records', type_='foreignkey')
    op.create_foreign_key('usage_records_tenant_id_fkey', 'usage_records', 'tenants', ['tenant_id'], ['id'])
    
    # 8. conversations.tenant_id (restore SET NULL behavior)
    op.drop_constraint('conversations_tenant_id_fkey', 'conversations', type_='foreignkey')
    op.create_foreign_key('conversations_tenant_id_fkey', 'conversations', 'tenants', ['tenant_id'], ['id'], ondelete='SET NULL')
