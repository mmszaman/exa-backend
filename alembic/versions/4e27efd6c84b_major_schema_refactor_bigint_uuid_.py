"""major_schema_refactor_bigint_uuid_billing

Revision ID: 4e27efd6c84b
Revises: cf058fa7d0de
Create Date: 2026-01-04 16:40:29.780390

IMPORTANT: This is a BREAKING migration that will DROP ALL EXISTING DATA
This migration:
1. Changes all IDs from Integer to BigInteger
2. Adds public_id (UUID) to all tables
3. Adds deleted_at for soft deletes
4. Changes JSON to JSONB
5. Adds new billing tables
6. Removes sessions and user_history tables
7. Updates relationships and constraints

FOR PRODUCTION: You would need to create a data migration script instead
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '4e27efd6c84b'
down_revision: Union[str, Sequence[str], None] = 'cf058fa7d0de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - WARNING: DROPS ALL TABLES"""
    
    # Drop all existing tables
    op.execute('DROP TABLE IF EXISTS user_history CASCADE')
    op.execute('DROP TABLE IF EXISTS sessions CASCADE')
    op.execute('DROP TABLE IF EXISTS businesses CASCADE')
    op.execute('DROP TABLE IF EXISTS subscriptions CASCADE')
    op.execute('DROP TABLE IF EXISTS memberships CASCADE')
    op.execute('DROP TABLE IF EXISTS products CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    op.execute('DROP TABLE IF EXISTS tenants CASCADE')
    
    # Drop existing enums if they exist
    op.execute('DROP TYPE IF EXISTS tenantstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS membershiprole CASCADE')
    op.execute('DROP TYPE IF EXISTS businesstype CASCADE')
    op.execute('DROP TYPE IF EXISTS businessstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS invoicestatus CASCADE')
    op.execute('DROP TYPE IF EXISTS paymentstatus CASCADE')
    
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create new enums
    op.execute("CREATE TYPE tenantstatus AS ENUM ('active', 'inactive', 'suspended', 'trial')")
    op.execute("CREATE TYPE membershiprole AS ENUM ('owner', 'admin', 'member', 'viewer')")
    op.execute("CREATE TYPE businesstype AS ENUM ('llc', 'corporation', 'partnership', 'sole_proprietorship', 'nonprofit', 'other')")
    op.execute("CREATE TYPE businessstatus AS ENUM ('active', 'inactive', 'pending', 'suspended')")
    op.execute("CREATE TYPE subscriptionstatus AS ENUM ('active', 'trialing', 'past_due', 'canceled', 'expired')")
    op.execute("CREATE TYPE invoicestatus AS ENUM ('draft', 'open', 'paid', 'void', 'uncollectible')")
    op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded')")
    
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('clerk_org_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('brand', sa.String(100)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('website', sa.String(255)),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('settings', JSONB),
        sa.Column('features', JSONB),
        sa.Column('clerk_metadata', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    # Manually set the column type to use the enum
    op.execute("ALTER TABLE tenants ALTER COLUMN status TYPE tenantstatus USING status::tenantstatus")
    op.create_index('ix_tenants_id', 'tenants', ['id'])
    op.create_index('ix_tenants_public_id', 'tenants', ['public_id'], unique=True)
    op.create_index('ix_tenants_clerk_org_id', 'tenants', ['clerk_org_id'], unique=True)
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)
    op.create_index('ix_tenants_created_at', 'tenants', ['created_at'])
    op.create_index('ix_tenants_deleted_at', 'tenants', ['deleted_at'])
    op.create_index('idx_brand_status', 'tenants', ['brand', 'status'])
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('clerk_user_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255)),
        sa.Column('full_name', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('phone_number', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('lead_source', sa.String(100)),
        sa.Column('brand', sa.String(100)),
        sa.Column('referral_code', sa.String(50)),
        sa.Column('utm_source', sa.String(100)),
        sa.Column('utm_medium', sa.String(100)),
        sa.Column('utm_campaign', sa.String(100)),
        sa.Column('newsletter', sa.Boolean(), default=False),
        sa.Column('email_notifications', sa.Boolean(), default=True),
        sa.Column('marketing_emails', sa.Boolean(), default=False),
        sa.Column('clerk_metadata', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_public_id', 'users', ['public_id'], unique=True)
    op.create_index('ix_users_clerk_user_id', 'users', ['clerk_user_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])
    
    # Create memberships table
    op.create_table('memberships',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permissions', JSONB),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'tenant_id', name='uq_user_tenant')
    )
    op.execute("ALTER TABLE memberships ALTER COLUMN role TYPE membershiprole USING role::membershiprole")
    op.create_index('ix_memberships_public_id', 'memberships', ['public_id'], unique=True)
    op.create_index('ix_memberships_tenant_id', 'memberships', ['tenant_id'])
    op.create_index('ix_memberships_user_id', 'memberships', ['user_id'])
    op.create_index('ix_memberships_deleted_at', 'memberships', ['deleted_at'])
    
    # Create businesses table
    op.create_table('businesses',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('owner_user_id', sa.BigInteger()),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('legal_name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('tax_id', sa.String(50)),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('website', sa.String(255)),
        sa.Column('address', JSONB, nullable=False),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('description', sa.Text()),
        sa.Column('industry', sa.String(100)),
        sa.Column('employee_count', sa.BigInteger()),
        sa.Column('founded_year', sa.BigInteger()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("ALTER TABLE businesses ALTER COLUMN type TYPE businesstype USING type::businesstype")
    op.execute("ALTER TABLE businesses ALTER COLUMN status TYPE businessstatus USING status::businessstatus")
    op.create_index('ix_businesses_id', 'businesses', ['id'])
    op.create_index('ix_businesses_public_id', 'businesses', ['public_id'], unique=True)
    op.create_index('ix_businesses_tenant_id', 'businesses', ['tenant_id'])
    op.create_index('ix_businesses_created_at', 'businesses', ['created_at'])
    op.create_index('ix_businesses_deleted_at', 'businesses', ['deleted_at'])
    op.create_index('idx_tenant_status', 'businesses', ['tenant_id', 'status'])
    
    # Create products table
    op.create_table('products',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('version', sa.BigInteger(), default=1),
        sa.Column('is_current', sa.Boolean(), default=True),
        sa.Column('price_monthly', sa.Numeric(10, 2)),
        sa.Column('price_yearly', sa.Numeric(10, 2)),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('features', JSONB),
        sa.Column('limits', JSONB),
        sa.Column('stripe_product_id', sa.String(255)),
        sa.Column('stripe_price_monthly_id', sa.String(255)),
        sa.Column('stripe_price_yearly_id', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_public_id', 'products', ['public_id'], unique=True)
    op.create_index('ix_products_code', 'products', ['code'], unique=True)
    op.create_index('ix_products_created_at', 'products', ['created_at'])
    op.create_index('ix_products_deleted_at', 'products', ['deleted_at'])
    
    # Create billing_profiles table
    op.create_table('billing_profiles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('provider', sa.String(50), default='stripe'),
        sa.Column('stripe_customer_id', sa.String(255)),
        sa.Column('billing_email', sa.String(255)),
        sa.Column('billing_name', sa.String(255)),
        sa.Column('billing_address', JSONB),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('tax_id', sa.String(100)),
        sa.Column('tax_exempt', sa.Boolean(), default=False),
        sa.Column('default_payment_method', sa.String(255)),
        sa.Column('payment_methods', JSONB),
        sa.Column('provider_metadata', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_billing_profiles_public_id', 'billing_profiles', ['public_id'], unique=True)
    op.create_index('ix_billing_profiles_tenant_id', 'billing_profiles', ['tenant_id'], unique=True)
    op.create_index('ix_billing_profiles_deleted_at', 'billing_profiles', ['deleted_at'])
    
    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('billing_profile_id', sa.BigInteger()),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True)),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True)),
        sa.Column('price_monthly', sa.Numeric(10, 2)),
        sa.Column('price_yearly', sa.Numeric(10, 2)),
        sa.Column('features_snapshot', JSONB),
        sa.Column('limits_snapshot', JSONB),
        sa.Column('stripe_subscription_id', sa.String(255)),
        sa.Column('cancel_at_period_end', sa.Boolean(), default=False),
        sa.Column('canceled_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['billing_profile_id'], ['billing_profiles.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_public_id', 'subscriptions', ['public_id'], unique=True)
    op.create_index('ix_subscriptions_created_at', 'subscriptions', ['created_at'])
    op.create_index('ix_subscriptions_deleted_at', 'subscriptions', ['deleted_at'])
    op.create_index('idx_subscription_tenant_status', 'subscriptions', ['tenant_id', 'status'])
    op.execute("ALTER TABLE subscriptions ALTER COLUMN status TYPE subscriptionstatus USING status::subscriptionstatus")
    
    # Create invoices table
    op.create_table('invoices',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('billing_profile_id', sa.BigInteger()),
        sa.Column('subscription_id', sa.BigInteger()),
        sa.Column('provider_invoice_id', sa.String(255)),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('subtotal_amount', sa.Numeric(10, 2), default=0),
        sa.Column('tax_amount', sa.Numeric(10, 2), default=0),
        sa.Column('total_amount', sa.Numeric(10, 2), default=0),
        sa.Column('due_at', sa.DateTime(timezone=True)),
        sa.Column('paid_at', sa.DateTime(timezone=True)),
        sa.Column('invoice_pdf_url', sa.String(500)),
        sa.Column('provider_metadata', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['billing_profile_id'], ['billing_profiles.id']),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invoices_public_id', 'invoices', ['public_id'], unique=True)
    op.create_index('ix_invoices_created_at', 'invoices', ['created_at'])
    op.execute("ALTER TABLE invoices ALTER COLUMN status TYPE invoicestatus USING status::invoicestatus")
    
    # Create invoice_line_items table
    op.create_table('invoice_line_items',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('invoice_id', sa.BigInteger(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('quantity', sa.BigInteger(), default=1),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('line_metadata', JSONB),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('billing_profile_id', sa.BigInteger()),
        sa.Column('invoice_id', sa.BigInteger()),
        sa.Column('provider_payment_id', sa.String(255)),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('payment_method', sa.String(100)),
        sa.Column('failure_reason', sa.Text()),
        sa.Column('provider_metadata', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['billing_profile_id'], ['billing_profiles.id']),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payments_public_id', 'payments', ['public_id'], unique=True)
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])
    op.execute("ALTER TABLE payments ALTER COLUMN status TYPE paymentstatus USING status::paymentstatus")
    
    # Create billing_credits table
    op.create_table('billing_credits',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('billing_profile_id', sa.BigInteger()),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('reason', sa.String(255)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['billing_profile_id'], ['billing_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_billing_credits_created_at', 'billing_credits', ['created_at'])
    
    # Create usage_records table
    op.create_table('usage_records',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('subscription_id', sa.BigInteger()),
        sa.Column('metric', sa.String(100), nullable=False),
        sa.Column('quantity', sa.BigInteger(), default=0),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usage_records_recorded_at', 'usage_records', ['recorded_at'])


def downgrade() -> None:
    """Downgrade schema - WARNING: DROPS ALL TABLES"""
    op.execute('DROP TABLE IF EXISTS usage_records CASCADE')
    op.execute('DROP TABLE IF EXISTS billing_credits CASCADE')
    op.execute('DROP TABLE IF EXISTS payments CASCADE')
    op.execute('DROP TABLE IF EXISTS invoice_line_items CASCADE')
    op.execute('DROP TABLE IF EXISTS invoices CASCADE')
    op.execute('DROP TABLE IF EXISTS subscriptions CASCADE')
    op.execute('DROP TABLE IF EXISTS billing_profiles CASCADE')
    op.execute('DROP TABLE IF EXISTS products CASCADE')
    op.execute('DROP TABLE IF EXISTS businesses CASCADE')
    op.execute('DROP TABLE IF EXISTS memberships CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    op.execute('DROP TABLE IF EXISTS tenants CASCADE')
    
    op.execute('DROP TYPE IF EXISTS paymentstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS invoicestatus CASCADE')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS businessstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS businesstype CASCADE')
    op.execute('DROP TYPE IF EXISTS membershiprole CASCADE')
    op.execute('DROP TYPE IF EXISTS tenantstatus CASCADE')
