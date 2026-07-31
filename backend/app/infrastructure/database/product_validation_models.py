"""Normalized TASK-023 study records; deliberately disconnected from world inputs."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class StudyProtocolRecord(Base):
    __tablename__ = "study_protocols"
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(16), nullable=False)
    sample_target: Mapped[int] = mapped_column(Integer, nullable=False)
    frozen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    enrollment_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    superseded_by: Mapped[str | None] = mapped_column(
        ForeignKey("study_protocols.id", ondelete="RESTRICT")
    )


class StudyParticipantRecord(Base):
    __tablename__ = "study_participants"
    __table_args__ = (
        UniqueConstraint("protocol_id", "opaque_code_hash", name="uq_study_participant_code"),
        CheckConstraint("sequence IN ('AB','BA')", name="ck_study_sequence"),
    )
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    protocol_id: Mapped[str] = mapped_column(
        ForeignKey("study_protocols.id", ondelete="RESTRICT"), nullable=False
    )
    opaque_code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    sequence: Mapped[str] = mapped_column(String(2), nullable=False)
    assignment_proof: Mapped[str] = mapped_column(String(64), nullable=False)
    device_class: Mapped[str] = mapped_column(String(24), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deletion_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StudyQuestionRecord(Base):
    __tablename__ = "study_questions"
    __table_args__ = (
        UniqueConstraint("protocol_id", "id", name="uq_study_protocol_question"),
        CheckConstraint(
            "scope IN ('participant','fictional_world','comprehension')",
            name="ck_study_question_scope",
        ),
    )
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    protocol_id: Mapped[str] = mapped_column(
        ForeignKey("study_protocols.id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    construct_code: Mapped[str] = mapped_column(String(32), nullable=False)
    scope: Mapped[str] = mapped_column(String(24), nullable=False)
    prompt: Mapped[str] = mapped_column(String(600), nullable=False)
    option_codes: Mapped[str] = mapped_column(String(256), nullable=False)
    correct_code: Mapped[str | None] = mapped_column(String(32))
    wording_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class StudyConsentRecord(Base):
    __tablename__ = "study_consents"
    __table_args__ = (
        UniqueConstraint("participant_id", "version", name="uq_study_consent_version"),
        CheckConstraint("status IN ('accepted','declined','withdrawn')", name="ck_consent_status"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("study_participants.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    wording_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    acknowledgement_codes: Mapped[str] = mapped_column(String(256), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class StudyPeriodRecord(Base):
    __tablename__ = "study_periods"
    __table_args__ = (
        UniqueConstraint("participant_id", "period", name="uq_study_participant_period"),
        CheckConstraint("period BETWEEN 1 AND 2", name="ck_study_period"),
        CheckConstraint("condition IN ('causal','chronological')", name="ck_study_condition"),
        Index("ix_study_period_protocol_state", "protocol_id", "completed_at"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    protocol_id: Mapped[str] = mapped_column(
        ForeignKey("study_protocols.id", ondelete="RESTRICT"), nullable=False
    )
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("study_participants.id", ondelete="CASCADE"), nullable=False
    )
    period: Mapped[int] = mapped_column(Integer, nullable=False)
    condition: Mapped[str] = mapped_column(String(16), nullable=False)
    interval_id: Mapped[str] = mapped_column(String(96), nullable=False)
    source_watermark: Mapped[str] = mapped_column(String(64), nullable=False)
    presentation_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    exposure_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StudyResponseRecord(Base):
    __tablename__ = "study_responses"
    __table_args__ = (
        UniqueConstraint("period_id", "question_id", "version", name="uq_study_response_version"),
        UniqueConstraint("participant_id", "idempotency_key", name="uq_study_response_key"),
        CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_study_rating"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("study_participants.id", ondelete="CASCADE"), nullable=False
    )
    period_id: Mapped[str] = mapped_column(
        ForeignKey("study_periods.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[str] = mapped_column(
        ForeignKey("study_questions.id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    option_code: Mapped[str | None] = mapped_column(String(32))
    rating: Mapped[int | None] = mapped_column(Integer)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    corrects_response_id: Mapped[str | None] = mapped_column(
        ForeignKey("study_responses.id", ondelete="CASCADE")
    )
    invalidated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class StudyDemandProbeRecord(Base):
    __tablename__ = "study_demand_probes"
    __table_args__ = (
        UniqueConstraint("participant_id", "probe_type", name="uq_study_probe"),
        CheckConstraint("effort_rating BETWEEN 1 AND 5", name="ck_study_probe_effort"),
    )
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("study_participants.id", ondelete="CASCADE"), nullable=False
    )
    probe_type: Mapped[str] = mapped_column(String(32), nullable=False)
    initiated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason_code: Mapped[str] = mapped_column(String(32), nullable=False)
    effort_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    first_choice_rank: Mapped[int] = mapped_column(Integer, nullable=False)


class StudyReportRecord(Base):
    __tablename__ = "study_reports"
    __table_args__ = (Index("ix_study_report_protocol_created", "protocol_id", "created_at"),)
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    protocol_id: Mapped[str] = mapped_column(
        ForeignKey("study_protocols.id", ondelete="RESTRICT"), nullable=False
    )
    dataset_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    input_watermark: Mapped[str] = mapped_column(String(64), nullable=False)
    included_count: Mapped[int] = mapped_column(Integer, nullable=False)
    excluded_count: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_count: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_class: Mapped[str] = mapped_column(String(24), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
