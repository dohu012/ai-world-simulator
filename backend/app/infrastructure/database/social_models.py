"""Normalized Task 18 communication, belief, and dialogue tables."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class CommunicationChannelRecord(Base):
    __tablename__ = "communication_channels"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    delay_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    reliability_milli: Mapped[int] = mapped_column(Integer, nullable=False)
    distortion_policy_id: Mapped[str] = mapped_column(String(64), nullable=False)
    privacy_class: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class MessageRecord(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id: Mapped[str | None] = mapped_column(ForeignKey("characters.id", ondelete="SET NULL"))
    content_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    body: Mapped[str] = mapped_column(String(1000), nullable=False)
    claims: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    sent_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TransmissionRecord(Base):
    __tablename__ = "transmissions"
    __table_args__ = (
        UniqueConstraint("delivery_key", name="uq_transmission_delivery_key"),
        Index(
            "ix_transmissions_due_order",
            "world_id",
            "status",
            "arrival_world_time",
            "priority",
            "created_at",
            "id",
        ),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    delivery_key: Mapped[str] = mapped_column(String(180), nullable=False)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    channel_id: Mapped[str] = mapped_column(
        ForeignKey("communication_channels.id", ondelete="RESTRICT"), nullable=False
    )
    sender_id: Mapped[str | None] = mapped_column(ForeignKey("characters.id", ondelete="SET NULL"))
    recipient_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    sent_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arrival_world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    claim_owner: Mapped[str | None] = mapped_column(String(128))
    claim_token: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_observation_id: Mapped[str | None] = mapped_column(
        ForeignKey("observations.id", ondelete="SET NULL"), unique=True
    )
    delivered_wake_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_wakes.id", ondelete="SET NULL"), unique=True
    )
    failure_code: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class BeliefEvidenceRecord(Base):
    __tablename__ = "belief_evidence"
    __table_args__ = (
        UniqueConstraint(
            "agent_id", "proposition_key", "observation_id", name="uq_belief_evidence_observation"
        ),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    proposition_key: Mapped[str] = mapped_column(String(128), nullable=False)
    observation_id: Mapped[str] = mapped_column(
        ForeignKey("observations.id", ondelete="CASCADE"), nullable=False
    )
    causal_source_key: Mapped[str] = mapped_column(String(160), nullable=False)
    stance: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    reliability_milli: Mapped[int] = mapped_column(Integer, nullable=False)
    world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class BeliefRevisionRecord(Base):
    __tablename__ = "belief_revisions"
    __table_args__ = (
        UniqueConstraint(
            "agent_id", "proposition_key", "revision", name="uq_belief_revision_number"
        ),
        Index("ix_belief_revisions_current", "world_id", "agent_id", "proposition_key", "revision"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    proposition_key: Mapped[str] = mapped_column(String(128), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    prior_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("belief_revisions.id", ondelete="RESTRICT")
    )
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("belief_evidence.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence_milli: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(32), nullable=False)
    causal_source_keys: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ConversationRecord(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    participant_ids: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    current_speaker_id: Mapped[str | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL")
    )
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_turns: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    used_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=1200)
    world_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latest_transmission_id: Mapped[str | None] = mapped_column(
        ForeignKey("transmissions.id", ondelete="SET NULL")
    )
    terminal_reason: Mapped[str | None] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
