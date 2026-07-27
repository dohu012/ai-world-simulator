"""Normalized durable runtime persistence tables."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class WorldRuntimeRecord(Base):
    __tablename__ = "world_runtimes"
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="virtual")
    current_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    real_time_anchor: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    speed_milli: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    generation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    catch_up_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_code: Mapped[str | None] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ScheduledWorldEventRecord(Base):
    __tablename__ = "scheduled_world_events"
    __table_args__ = (
        UniqueConstraint("world_id", "idempotency_key", name="uq_scheduled_event_key"),
        Index(
            "ix_scheduled_events_due_order",
            "world_id",
            "status",
            "due_world_time",
            "priority",
            "created_at",
            "id",
        ),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    due_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    parameters: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    claim_owner: Mapped[str | None] = mapped_column(String(128))
    claim_token: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    published_event_id: Mapped[str | None] = mapped_column(
        ForeignKey("world_events.id", ondelete="SET NULL"), unique=True
    )
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    failure_code: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AgentWakeRecord(Base):
    __tablename__ = "agent_wakes"
    __table_args__ = (
        UniqueConstraint("world_id", "agent_id", "causal_key", name="uq_agent_wake_causal"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    causal_key: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(String(32), nullable=False)
    observation_ids: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OracleWindowRecord(Base):
    __tablename__ = "oracle_windows"
    __table_args__ = (
        UniqueConstraint(
            "world_id", "agent_id", "decision_correlation_id", name="uq_oracle_decision"
        ),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    request_id: Mapped[str] = mapped_column(
        ForeignKey("oracle_requests.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    decision_correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    world_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    real_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    outcome: Mapped[str | None] = mapped_column(String(32))
    response_id: Mapped[str | None] = mapped_column(
        ForeignKey("oracle_responses.id", ondelete="SET NULL"), unique=True
    )
    delivered_observation_id: Mapped[str | None] = mapped_column(
        ForeignKey("observations.id", ondelete="SET NULL"), unique=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    final_decision_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_decisions.id", ondelete="SET NULL"), unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class NotificationOutboxRecord(Base):
    __tablename__ = "notification_outbox"
    __table_args__ = (UniqueConstraint("dispatch_key", name="uq_notification_dispatch_key"),)
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    dispatch_key: Mapped[str] = mapped_column(String(160), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dispatched: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
