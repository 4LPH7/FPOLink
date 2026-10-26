"""Per-farmer bot activity log for pilot reporting.

Revision ID: 0014_bot_activity
Revises: 0013_fpo_tasks
Create Date: 2026-10-26
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0014_bot_activity"
down_revision: str = "0013_fpo_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bot_activity",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "farmer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("farmers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("intent", sa.String(30), nullable=False),
        sa.Column("advice_shown", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_bot_activity_created_at", "bot_activity", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_bot_activity_created_at", table_name="bot_activity")
    op.drop_table("bot_activity")
