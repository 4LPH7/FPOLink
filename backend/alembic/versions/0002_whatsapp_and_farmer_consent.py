"""WhatsApp bot tables and farmer consent migration

Revision ID: 0002_whatsapp_and_farmer_consent
Revises: 0001_initial_schema
Create Date: 2026-09-20 19:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_whatsapp_and_farmer_consent"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns to farmers
    op.add_column("farmers", sa.Column("phone", sa.String(length=10), nullable=True))
    op.add_column(
        "farmers",
        sa.Column("lang", sa.String(length=10), nullable=False, server_default="ta"),
    )
    op.add_column(
        "farmers",
        sa.Column(
            "alerts_opt_in",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "farmers",
        sa.Column("alerts_opt_in_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "farmers",
        sa.Column("alerts_opt_out_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Backfill farmers.phone from users table (last 10 digits)
    # Checks dialect to support PostgreSQL regex and SQLite/generic fallback
    bind = op.get_bind()
    if bind and bind.dialect.name == "postgresql":
        op.execute(
            """
            UPDATE farmers f
            SET phone = RIGHT(REGEXP_REPLACE(u.phone, '\\D', '', 'g'), 10)
            FROM users u
            WHERE f.user_id = u.id AND f.phone IS NULL
            """
        )

    # 3. Create unique index on farmers(phone)
    op.create_index("ix_farmers_phone", "farmers", ["phone"], unique=True)

    # 4. whatsapp_inbound
    op.create_table(
        "whatsapp_inbound",
        sa.Column("message_id", sa.String(length=100), primary_key=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="received",
        ),
    )

    # 5. conversation_state
    json_col = (
        postgresql.JSONB(astext_type=sa.Text())
        if bind and bind.dialect.name == "postgresql"
        else sa.JSON()
    )
    op.create_table(
        "conversation_state",
        sa.Column("wa_id", sa.String(length=50), primary_key=True),
        sa.Column("step", sa.String(length=50), nullable=False, server_default="IDLE"),
        sa.Column("data", json_col, nullable=False, server_default="{}"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 6. outbound_messages
    uuid_col = (
        postgresql.UUID(as_uuid=True)
        if bind and bind.dialect.name == "postgresql"
        else sa.String(length=36)
    )
    op.create_table(
        "outbound_messages",
        sa.Column("id", uuid_col, primary_key=True),
        sa.Column("wa_id", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("template", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="sent",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_outbound_messages_wa_id", "outbound_messages", ["wa_id"])


def downgrade() -> None:
    op.drop_index("ix_outbound_messages_wa_id", table_name="outbound_messages")
    op.drop_table("outbound_messages")
    op.drop_table("conversation_state")
    op.drop_table("whatsapp_inbound")
    op.drop_index("ix_farmers_phone", table_name="farmers")
    op.drop_column("farmers", "alerts_opt_out_at")
    op.drop_column("farmers", "alerts_opt_in_at")
    op.drop_column("farmers", "alerts_opt_in")
    op.drop_column("farmers", "lang")
    op.drop_column("farmers", "phone")
