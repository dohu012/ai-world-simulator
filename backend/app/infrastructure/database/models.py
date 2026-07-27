"""SQLAlchemy persistence models for the replayable world-state foundation."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class PayloadMixin:
    schema_version: Mapped[str] = mapped_column(String(16), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class WorldRecord(PayloadMixin, Base):
    __tablename__ = "worlds"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    current_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)


class CharacterRecord(PayloadMixin, Base):
    __tablename__ = "characters"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)


class LocationRecord(PayloadMixin, Base):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class LocationEdgeRecord(Base):
    __tablename__ = "location_edges"
    __table_args__ = (Index("ix_location_edges_world_from", "world_id", "from_location_id"),)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), primary_key=True
    )
    from_location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True
    )
    to_location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True
    )


class AgentProfileRecord(PayloadMixin, Base):
    __tablename__ = "agent_profiles"
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )


class WorldFactRecord(PayloadMixin, Base):
    __tablename__ = "world_facts"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    visibility: Mapped[str] = mapped_column(String(32), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_event_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)


class WorldEventRecord(PayloadMixin, Base):
    __tablename__ = "world_events"
    __table_args__ = (
        Index("ix_world_events_world_occurred", "world_id", "occurred_at", "id"),
        Index("ix_world_events_world_correlation", "world_id", "correlation_id"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    visibility: Mapped[str] = mapped_column(String(32), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_action_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)


class ObservationRecord(PayloadMixin, Base):
    __tablename__ = "observations"
    __table_args__ = (
        Index("ix_observations_world_agent_time", "world_id", "agent_id", "observed_at"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_event_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    source_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class AgentBeliefRecord(PayloadMixin, Base):
    __tablename__ = "agent_beliefs"
    __table_args__ = (
        Index("ix_agent_beliefs_world_agent_time", "world_id", "agent_id", "learned_at"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    learned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class OracleRequestRecord(PayloadMixin, Base):
    __tablename__ = "oracle_requests"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decision_correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)


class OracleResponseRecord(PayloadMixin, Base):
    __tablename__ = "oracle_responses"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    request_id: Mapped[str] = mapped_column(
        ForeignKey("oracle_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ActionIntentRecord(PayloadMixin, Base):
    __tablename__ = "action_intents"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)


class ActionResultRecord(PayloadMixin, Base):
    __tablename__ = "action_results"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_id: Mapped[str] = mapped_column(
        ForeignKey("action_intents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)


class PromptVersionRecord(Base):
    __tablename__ = "prompt_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    schema_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AgentDecisionRecord(Base):
    __tablename__ = "agent_decisions"
    __table_args__ = (
        UniqueConstraint("world_id", "agent_id", "idempotency_key", name="uq_decision_key"),
        Index("ix_agent_decisions_world_agent_created", "world_id", "agent_id", "created_at"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    claim_owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    claim_token: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    action_intent_id: Mapped[str | None] = mapped_column(
        ForeignKey("action_intents.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    input_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    outcome_payload: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ModelCallAttemptRecord(Base):
    __tablename__ = "model_call_attempts"
    __table_args__ = (
        UniqueConstraint("decision_id", "attempt_number", name="uq_model_attempt_number"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    decision_id: Mapped[str] = mapped_column(
        ForeignKey("agent_decisions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# Ensure TASK-017 tables are registered in shared metadata.
from app.infrastructure.database import runtime_models as runtime_models  # noqa: E402,F401
