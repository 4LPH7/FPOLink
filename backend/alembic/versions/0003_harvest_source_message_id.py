"""Add source_message_id to harvests for WhatsApp idempotency

Revision ID: 0003_harvest_source_message_id
Revises: 0002_whatsapp_and_farmer_consent
Create Date: 2026-09-21 21:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_harvest_source_message_id"
down_revision: Union[str, None] = "0003_farmer_notice_sent_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "harvests",
        sa.Column("source_message_id", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_harvests_source_message_id",
        "harvests",
        ["source_message_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_harvests_source_message_id", table_name="harvests")
    op.drop_column("harvests", "source_message_id")
