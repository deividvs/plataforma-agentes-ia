"""Add contact fields used by WhatsApp message processing and chat lists.

Revision ID: 0003
Revises: 0002
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("contacts", sa.Column("sender_lid", sa.String(length=255), nullable=True))
    op.add_column("contacts", sa.Column("source_id", sa.String(length=255), nullable=True))
    op.add_column("contacts", sa.Column("thumbnail_url", sa.Text(), nullable=True))
    op.add_column("contacts", sa.Column("last_message_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("contacts", sa.Column("unread_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("contacts", sa.Column("archived", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_unique_constraint(
        "uq_contact_client_company_phone", "contacts", ["client_id", "company_id", "phone"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_contact_client_company_phone", "contacts", type_="unique")
    op.drop_column("contacts", "archived")
    op.drop_column("contacts", "unread_count")
    op.drop_column("contacts", "last_message_at")
    op.drop_column("contacts", "thumbnail_url")
    op.drop_column("contacts", "source_id")
    op.drop_column("contacts", "sender_lid")
