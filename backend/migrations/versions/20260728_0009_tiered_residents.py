"""add tiered resident simulation state and schedule templates"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260728_0009"
down_revision: str | None = "20260728_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "schedule_templates",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tier", sa.String(8), nullable=False),
        sa.Column("due_minute", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("due_minute BETWEEN 0 AND 1439", name="ck_schedule_due_minute"),
        sa.CheckConstraint("version >= 1", name="ck_schedule_version"),
    )
    op.create_index("ix_schedule_templates_world_id", "schedule_templates", ["world_id"])
    op.create_table(
        "resident_simulation_state",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tier", sa.String(8), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("location_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("schedule_template_id", sa.String(128), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_resident_version"),
    )
    op.create_index(
        "ix_resident_simulation_state_world_id", "resident_simulation_state", ["world_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_resident_simulation_state_world_id", table_name="resident_simulation_state")
    op.drop_table("resident_simulation_state")
    op.drop_index("ix_schedule_templates_world_id", table_name="schedule_templates")
    op.drop_table("schedule_templates")
