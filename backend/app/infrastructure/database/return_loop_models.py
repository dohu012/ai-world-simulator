"""Normalized persistence for owner-scoped return-loop projections."""

from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    text as sql_text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class NotificationPreferenceRecord(Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint(
            "world_id", "owner_id", "version", name="uq_notification_preference_version"
        ),
        Index(
            "uq_notification_preference_active",
            "world_id",
            "owner_id",
            unique=True,
            postgresql_where=sql_text("active"),
        ),
        CheckConstraint("inbox_daily_cap BETWEEN 0 AND 6", name="ck_inbox_daily_cap"),
        CheckConstraint("push_daily_cap BETWEEN 0 AND 2", name="ck_push_daily_cap"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="RESTRICT"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    in_site_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    quiet_start: Mapped[time] = mapped_column(Time, nullable=False)
    quiet_end: Mapped[time] = mapped_column(Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    inbox_daily_cap: Mapped[int] = mapped_column(Integer, nullable=False)
    push_daily_cap: Mapped[int] = mapped_column(Integer, nullable=False)
    paused_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    followed_agent_ids: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    enabled_categories: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OfflineIntervalRecord(Base):
    __tablename__ = "offline_intervals"
    __table_args__ = (
        UniqueConstraint("world_id", "owner_id", "logical_key", name="uq_offline_interval_logical"),
        CheckConstraint("ended_at > started_at", name="ck_offline_interval_time"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="RESTRICT"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    logical_key: Mapped[str] = mapped_column(String(200), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_watermark: Mapped[str] = mapped_column(String(64), nullable=False)
    preference_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OfflineSummaryRecord(Base):
    __tablename__ = "offline_summaries"
    __table_args__ = (
        UniqueConstraint(
            "world_id",
            "owner_id",
            "source_watermark",
            "compiler_version",
            name="uq_offline_summary_logical",
        ),
        Index("ix_offline_summary_owner_created", "world_id", "owner_id", "created_at"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    interval_id: Mapped[str] = mapped_column(
        ForeignKey("offline_intervals.id", ondelete="RESTRICT")
    )
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="RESTRICT"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    source_watermark: Mapped[str] = mapped_column(String(64), nullable=False)
    compiler_version: Mapped[str] = mapped_column(String(64), nullable=False)
    lifecycle: Mapped[str] = mapped_column(String(24), nullable=False)
    narrative: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OfflineSummaryClaimRecord(Base):
    __tablename__ = "offline_summary_claims"
    __table_args__ = (
        UniqueConstraint(
            "summary_id",
            "source_type",
            "source_id",
            "source_version",
            name="uq_summary_claim_source",
        ),
        Index("ix_summary_claim_source", "world_id", "owner_id", "source_type", "source_id"),
    )
    id: Mapped[str] = mapped_column(String(192), primary_key=True)
    summary_id: Mapped[str] = mapped_column(ForeignKey("offline_summaries.id", ondelete="RESTRICT"))
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="RESTRICT"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(160), nullable=False)
    source_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    epistemic_class: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    visible_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)


class InboxItemRecord(Base):
    __tablename__ = "inbox_items"
    __table_args__ = (
        UniqueConstraint("world_id", "owner_id", "logical_key", name="uq_inbox_item_logical"),
        Index("ix_inbox_owner_available", "world_id", "owner_id", "available_at", "id"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="RESTRICT"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    logical_key: Mapped[str] = mapped_column(String(256), nullable=False)
    summary_id: Mapped[str | None] = mapped_column(
        ForeignKey("offline_summaries.id", ondelete="RESTRICT")
    )
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    preview: Mapped[str] = mapped_column(String(240), nullable=False)
    lock_screen_body: Mapped[str] = mapped_column(String(160), nullable=False)
    fictional: Mapped[bool] = mapped_column(Boolean, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PlaytestEventRecord(Base):
    __tablename__ = "return_playtest_events"
    __table_args__ = (
        UniqueConstraint("world_id", "owner_id", "idempotency_key", name="uq_playtest_event_key"),
        Index("ix_playtest_event_owner_time", "world_id", "owner_id", "occurred_at"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    world_id: Mapped[str] = mapped_column(ForeignKey("worlds.id", ondelete="RESTRICT"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="RESTRICT"))
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    event_code: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
