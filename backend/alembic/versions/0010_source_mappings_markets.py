"""Phase 9: Source mappings, market expansion, raw ingest checksum, and price lineage.

Revision ID: 0010_source_mappings_markets
Revises: 0009_statewide_ingestion_quality
Create Date: 2026-09-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0010_source_mappings_markets"
down_revision: str = "0009_statewide_ingestion_quality"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Expand markets table
    op.add_column("markets", sa.Column("canonical_name", sa.String(200), nullable=True))
    op.add_column("markets", sa.Column("tamil_name", sa.String(200), nullable=True))
    op.add_column("markets", sa.Column("is_regulated", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("markets", sa.Column("e_nam", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("markets", sa.Column("operating_status", sa.String(50), nullable=False, server_default="active"))

    # Backfill canonical_name with name where null
    op.execute("UPDATE markets SET canonical_name = lower(name) WHERE canonical_name IS NULL;")

    # 2. Expand raw_ingest table
    op.add_column("raw_ingest", sa.Column("source_record_id", sa.String(100), nullable=True))
    op.add_column("raw_ingest", sa.Column("checksum", sa.String(64), nullable=True))
    op.add_column("raw_ingest", sa.Column("retrieved_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_raw_ingest_checksum", "raw_ingest", ["checksum"])

    # 3. Expand market_prices table with lineage
    op.add_column("market_prices", sa.Column("ingestion_run_id", UUID(as_uuid=True), sa.ForeignKey("ingestion_runs.id", ondelete="SET NULL"), nullable=True))
    op.add_column("market_prices", sa.Column("raw_ingest_id", UUID(as_uuid=True), sa.ForeignKey("raw_ingest.id", ondelete="SET NULL"), nullable=True))

    # 4. Create crop_source_mappings
    op.create_table(
        "crop_source_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("crop_id", UUID(as_uuid=True), sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_code", sa.String(50), nullable=False),
        sa.Column("external_code", sa.String(100), nullable=False),
        sa.Column("external_name", sa.String(200), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("verified_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source_code", "external_code", name="uix_crop_source_mapping_code"),
    )
    op.create_index("ix_crop_source_mappings_source_code", "crop_source_mappings", ["source_code"])
    op.create_index("ix_crop_source_mappings_external_code", "crop_source_mappings", ["external_code"])
    op.create_index("ix_crop_source_mappings_external_name", "crop_source_mappings", ["external_name"])

    # 5. Create market_source_mappings
    op.create_table(
        "market_source_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("market_id", UUID(as_uuid=True), sa.ForeignKey("markets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_code", sa.String(50), nullable=False),
        sa.Column("external_code", sa.String(100), nullable=False),
        sa.Column("external_name", sa.String(200), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("verified_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source_code", "external_code", name="uix_market_source_mapping_code"),
    )
    op.create_index("ix_market_source_mappings_source_code", "market_source_mappings", ["source_code"])
    op.create_index("ix_market_source_mappings_external_code", "market_source_mappings", ["external_code"])
    op.create_index("ix_market_source_mappings_external_name", "market_source_mappings", ["external_name"])

    # 6. Create variety_source_mappings
    op.create_table(
        "variety_source_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("variety_id", UUID(as_uuid=True), sa.ForeignKey("varieties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_code", sa.String(50), nullable=False),
        sa.Column("external_code", sa.String(100), nullable=False),
        sa.Column("external_name", sa.String(200), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("verified_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source_code", "external_code", name="uix_variety_source_mapping_code"),
    )
    op.create_index("ix_variety_source_mappings_source_code", "variety_source_mappings", ["source_code"])
    op.create_index("ix_variety_source_mappings_external_code", "variety_source_mappings", ["external_code"])
    op.create_index("ix_variety_source_mappings_external_name", "variety_source_mappings", ["external_name"])


def downgrade() -> None:
    op.drop_table("variety_source_mappings")
    op.drop_table("market_source_mappings")
    op.drop_table("crop_source_mappings")
    op.drop_column("market_prices", "raw_ingest_id")
    op.drop_column("market_prices", "ingestion_run_id")
    op.drop_index("ix_raw_ingest_checksum", table_name="raw_ingest")
    op.drop_column("raw_ingest", "retrieved_at")
    op.drop_column("raw_ingest", "checksum")
    op.drop_column("raw_ingest", "source_record_id")
    op.drop_column("markets", "operating_status")
    op.drop_column("markets", "e_nam")
    op.drop_column("markets", "is_regulated")
    op.drop_column("markets", "tamil_name")
    op.drop_column("markets", "canonical_name")
