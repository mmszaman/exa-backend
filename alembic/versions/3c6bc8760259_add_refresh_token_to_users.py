"""add_refresh_token_to_users

Revision ID: 3c6bc8760259
Revises: fa5e8a66006c
Create Date: 2025-12-12 09:55:35.972111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c6bc8760259'
down_revision: Union[str, Sequence[str], None] = 'fa5e8a66006c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('refresh_token', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'refresh_token')
