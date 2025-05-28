"""Add is_active to Token

Revision ID: 82a21336fbb3
Revises: 2a717a8424b1
Create Date: 2025-05-22 02:09:42.631897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82a21336fbb3'
down_revision: Union[str, None] = '2a717a8424b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
