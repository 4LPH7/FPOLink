"""Phase 4: Outbound message tracking and recipient reputation

Revision ID: 0004_phase4_outbound
Revises: 0003_harvest_source_message_id
Create Date: 2026-09-23 10:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_phase4_outbound"
down_revision: Union[str, None] = "0003_harvest_source_message_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update outbound_messages
    op.add_column(
        "outbound_messages",
        sa.Column("meta_message_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_outbound_messages_meta_message_id",
        "outbound_messages",
        ["meta_message_id"],
        unique=False,
    )
    op.add_column(
        "outbound_messages",
        sa.Column(
            "error_details",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
    )
    op.add_column(
        "outbound_messages",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 2. Update farmers table
    op.add_column(
        "farmers",
        sa.Column(
            "is_unreachable",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    # 3. Create whatsapp_recipient_status table
    op.create_table(
        "whatsapp_recipient_status",
        sa.Column("wa_id", sa.String(length=50), nullable=False),
        sa.Column("consecutive_failures", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_unreachable", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_reason", sa.String(length=255), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("wa_id"),
    )


def downgrade() -> None:
    op.drop_table("whatsapp_recipient_status")
    op.drop_column("farmers", "is_unreachable")
    op.drop_column("outbound_messages", "updated_at")
    op.drop_column("outbound_messages", "error_details")
    op.drop_index("ix_outbound_messages_meta_message_id", table_name="outbound_messages")
    op.drop_column("outbound_messages", "meta_message_id")
