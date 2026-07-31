"""Bounded, auditable fictional identity and directional relationship evolution."""

from __future__ import annotations

import math
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from app.domain.common import DomainModel, NonEmptyString, SchemaVersion, Timestamp

EVOLUTION_POLICY_VERSION = "evolution-policy-v1"
SUMMARY_POLICY_VERSION = "evolution-summary-v1"
Scalar = Annotated[float, Field(ge=-1.0, le=1.0, allow_inf_nan=False)]
Confidence = Annotated[float, Field(ge=0.0, le=1.0, allow_inf_nan=False)]
Summary = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=600)]

IDENTITY_EVENT_CAP = 0.08
IDENTITY_CUMULATIVE_CAP = 0.30
RELATIONSHIP_EVENT_CAP = 0.15
RELATIONSHIP_DAY_CAP = 0.30
DEPENDENCE_CAP = 0.45
MIN_IDENTITY_EVIDENCE = 2


class TargetType(StrEnum):
    AGENT = "agent"
    ORACLE = "oracle"


class EvidenceRole(StrEnum):
    DIRECT_INTERACTION = "direct_interaction"
    REPORTED_INTERACTION = "reported_interaction"
    OUTCOME = "outcome"
    REPEATED_PATTERN = "repeated_pattern"
    CONTRADICTION = "contradiction"
    REFLECTION = "reflection"
    ORACLE_EVENT = "oracle_event"


class Dimension(StrEnum):
    CAUTION = "caution"
    COMPASSION = "compassion"
    CONFIDENCE = "confidence"
    SELF_RELIANCE = "self_reliance"
    TRUST = "trust"
    AFFECTION = "affection"
    RESPECT = "respect"
    FEAR = "fear"
    RESENTMENT = "resentment"
    GRATITUDE = "gratitude"
    DEPENDENCE = "dependence"
    FAMILIARITY = "familiarity"


DecisionReason = Literal[
    "ACCEPTED",
    "OWNER_MISMATCH",
    "WORLD_MISMATCH",
    "AGENT_MISMATCH",
    "FUTURE_EVIDENCE",
    "INVISIBLE_EVIDENCE",
    "DUPLICATE_EVIDENCE",
    "INSUFFICIENT_EVIDENCE",
    "UNKNOWN_EVIDENCE",
    "DIMENSION_NOT_ALLOWED",
    "EVENT_CAP",
    "DAY_CAP",
    "CUMULATIVE_CAP",
    "DEPENDENCE_CAP",
    "STALE_WATERMARK",
]


IDENTITY_DIMENSIONS = {
    Dimension.CAUTION,
    Dimension.COMPASSION,
    Dimension.CONFIDENCE,
    Dimension.SELF_RELIANCE,
}
RELATIONSHIP_DIMENSIONS = set(Dimension) - IDENTITY_DIMENSIONS


