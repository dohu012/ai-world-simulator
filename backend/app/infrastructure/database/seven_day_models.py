"""Normalized TASK-019 persistence records."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ResourceDefinitionRecord(Base):
    __tablename__ = "resource_definitions"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    resource_type: Mapped[str] = mapped_column(String(64))
    unit: Mapped[str] = mapped_column(String(32))
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class ResourceAccountRecord(Base):
    __tablename__ = "resource_accounts"
    __table_args__ = (
        CheckConstraint(
            "available >= 0 AND reserved >= 0 AND consumed >= 0", name="ck_resource_nonnegative"
        ),
        CheckConstraint(
            "capacity IS NULL OR available + reserved <= capacity", name="ck_resource_capacity"
        ),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    resource_id: Mapped[str] = mapped_column(ForeignKey("resource_definitions.id"))
    holder_kind: Mapped[str] = mapped_column(String(32))
    holder_id: Mapped[str] = mapped_column(String(128))
    available: Mapped[int] = mapped_column(Integer)
    reserved: Mapped[int] = mapped_column(Integer)
    consumed: Mapped[int] = mapped_column(Integer)
    capacity: Mapped[int | None] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class ResourceLedgerRecord(Base):
    __tablename__ = "resource_ledger"
    __table_args__ = (
        UniqueConstraint("world_id", "idempotency_key", name="uq_resource_ledger_key"),
        CheckConstraint("amount > 0", name="ck_resource_ledger_amount"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"))
    resource_id: Mapped[str] = mapped_column(ForeignKey("resource_definitions.id"))
    idempotency_key: Mapped[str] = mapped_column(String(160))
    operation: Mapped[str] = mapped_column(String(32))
    amount: Mapped[int] = mapped_column(Integer)
    world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class AgentGoalRecord(Base):
    __tablename__ = "agent_goals"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(32))
    priority: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class AgentPlanRecord(Base):
    __tablename__ = "agent_plans"
    __table_args__ = (
        CheckConstraint("replan_count BETWEEN 0 AND 2", name="ck_plan_replans"),
        CheckConstraint("retry_count BETWEEN 0 AND 3", name="ck_plan_retries"),
        Index("ix_agent_plans_due", "world_id", "status", "deadline_world_time"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"))
    goal_id: Mapped[str] = mapped_column(ForeignKey("agent_goals.id", ondelete="CASCADE"))
    slot: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    deadline_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    replan_count: Mapped[int] = mapped_column(Integer)
    retry_count: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer)
    fencing_token: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class ConditionalEventRecord(Base):
    __tablename__ = "conditional_world_events"
    __table_args__ = (UniqueConstraint("world_id", "idempotency_key", name="uq_condition_key"),)
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(32))
    deadline_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class AdjudicationTraceRecord(Base):
    __tablename__ = "adjudication_traces"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    action_id: Mapped[str] = mapped_column(
        ForeignKey("action_intents.id", ondelete="CASCADE"), unique=True
    )
    seed_hash: Mapped[str] = mapped_column(String(64))
    roll_basis_points: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)


class ScenarioCheckpointRecord(Base):
    __tablename__ = "scenario_checkpoints"
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), primary_key=True
    )
    scenario_version: Mapped[str] = mapped_column(String(32))
    current_day: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32))
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)
    __table_args__ = (
        CheckConstraint("current_day BETWEEN 0 AND 7", name="ck_scenario_day"),
        CheckConstraint("version >= 1", name="ck_scenario_version"),
    )


class ResidentSimulationRecord(Base):
    __tablename__ = "resident_simulation_state"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    tier: Mapped[str] = mapped_column(String(8))
    role: Mapped[str] = mapped_column(String(64))
    location_id: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    schedule_template_id: Mapped[str] = mapped_column(String(128))
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)
    __table_args__ = (CheckConstraint("version >= 1", name="ck_resident_version"),)


class ScheduleTemplateRecord(Base):
    __tablename__ = "schedule_templates"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), index=True)
    tier: Mapped[str] = mapped_column(String(8))
    due_minute: Mapped[int] = mapped_column(Integer)
    priority: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)
    __table_args__ = (
        CheckConstraint("due_minute BETWEEN 0 AND 1439", name="ck_schedule_due_minute"),
        CheckConstraint("version >= 1", name="ck_schedule_version"),
    )
