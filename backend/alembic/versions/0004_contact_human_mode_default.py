"""Default new contacts to agent mode when inserted through SQL.

Revision ID: 0004
Revises: 0003
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("contacts", "human_mode", server_default=sa.false())


def downgrade() -> None:
    op.alter_column("contacts", "human_mode", server_default=None)
