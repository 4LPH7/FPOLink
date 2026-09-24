"""Phase 8: Multi-tenant RBAC expansion, user scoping, and audit logging.

Revision ID: 0008_multitenant_rbac_audit
Revises: 0007_crop_market_ontology
Create Date: 2026-09-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0008_multitenant_rbac_audit"
down_revision: str = "0007_crop_market_ontology"
branch_labels = None
depends_on = None


def upgrade() -> None:
    new_roles = [
        "state_admin",
        "STATE_ADMIN",
        "district_admin",
        "DISTRICT_ADMIN",
        "fpo_admin",
        "FPO_ADMIN",
        "data_operator",
        "DATA_OPERATOR",
        "analyst",
        "ANALYST",
        "field_agent",
        "FIELD_AGENT",
    ]
    for role_val in new_roles:
        op.execute(sa.text(f"ALTER TYPE userrole ADD VALUE IF NOT EXISTS '{role_val}'"))

    # 2. Add tenant scoping columns to users
    op.add_column("users", sa.Column("fpo_id", UUID(as_uuid=True), sa.ForeignKey("fpos.id"), nullable=True))
    op.add_column("users", sa.Column("district_id", UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True))

    # 3. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=False),
        sa.Column("before_state", JSONB(), nullable=True),
        sa.Column("after_state", JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_column("users", "district_id")
    op.drop_column("users", "fpo_id")
