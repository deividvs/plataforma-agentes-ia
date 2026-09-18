"""Create the webhook audit table used by WAHA callbacks.

Revision ID: 0002
Revises: 0001
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "webhook_audit",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("instance_id", sa.String(length=255), nullable=False),
        sa.Column("company_id", sa.BigInteger(), nullable=True),
        sa.Column("message_id", sa.String(length=255), server_default="", nullable=False),
        sa.Column("phone", sa.String(length=100), server_default="", nullable=False),
        sa.Column("message_type", sa.String(length=100), nullable=False),
        sa.Column("message_data", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="received", nullable=False),
        sa.Column("processing_status", sa.String(length=50), nullable=True),
        sa.Column("task_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_webhook_audit_dedupe",
        "webhook_audit",
        ["company_id", "message_id", "message_type", "created_at"],
    )
    op.create_index(
        "idx_webhook_audit_status_created",
        "webhook_audit",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_webhook_audit_status_created", table_name="webhook_audit")
    op.drop_index("idx_webhook_audit_dedupe", table_name="webhook_audit")
    op.drop_table("webhook_audit")
