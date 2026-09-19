"""Initial schema with all 21 tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-19 17:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=15), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "FPO_STAFF", "FARMER", "BUYER", name="userrole"),
            nullable=False,
        ),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("language_preference", sa.String(length=2), nullable=True, server_default="en"),
        sa.Column("telegram_chat_id", sa.String(), nullable=True),
        sa.Column("consent_given", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("consent_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    # --- 2. fpos ---
    op.create_table(
        "fpos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("registration_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("village", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True, server_default="Tamil Nadu"),
        sa.Column("contact_phone", sa.String(length=15), nullable=False),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 3. crops ---
    op.create_table(
        "crops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("tamil_name", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True, server_default="kg"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 4. varieties ---
    op.create_table(
        "varieties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("tamil_name", sa.String(length=100), nullable=True),
        sa.Column("grade", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 5. farmers ---
    op.create_table(
        "farmers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "fpo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fpos.id"), nullable=False
        ),
        sa.Column("village", sa.String(length=100), nullable=False),
        sa.Column("taluk", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=True, server_default="Erode"),
        sa.Column("farm_area_acres", sa.Float(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 6. farms ---
    op.create_table(
        "farms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id"), nullable=False
        ),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column("area_acres", sa.Float(), nullable=False),
        sa.Column("sowing_date", sa.Date(), nullable=True),
        sa.Column("expected_harvest_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 7. markets ---
    op.create_table(
        "markets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True, server_default="Tamil Nadu"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("market_type", sa.String(length=50), nullable=False, server_default="mandi"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 8. harvests ---
    op.create_table(
        "harvests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id"), nullable=False
        ),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column("quantity_kg", sa.Float(), nullable=False),
        sa.Column("grade", sa.Enum("A", "B", "C", name="harvestgrade"), nullable=False),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("SUBMITTED", "VERIFIED", "AGGREGATED", "SOLD", name="harveststatus"),
            nullable=True,
            server_default="SUBMITTED",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 9. market_prices ---
    op.create_table(
        "market_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column(
            "variety_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("varieties.id"),
            nullable=True,
        ),
        sa.Column(
            "market_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("markets.id"), nullable=False
        ),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("min_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("max_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("modal_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("raw_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("raw_unit", sa.String(length=20), nullable=True),
        sa.Column("arrival_quantity", sa.Float(), nullable=True),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.UniqueConstraint(
            "crop_id",
            "market_id",
            "variety_id",
            "price_date",
            "source",
            name="uix_market_price_details",
            postgresql_nulls_not_distinct=True,
        ),
    )
    op.create_index("ix_market_prices_price_date", "market_prices", ["price_date"])

    # --- 10. model_versions ---
    op.create_table(
        "model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_type", sa.String(length=50), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 11. predictions ---
    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column(
            "market_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("markets.id"), nullable=False
        ),
        sa.Column("predicted_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("lower_bound", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("upper_bound", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "model_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_versions.id"),
            nullable=True,
        ),
        sa.Column("prediction_date", sa.Date(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("signal", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 12. forecast_log ---
    op.create_table(
        "forecast_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "prediction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("predictions.id"),
            nullable=False,
        ),
        sa.Column("actual_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("error", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 13. buyers ---
    op.create_table(
        "buyers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("contact_phone", sa.String(length=15), nullable=False),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 14. buyer_requirements ---
    op.create_table(
        "buyer_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyers.id"), nullable=False
        ),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column("quantity_kg", sa.Float(), nullable=False),
        sa.Column(
            "min_grade",
            sa.Enum("A", "B", "C", name="harvestgrade", create_type=False),
            nullable=False,
        ),
        sa.Column("required_date", sa.Date(), nullable=False),
        sa.Column("max_price_per_kg", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True, server_default="open"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 15. aggregation_batches ---
    op.create_table(
        "aggregation_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "fpo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fpos.id"), nullable=False
        ),
        sa.Column(
            "crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crops.id"), nullable=False
        ),
        sa.Column("total_quantity_kg", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("target_quantity_kg", sa.Float(), nullable=True),
        sa.Column(
            "grade", sa.Enum("A", "B", "C", name="harvestgrade", create_type=False), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum("OPEN", "FILLING", "READY", "SOLD", "COMPLETED", name="batchstatus"),
            nullable=True,
            server_default="OPEN",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 16. batch_items ---
    op.create_table(
        "batch_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("aggregation_batches.id"),
            nullable=False,
        ),
        sa.Column(
            "harvest_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("harvests.id"),
            nullable=False,
        ),
        sa.Column("quantity_kg", sa.Float(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 17. notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 18. orders ---
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "fpo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fpos.id"), nullable=False
        ),
        sa.Column(
            "buyer_requirement_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("buyer_requirements.id"),
            nullable=False,
        ),
        sa.Column(
            "batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("aggregation_batches.id"),
            nullable=False,
        ),
        sa.Column("quantity_kg", sa.Float(), nullable=False),
        sa.Column("price_per_kg", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 19. weather_data ---
    op.create_table(
        "weather_data",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("temperature_max", sa.Float(), nullable=False),
        sa.Column("temperature_min", sa.Float(), nullable=False),
        sa.Column("rainfall_mm", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True, server_default="open_meteo"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.UniqueConstraint("district", "date", name="uix_weather_district_date"),
    )

    # --- 20. ingestion_logs ---
    op.create_table(
        "ingestion_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("records_fetched", sa.Integer(), nullable=False),
        sa.Column("records_stored", sa.Integer(), nullable=False),
        sa.Column("errors", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("error_details", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column(
            "run_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )

    # --- 21. raw_ingest ---
    op.create_table(
        "raw_ingest",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column("processed", sa.Boolean(), nullable=True, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_table("raw_ingest")
    op.drop_table("ingestion_logs")
    op.drop_table("weather_data")
    op.drop_table("orders")
    op.drop_table("notifications")
    op.drop_table("batch_items")
    op.drop_table("aggregation_batches")
    op.drop_table("buyer_requirements")
    op.drop_table("buyers")
    op.drop_table("forecast_log")
    op.drop_table("predictions")
    op.drop_table("model_versions")
    op.drop_table("market_prices")
    op.drop_table("harvests")
    op.drop_table("markets")
    op.drop_table("farms")
    op.drop_table("farmers")
    op.drop_table("varieties")
    op.drop_table("crops")
    op.drop_table("fpos")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS batchstatus CASCADE;")
    op.execute("DROP TYPE IF EXISTS harveststatus CASCADE;")
    op.execute("DROP TYPE IF EXISTS harvestgrade CASCADE;")
    op.execute("DROP TYPE IF EXISTS userrole CASCADE;")
