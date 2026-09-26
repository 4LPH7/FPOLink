"""Phase 13: Supply and demand network — farms plots, buyers, requirements, and supply matches.

Revision ID: 0011_supply_demand_network
Revises: 0010_source_mappings_markets
Create Date: 2026-09-26
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision: str = "0011_supply_demand_network"
down_revision: str = "0010_source_mappings_markets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Expand farms table with plot metadata & yield tracking
    op.add_column("farms", sa.Column("plot_name", sa.String(100), nullable=True))
    op.add_column("farms", sa.Column("village", sa.String(100), nullable=True))
    op.add_column("farms", sa.Column("soil_type", sa.String(50), nullable=True))
    op.add_column("farms", sa.Column("irrigation_type", sa.String(50), nullable=True))
    op.add_column("farms", sa.Column("expected_yield_kg", sa.Float(), nullable=True))
    op.add_column("farms", sa.Column("actual_yield_kg", sa.Float(), nullable=True))
    op.add_column(
        "farms",
        sa.Column(
            "state_id",
            UUID(as_uuid=True),
            sa.ForeignKey("states.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "farms",
        sa.Column(
            "district_id",
            UUID(as_uuid=True),
            sa.ForeignKey("districts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "farms",
        sa.Column(
            "taluk_id",
            UUID(as_uuid=True),
            sa.ForeignKey("taluks.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "farms",
        sa.Column(
            "village_id",
            UUID(as_uuid=True),
            sa.ForeignKey("villages.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # 2. Expand buyers table (make user_id nullable for staff mediation, add FPO scoping)
    op.alter_column(
        "buyers",
        "user_id",
        existing_type=UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column(
        "buyers",
        sa.Column(
            "fpo_id",
            UUID(as_uuid=True),
            sa.ForeignKey("fpos.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "buyers",
        sa.Column("buyer_type", sa.String(50), nullable=False, server_default="wholesaler"),
    )
    op.add_column("buyers", sa.Column("contact_name", sa.String(100), nullable=True))
    op.add_column("buyers", sa.Column("district", sa.String(100), nullable=True))
    op.add_column(
        "buyers",
        sa.Column(
            "district_id",
            UUID(as_uuid=True),
            sa.ForeignKey("districts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "buyers",
        sa.Column(
            "state_id",
            UUID(as_uuid=True),
            sa.ForeignKey("states.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("buyers", sa.Column("gstin", sa.String(20), nullable=True))
    op.add_column(
        "buyers",
        sa.Column("verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "buyers",
        sa.Column(
            "created_by_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # 3. Expand buyer_requirements table
    op.add_column(
        "buyer_requirements",
        sa.Column(
            "fpo_id",
            UUID(as_uuid=True),
            sa.ForeignKey("fpos.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "buyer_requirements",
        sa.Column(
            "district_id",
            UUID(as_uuid=True),
            sa.ForeignKey("districts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "buyer_requirements",
        sa.Column(
            "variety_id",
            UUID(as_uuid=True),
            sa.ForeignKey("varieties.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "buyer_requirements",
        sa.Column("fulfilled_quantity_kg", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "buyer_requirements",
        sa.Column("delivery_window_days", sa.Integer(), nullable=False, server_default="7"),
    )
    op.add_column(
        "buyer_requirements",
        sa.Column("delivery_location", sa.String(200), nullable=True),
    )
    op.add_column(
        "buyer_requirements",
        sa.Column(
            "created_by_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # 4. Create supply_matches table
    op.create_table(
        "supply_matches",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "buyer_requirement_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buyer_requirements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "farm_id",
            UUID(as_uuid=True),
            sa.ForeignKey("farms.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "harvest_id",
            UUID(as_uuid=True),
            sa.ForeignKey("harvests.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "fpo_id",
            UUID(as_uuid=True),
            sa.ForeignKey("fpos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("matched_quantity_kg", sa.Float(), nullable=False),
        sa.Column("offered_price_per_kg", sa.Numeric(12, 2), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("match_breakdown", JSONB, nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="suggested"),
        sa.Column("staff_notes", sa.Text(), nullable=True),
        sa.Column(
            "confirmed_by_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("farmer_responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_supply_matches_buyer_req",
        "supply_matches",
        ["buyer_requirement_id"],
    )
    op.create_index(
        "ix_supply_matches_fpo",
        "supply_matches",
        ["fpo_id"],
    )
    op.create_index(
        "ix_supply_matches_status",
        "supply_matches",
        ["status"],
    )


def downgrade() -> None:
    op.drop_table("supply_matches")

    op.drop_column("buyer_requirements", "created_by_user_id")
    op.drop_column("buyer_requirements", "delivery_location")
    op.drop_column("buyer_requirements", "delivery_window_days")
    op.drop_column("buyer_requirements", "fulfilled_quantity_kg")
    op.drop_column("buyer_requirements", "variety_id")
    op.drop_column("buyer_requirements", "district_id")
    op.drop_column("buyer_requirements", "fpo_id")

    op.drop_column("buyers", "created_by_user_id")
    op.drop_column("buyers", "verified")
    op.drop_column("buyers", "gstin")
    op.drop_column("buyers", "state_id")
    op.drop_column("buyers", "district_id")
    op.drop_column("buyers", "district")
    op.drop_column("buyers", "contact_name")
    op.drop_column("buyers", "buyer_type")
    op.drop_column("buyers", "fpo_id")
    op.alter_column(
        "buyers",
        "user_id",
        existing_type=UUID(as_uuid=True),
        nullable=False,
    )

    op.drop_column("farms", "village_id")
    op.drop_column("farms", "taluk_id")
    op.drop_column("farms", "district_id")
    op.drop_column("farms", "state_id")
    op.drop_column("farms", "actual_yield_kg")
    op.drop_column("farms", "expected_yield_kg")
    op.drop_column("farms", "irrigation_type")
    op.drop_column("farms", "soil_type")
    op.drop_column("farms", "village")
    op.drop_column("farms", "plot_name")
