"""Add notice_sent_at to farmers for DPDP first-contact notice tracking

Revision ID: 0003_farmer_notice_sent_at
Revises: 0002_whatsapp_and_farmer_consent
Create Date: 2026-09-20 22:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_farmer_notice_sent_at"
down_revision: Union[str, None] = "0002_whatsapp_and_farmer_consent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "farmers",
        sa.Column("notice_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("farmers", "notice_sent_at")
