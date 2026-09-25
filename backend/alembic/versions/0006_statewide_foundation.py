"""Phase 8: Add geography hierarchy and link foreign keys to FPO, Farmer, and Market.

Revision ID: 0006_statewide_foundation
Revises: 0005_phase5_prod
Create Date: 2026-09-24
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "0006_statewide_foundation"
down_revision: str = "0005_phase5_prod"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. States table
    op.create_table(
        "states",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("code", sa.String(10), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 2. Districts table
    op.create_table(
        "districts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "state_id",
            UUID(as_uuid=True),
            sa.ForeignKey("states.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 3. Taluks table
    op.create_table(
        "taluks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "district_id",
            UUID(as_uuid=True),
            sa.ForeignKey("districts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 4. Blocks table
    op.create_table(
        "blocks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "taluk_id",
            UUID(as_uuid=True),
            sa.ForeignKey("taluks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 5. Villages table
    op.create_table(
        "villages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "taluk_id",
            UUID(as_uuid=True),
            sa.ForeignKey("taluks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "block_id",
            UUID(as_uuid=True),
            sa.ForeignKey("blocks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 6. Add columns to fpos
    op.add_column(
        "fpos", sa.Column("state_id", UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=True)
    )
    op.add_column(
        "fpos",
        sa.Column("district_id", UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True),
    )
    op.add_column(
        "fpos", sa.Column("taluk_id", UUID(as_uuid=True), sa.ForeignKey("taluks.id"), nullable=True)
    )

    # 7. Add columns to farmers
    op.add_column(
        "farmers",
        sa.Column("state_id", UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=True),
    )
    op.add_column(
        "farmers",
        sa.Column("district_id", UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True),
    )
    op.add_column(
        "farmers",
        sa.Column("taluk_id", UUID(as_uuid=True), sa.ForeignKey("taluks.id"), nullable=True),
    )
    op.add_column(
        "farmers",
        sa.Column("village_id", UUID(as_uuid=True), sa.ForeignKey("villages.id"), nullable=True),
    )

    # 8. Add columns to markets
    op.add_column(
        "markets",
        sa.Column("state_id", UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=True),
    )
    op.add_column(
        "markets",
        sa.Column("district_id", UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True),
    )
    op.add_column(
        "markets",
        sa.Column("taluk_id", UUID(as_uuid=True), sa.ForeignKey("taluks.id"), nullable=True),
    )
    op.add_column("markets", sa.Column("code", sa.String(50), unique=True, nullable=True))
    op.add_column(
        "markets", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true")
    )


def downgrade() -> None:
    op.drop_column("markets", "is_active")
    op.drop_column("markets", "code")
    op.drop_column("markets", "taluk_id")
    op.drop_column("markets", "district_id")
    op.drop_column("markets", "state_id")

    op.drop_column("farmers", "village_id")
    op.drop_column("farmers", "taluk_id")
    op.drop_column("farmers", "district_id")
    op.drop_column("farmers", "state_id")

    op.drop_column("fpos", "taluk_id")
    op.drop_column("fpos", "district_id")
    op.drop_column("fpos", "state_id")

    op.drop_table("villages")
    op.drop_table("blocks")
    op.drop_table("taluks")
    op.drop_table("districts")
    op.drop_table("states")
