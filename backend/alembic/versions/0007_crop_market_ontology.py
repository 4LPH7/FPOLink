"""Phase 8: Add crop ontology, crop_aliases, variety_aliases, and market_aliases.

Revision ID: 0007_crop_market_ontology
Revises: 0006_statewide_foundation
Create Date: 2026-09-24
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "0007_crop_market_ontology"
down_revision: str = "0006_statewide_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Expand crops table
    op.add_column("crops", sa.Column("canonical_name", sa.String(100), unique=True, nullable=True))
    op.add_column("crops", sa.Column("scientific_name", sa.String(150), nullable=True))
    op.add_column("crops", sa.Column("subcategory", sa.String(50), nullable=True))
    op.add_column(
        "crops", sa.Column("default_unit", sa.String(20), nullable=True, server_default="kg")
    )
    op.add_column(
        "crops", sa.Column("market_unit", sa.String(20), nullable=True, server_default="quintal")
    )
    op.add_column("crops", sa.Column("season_type", sa.String(50), nullable=True))
    op.add_column("crops", sa.Column("water_requirement", sa.String(20), nullable=True))
    op.add_column("crops", sa.Column("perishability", sa.String(20), nullable=True))
    op.add_column("crops", sa.Column("storage_days", sa.Integer(), nullable=True))
    op.add_column(
        "crops", sa.Column("is_horticulture", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "crops", sa.Column("is_commercial", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "crops", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true")
    )

    # 2. Create crop_aliases table
    op.create_table(
        "crop_aliases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "crop_id",
            UUID(as_uuid=True),
            sa.ForeignKey("crops.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias", sa.String(100), unique=True, nullable=False),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 3. Expand varieties table
    op.add_column("varieties", sa.Column("canonical_name", sa.String(100), nullable=True))
    op.add_column("varieties", sa.Column("maturity_days", sa.Integer(), nullable=True))
    op.add_column("varieties", sa.Column("market_unit", sa.String(20), nullable=True))

    # 4. Create variety_aliases table
    op.create_table(
        "variety_aliases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "variety_id",
            UUID(as_uuid=True),
            sa.ForeignKey("varieties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias", sa.String(100), nullable=False),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_variety_aliases_alias", "variety_aliases", ["alias"])

    # 5. Create market_aliases table
    op.create_table(
        "market_aliases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "market_id",
            UUID(as_uuid=True),
            sa.ForeignKey("markets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias", sa.String(200), unique=True, nullable=False),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("market_aliases")

    op.drop_index("ix_variety_aliases_alias", table_name="variety_aliases")
    op.drop_table("variety_aliases")

    op.drop_column("varieties", "market_unit")
    op.drop_column("varieties", "maturity_days")
    op.drop_column("varieties", "canonical_name")

    op.drop_table("crop_aliases")

    op.drop_column("crops", "is_active")
    op.drop_column("crops", "is_commercial")
    op.drop_column("crops", "is_horticulture")
    op.drop_column("crops", "storage_days")
    op.drop_column("crops", "perishability")
    op.drop_column("crops", "water_requirement")
    op.drop_column("crops", "season_type")
    op.drop_column("crops", "market_unit")
    op.drop_column("crops", "default_unit")
    op.drop_column("crops", "subcategory")
    op.drop_column("crops", "scientific_name")
    op.drop_column("crops", "canonical_name")
