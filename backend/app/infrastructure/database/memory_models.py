"""Normalized auditable memory, embedding-job, and retrieval-trace tables."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class MemoryItemRecord(Base):
    __tablename__ = "memory_items"
    __table_args__ = (
        UniqueConstraint(
            "world_id", "owner_id", "logical_key", "policy_version", name="uq_memory_logical"
        ),
        CheckConstraint("admission_score BETWEEN 0 AND 1", name="ck_memory_admission_score"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_memory_confidence"),
        Index(
            "ix_memory_owner_time_type",
            "world_id",
            "owner_id",
            "occurred_at",
            "memory_type",
        ),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    world_id: Mapped[str] = mapped_column(
        ForeignKey("worlds.id", ondelete="RESTRICT"), nullable=False
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT"), nullable=False
    )
    logical_key: Mapped[str] = mapped_column(String(128), nullable=False)
    memory_type: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    admission_score: Mapped[float] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    policy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    supersedes_id: Mapped[str | None] = mapped_column(
        ForeignKey("memory_items.id", ondelete="RESTRICT")
    )
    tombstoned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MemorySourceRecord(Base):
    __tablename__ = "memory_sources"
    __table_args__ = (
        UniqueConstraint("memory_id", "source_type", "source_id", name="uq_memory_source"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memory_items.id", ondelete="RESTRICT"), nullable=False
    )
    world_id: Mapped[str] = mapped_column(String(128), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)


class MemoryEmbeddingRecord(Base):
    __tablename__ = "memory_embeddings"
    __table_args__ = (
        UniqueConstraint(
            "memory_id", "model_revision", "content_hash", name="uq_memory_embedding_revision"
        ),
        CheckConstraint("dimensions > 0 AND dimensions <= 4096", name="ck_embedding_dimensions"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memory_items.id", ondelete="RESTRICT"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    model_revision: Mapped[str] = mapped_column(String(128), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    vector: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metrics: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MemoryEmbeddingJobRecord(Base):
    __tablename__ = "memory_embedding_jobs"
    __table_args__ = (
        UniqueConstraint("memory_id", "model_revision", name="uq_embedding_job"),
        Index("ix_embedding_jobs_claim", "status", "retry_at", "lease_expires_at"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memory_items.id", ondelete="RESTRICT"), nullable=False
    )
    model_revision: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    claim_owner: Mapped[str | None] = mapped_column(String(128))
    claim_token: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_code: Mapped[str | None] = mapped_column(String(64))


class MemoryRetrievalRunRecord(Base):
    __tablename__ = "memory_retrieval_runs"
    __table_args__ = (
        UniqueConstraint("decision_id", "context_watermark", name="uq_retrieval_decision_context"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    decision_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_decisions.id", ondelete="RESTRICT")
    )
    world_id: Mapped[str] = mapped_column(String(128), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(128), nullable=False)
    cutoff: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_revision: Mapped[str | None] = mapped_column(String(128))
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    context_watermark: Mapped[str] = mapped_column(String(64), nullable=False)
    token_budget: Mapped[int] = mapped_column(Integer, nullable=False)
    token_used: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MemoryRetrievalCandidateRecord(Base):
    __tablename__ = "memory_retrieval_candidates"
    __table_args__ = (
        UniqueConstraint("retrieval_id", "memory_id", name="uq_retrieval_candidate"),
        CheckConstraint("rank > 0", name="ck_retrieval_candidate_rank"),
    )
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    retrieval_id: Mapped[str] = mapped_column(
        ForeignKey("memory_retrieval_runs.id", ondelete="RESTRICT"), nullable=False
    )
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memory_items.id", ondelete="RESTRICT"), nullable=False
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    exclusion_reason: Mapped[str] = mapped_column(String(32), nullable=False)
    score_components: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
