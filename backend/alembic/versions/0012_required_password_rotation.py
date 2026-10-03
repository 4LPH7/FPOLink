"""Require existing privileged accounts to rotate credentials at next sign-in.

Revision ID: 0012_required_password_rotation
Revises: 0011_supply_demand_network
Create Date: 2026-10-03
"""

import sqlalchemy as sa

from alembic import op

revision: str = "0012_required_password_rotation"
down_revision: str = "0011_supply_demand_network"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_change_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("users", "password_change_required", server_default=None)

    # Force staff and administrative accounts created before this release to rotate
    # their password before accessing any protected application route.
    op.execute("UPDATE users SET password_change_required = TRUE " "WHERE role::text <> 'FARMER'")


def downgrade() -> None:
    op.drop_column("users", "password_change_required")
