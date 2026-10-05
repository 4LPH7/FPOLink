"""FPO operations to-do list.

Revision ID: 0013_fpo_tasks
Revises: 0012_required_password_rotation
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0013_fpo_tasks"
down_revision: str = "0012_required_password_rotation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fpo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fpos.id"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="todo"),
        sa.Column("priority", sa.String(10), nullable=False, server_default="medium"),
        sa.Column("category", sa.String(30), nullable=False, server_default="general"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column(
            "farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id"), nullable=True
        ),
        sa.Column(
            "harvest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("harvests.id"), nullable=True
        ),
        sa.Column(
            "assigned_to_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_fpo_id", "tasks", ["fpo_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])


def downgrade() -> None:
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_fpo_id", table_name="tasks")
    op.drop_table("tasks")