class IdentityBaseline(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    agent_id: NonEmptyString
    generation: int = Field(ge=1)
    traits: dict[str, Scalar] = Field(max_length=32)
    values: dict[str, int] = Field(max_length=32)
    protected_values: set[NonEmptyString] = Field(default_factory=set, max_length=32)
    desires: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    fears: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    taboos: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    persona_summary: Summary
    source_references: list[NonEmptyString] = Field(min_length=1, max_length=32)
    created_at: Timestamp
    content_hash: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def validate_baseline(self) -> IdentityBaseline:
        if not self.protected_values <= self.values.keys():
            raise ValueError("protected values must exist in values")
        return self


class IdentitySnapshot(DomainModel):
    id: NonEmptyString
    baseline_id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    agent_id: NonEmptyString
    version: int = Field(ge=1)
    offsets: dict[Dimension, Scalar] = Field(default_factory=dict, max_length=16)
    confidence: Confidence
    persona_summary: Summary
    evidence_horizon: Timestamp
    policy_version: Literal["evolution-policy-v1"] = "evolution-policy-v1"
    previous_snapshot_id: str | None = None
    lifecycle: Literal["active", "superseded", "reverted", "invalidated"] = "active"
    content_hash: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def identity_dimensions_only(self) -> IdentitySnapshot:
        if any(key not in IDENTITY_DIMENSIONS for key in self.offsets):
            raise ValueError("relationship dimension in identity snapshot")
        if any(abs(value) > IDENTITY_CUMULATIVE_CAP for value in self.offsets.values()):
            raise ValueError("identity cumulative cap exceeded")
        return self


class RelationshipSnapshot(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    subject_agent_id: NonEmptyString
    target_type: TargetType
    target_id: NonEmptyString
    version: int = Field(ge=1)
    dimensions: dict[Dimension, Scalar] = Field(default_factory=dict, max_length=16)
    uncertainty: Confidence
    interpretation: Summary
    evidence_horizon: Timestamp
    policy_version: Literal["evolution-policy-v1"] = "evolution-policy-v1"
    previous_snapshot_id: str | None = None
    content_hash: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def validate_edge(self) -> RelationshipSnapshot:
        if self.target_type is TargetType.AGENT and self.subject_agent_id == self.target_id:
            raise ValueError("self relationship is forbidden")
        if any(key not in RELATIONSHIP_DIMENSIONS for key in self.dimensions):
            raise ValueError("identity dimension in relationship snapshot")
        if self.dimensions.get(Dimension.DEPENDENCE, 0.0) > DEPENDENCE_CAP:
            raise ValueError("dependence safety cap exceeded")
        return self


class EvolutionEvidence(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    agent_id: NonEmptyString
    source_type: Literal["observation", "memory", "action_result"]
    source_id: NonEmptyString
    occurred_at: Timestamp
    visible_from: Timestamp
    role: EvidenceRole
    independent_key: NonEmptyString
    summary: Summary
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def time_order(self) -> EvolutionEvidence:
        if self.visible_from < self.occurred_at:
            raise ValueError("evidence visible before occurrence")
        return self


class ProposedDelta(DomainModel):
    dimension: Dimension
    magnitude: float
    confidence: float
    evidence_ids: list[NonEmptyString] = Field(min_length=1, max_length=16)
    rationale: Summary

    @model_validator(mode="after")
    def finite_numbers(self) -> ProposedDelta:
        if not math.isfinite(self.magnitude) or not math.isfinite(self.confidence):
            raise ValueError("non-finite proposal")
        return self


class DeltaDecision(DomainModel):
    dimension: Dimension
    accepted: bool
    applied_magnitude: float
    reason: DecisionReason


def canonical_hash(parts: list[str]) -> str:
    return sha256("\x1f".join(parts).encode()).hexdigest()


def evidence_watermark(evidence: list[EvolutionEvidence]) -> str:
    ordered = sorted(evidence, key=lambda item: item.id)
    return canonical_hash(
        [
            EVOLUTION_POLICY_VERSION,
            *(f"{item.id}:{item.visible_from.isoformat()}" for item in ordered),
        ]
    )


def validate_delta(
    proposal: ProposedDelta,
    *,
    evidence: list[EvolutionEvidence],
    world_id: str,
    owner_id: str,
    agent_id: str,
    cutoff: datetime,
    expected_watermark: str,
    current_value: float = 0.0,
    day_delta: float = 0.0,
    relationship: bool,
) -> DeltaDecision:
    """Code-owned per-dimension eligibility; model text has no authority."""
    by_id = {item.id: item for item in evidence}
    selected = [by_id[item] for item in proposal.evidence_ids if item in by_id]
    reason: DecisionReason = "ACCEPTED"
    if len(selected) != len(proposal.evidence_ids):
        reason = "UNKNOWN_EVIDENCE"
    elif any(item.world_id != world_id for item in selected):
        reason = "WORLD_MISMATCH"
    elif any(item.owner_id != owner_id for item in selected):
        reason = "OWNER_MISMATCH"
    elif any(item.agent_id != agent_id for item in selected):
        reason = "AGENT_MISMATCH"
    elif any(item.occurred_at > cutoff for item in selected):
        reason = "FUTURE_EVIDENCE"
    elif any(item.visible_from > cutoff for item in selected):
        reason = "INVISIBLE_EVIDENCE"
    elif len({item.independent_key for item in selected}) != len(selected):
        reason = "DUPLICATE_EVIDENCE"
    elif evidence_watermark(evidence) != expected_watermark:
        reason = "STALE_WATERMARK"
    elif relationship and proposal.dimension not in RELATIONSHIP_DIMENSIONS:
        reason = "DIMENSION_NOT_ALLOWED"
    elif not relationship and proposal.dimension not in IDENTITY_DIMENSIONS:
        reason = "DIMENSION_NOT_ALLOWED"
    elif not relationship and len(selected) < MIN_IDENTITY_EVIDENCE:
        reason = "INSUFFICIENT_EVIDENCE"
    else:
        cap = RELATIONSHIP_EVENT_CAP if relationship else IDENTITY_EVENT_CAP
        if abs(proposal.magnitude) > cap:
            reason = "EVENT_CAP"
        elif relationship and abs(day_delta + proposal.magnitude) > RELATIONSHIP_DAY_CAP:
            reason = "DAY_CAP"
        elif not relationship and abs(current_value + proposal.magnitude) > IDENTITY_CUMULATIVE_CAP:
            reason = "CUMULATIVE_CAP"
        elif (
            relationship
            and proposal.dimension is Dimension.DEPENDENCE
            and current_value + proposal.magnitude > DEPENDENCE_CAP
        ):
            reason = "DEPENDENCE_CAP"
    return DeltaDecision(
        dimension=proposal.dimension,
        accepted=reason == "ACCEPTED",
        applied_magnitude=round(proposal.magnitude, 6) if reason == "ACCEPTED" else 0.0,
        reason=reason,
    )


def oracle_deltas(
    *,
    replied: bool,
    urgent: bool,
    advice_quality: Literal["sound", "poor", "unknown"],
    outcome: Literal["good", "bad", "unknown"],
    choice: Literal["followed", "partial", "rejected"],
    value_conflict: bool,
    contact_possible: bool = True,
) -> dict[Dimension, float]:
    """Deterministic fallback separates advice, outcome, autonomy and silence."""
    result: dict[Dimension, float] = {}
    if not replied:
        if urgent and contact_possible:
            result[Dimension.TRUST] = -0.04
        return result
    result[Dimension.FAMILIARITY] = 0.03
    if advice_quality == "sound":
        result[Dimension.RESPECT] = 0.06
    elif advice_quality == "poor":
        result[Dimension.TRUST] = -0.06
    if value_conflict:
        result[Dimension.RESENTMENT] = 0.05
        result[Dimension.TRUST] = result.get(Dimension.TRUST, 0.0) - 0.03
    if choice == "rejected" and advice_quality == "sound":
        result[Dimension.GRATITUDE] = 0.03
    elif choice == "followed":
        result[Dimension.DEPENDENCE] = 0.02
    if outcome == "good":
        result[Dimension.GRATITUDE] = result.get(Dimension.GRATITUDE, 0.0) + 0.02
    elif outcome == "bad":
        result[Dimension.FEAR] = 0.02
    return {key: round(value, 6) for key, value in result.items()}
