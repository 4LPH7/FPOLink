"""Phase 5: Add retry_count to whatsapp_inbound for at-least-once sweep.

Revision ID: 0005_phase5_prod
Revises: 0004_phase4_outbound
Create Date: 2026-09-23
"""

import sqlalchemy as sa

from alembic import op

revision: str = "0005_phase5_prod"
down_revision: str = "0004_phase4_outbound"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "whatsapp_inbound",
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("whatsapp_inbound", "retry_count")
