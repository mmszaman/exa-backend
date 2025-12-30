"""migrate_to_clerk_authentication

Revision ID: a1b2c3d4e5f6
Revises: 3c6bc8760259
Create Date: 2025-12-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '3c6bc8760259'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migrate users table from JWT authentication to Clerk authentication.
    
    Changes:
    - Add clerk_user_id column (unique, indexed)
    - Remove hashed_password column
    - Remove is_verified column (Clerk handles verification)
    - Remove reset_otp and reset_otp_expiry columns
    - Remove refresh_token column
    - Make username nullable (Clerk may not always have username)
    """
    
    # Add clerk_user_id column (nullable initially for migration)
    op.add_column('users', sa.Column('clerk_user_id', sa.String(), nullable=True))
    
    # For existing users: generate a placeholder clerk_user_id
    # In production, you would migrate users to Clerk first
    op.execute("""
        UPDATE users 
        SET clerk_user_id = 'migrated_' || id::text 
        WHERE clerk_user_id IS NULL
    """)
    
    # Now make it non-nullable and add constraints
    op.alter_column('users', 'clerk_user_id', nullable=False)
    op.create_index('ix_users_clerk_user_id', 'users', ['clerk_user_id'])
    op.create_unique_constraint('uq_users_clerk_user_id', 'users', ['clerk_user_id'])
    
    # Make username nullable
    op.alter_column('users', 'username', nullable=True)
    
    # Remove authentication-related columns
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'reset_otp')
    op.drop_column('users', 'reset_otp_expiry')
    op.drop_column('users', 'refresh_token')


def downgrade() -> None:
    """
    Rollback to JWT authentication.
    WARNING: This will lose Clerk user associations.
    """
    
    # Add back authentication columns
    op.add_column('users', sa.Column('refresh_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_otp_expiry', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('reset_otp', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    
    # Make username non-nullable again (set default for null values)
    op.execute("UPDATE users SET username = email WHERE username IS NULL")
    op.alter_column('users', 'username', nullable=False)
    
    # Remove Clerk-specific columns
    op.drop_constraint('uq_users_clerk_user_id', 'users', type_='unique')
    op.drop_index('ix_users_clerk_user_id', 'users')
    op.drop_column('users', 'clerk_user_id')
