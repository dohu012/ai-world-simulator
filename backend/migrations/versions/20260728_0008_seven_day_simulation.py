"""add seven-day resources plans conditions and adjudication"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260728_0008"
down_revision: str | None = "20260727_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def world_id() -> sa.Column[str]:
    return sa.Column(
        "world_id", sa.String(128), sa.ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )


def upgrade() -> None:
    op.create_table(
        "resource_definitions",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("unit", sa.String(32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_resource_definitions_world_id", "resource_definitions", ["world_id"])
    op.create_table(
        "resource_accounts",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column(
            "resource_id", sa.String(128), sa.ForeignKey("resource_definitions.id"), nullable=False
        ),
        sa.Column("holder_kind", sa.String(32), nullable=False),
        sa.Column("holder_id", sa.String(128), nullable=False),
        sa.Column("available", sa.Integer(), nullable=False),
        sa.Column("reserved", sa.Integer(), nullable=False),
        sa.Column("consumed", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer()),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint(
            "available >= 0 AND reserved >= 0 AND consumed >= 0",
            name="ck_resource_nonnegative",
        ),
        sa.CheckConstraint(
            "capacity IS NULL OR available + reserved <= capacity", name="ck_resource_capacity"
        ),
    )
    op.create_index("ix_resource_accounts_world_id", "resource_accounts", ["world_id"])
    op.create_table(
        "resource_ledger",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column(
            "resource_id", sa.String(128), sa.ForeignKey("resource_definitions.id"), nullable=False
        ),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("operation", sa.String(32), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint("world_id", "idempotency_key", name="uq_resource_ledger_key"),
        sa.CheckConstraint("amount > 0", name="ck_resource_ledger_amount"),
    )
    op.create_table(
        "agent_goals",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column(
            "owner_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_agent_goals_world_id", "agent_goals", ["world_id"])
    op.create_index("ix_agent_goals_owner_id", "agent_goals", ["owner_id"])
    op.create_table(
        "agent_plans",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column(
            "owner_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "goal_id",
            sa.String(128),
            sa.ForeignKey("agent_goals.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("slot", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("deadline_world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replan_count", sa.Integer(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("fencing_token", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("replan_count BETWEEN 0 AND 2", name="ck_plan_replans"),
        sa.CheckConstraint("retry_count BETWEEN 0 AND 3", name="ck_plan_retries"),
    )
    op.create_index(
        "ix_agent_plans_due", "agent_plans", ["world_id", "status", "deadline_world_time"]
    )
    op.create_table(
        "conditional_world_events",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("deadline_world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fired_at", sa.DateTime(timezone=True)),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint("world_id", "idempotency_key", name="uq_condition_key"),
    )
    op.create_index(
        "ix_conditional_world_events_world_id", "conditional_world_events", ["world_id"]
    )
    op.create_table(
        "adjudication_traces",
        sa.Column("id", sa.String(128), primary_key=True),
        world_id(),
        sa.Column(
            "action_id",
            sa.String(128),
            sa.ForeignKey("action_intents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("seed_hash", sa.String(64), nullable=False),
        sa.Column("roll_basis_points", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_adjudication_traces_world_id", "adjudication_traces", ["world_id"])
    op.create_table(
        "scenario_checkpoints",
        world_id(),
        sa.Column("scenario_version", sa.String(32), nullable=False),
        sa.Column("current_day", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("world_id"),
        sa.CheckConstraint("current_day BETWEEN 0 AND 7", name="ck_scenario_day"),
        sa.CheckConstraint("version >= 1", name="ck_scenario_version"),
    )


def downgrade() -> None:
    op.drop_table("scenario_checkpoints")
    op.drop_index("ix_adjudication_traces_world_id", table_name="adjudication_traces")
    op.drop_table("adjudication_traces")
    op.drop_index("ix_conditional_world_events_world_id", table_name="conditional_world_events")
    op.drop_table("conditional_world_events")
    op.drop_index("ix_agent_plans_due", table_name="agent_plans")
    op.drop_table("agent_plans")
    op.drop_index("ix_agent_goals_owner_id", table_name="agent_goals")
    op.drop_index("ix_agent_goals_world_id", table_name="agent_goals")
    op.drop_table("agent_goals")
    op.drop_table("resource_ledger")
    op.drop_index("ix_resource_accounts_world_id", table_name="resource_accounts")
    op.drop_table("resource_accounts")
    op.drop_index("ix_resource_definitions_world_id", table_name="resource_definitions")
    op.drop_table("resource_definitions")
