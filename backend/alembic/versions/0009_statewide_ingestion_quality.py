"""Phase 8: Statewide Ingestion runs, data sources, and quality scoring.

Revision ID: 0009_statewide_ingestion_quality
Revises: 0008_multitenant_rbac_audit
Create Date: 2026-09-24
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision: str = "0009_statewide_ingestion_quality"
down_revision: str = "0008_multitenant_rbac_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add quality scoring columns to market_prices
    op.add_column(
        "market_prices",
        sa.Column("quality_score", sa.Float(), nullable=True, server_default="100.0"),
    )
    op.add_column("market_prices", sa.Column("quality_breakdown", JSONB(), nullable=True))

    # 2. Create data_sources table
    op.create_table(
        "data_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 3. Create ingestion_runs table
    op.create_table(
        "ingestion_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source_code", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("records_fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_ingested", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 4. Create data_quality_events table
    op.create_table(
        "data_quality_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("record_type", sa.String(50), nullable=False),
        sa.Column("record_id", sa.String(100), nullable=False),
        sa.Column("issue_type", sa.String(50), nullable=False),
        sa.Column("penalty", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("details", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("data_quality_events")
    op.drop_table("ingestion_runs")
    op.drop_table("data_sources")
    op.drop_column("market_prices", "quality_breakdown")
    op.drop_column("market_prices", "quality_score")
