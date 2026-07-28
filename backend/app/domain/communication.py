"""Strict contracts and deterministic policies for causal social information."""

from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChannelKind(StrEnum):
    DIRECT = "direct"
    OFFICIAL_BULLETIN = "official_bulletin"
    COURIER = "courier"
    LOCAL_RUMOR = "local_rumor"


class ClaimStance(StrEnum):
    OBSERVED = "observed"
    HEARD = "heard"
    UNCERTAIN = "uncertain"
    DENIED = "denied"
    CORRECTED = "corrected"


class TransmissionStatus(StrEnum):
    SCHEDULED = "scheduled"
    CLAIMED = "claimed"
    DELIVERED = "delivered"
    RETRYABLE_FAILED = "retryable_failed"
    TERMINAL_FAILED = "terminal_failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BeliefStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    CONFLICTED = "conflicted"


class ConversationState(StrEnum):
    OPENING = "opening"
    ACTIVE = "active"
    AWAITING_DELIVERY = "awaiting_delivery"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAULTED = "faulted"


class CommunicationChannel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    version: int = Field(ge=1)
    kind: ChannelKind
    delay_minutes: int = Field(ge=0, le=1440)
    reliability: float = Field(ge=0, le=1)
    distortion_policy_id: str
    privacy_class: str
    max_payload_chars: int = Field(ge=1, le=2000)
    valid_from: datetime
    valid_until: datetime | None = None

    def arrival(self, sent_at: datetime) -> datetime:
        return sent_at + timedelta(minutes=self.delay_minutes)


class MessageClaim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    proposition_key: str
    stance: ClaimStance
    value: str = Field(min_length=1, max_length=500)
    attribution: str = Field(min_length=1, max_length=160)
    causal_source_key: str = Field(min_length=1, max_length=160)


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    world_id: str
    sender_id: str | None
    content_kind: str
    body: str = Field(min_length=1, max_length=1000)
    claims: list[MessageClaim] = Field(min_length=1, max_length=4)
    sent_at: datetime
    correlation_id: str
    schema_version: str = "1.0"


class Transmission(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    delivery_key: str
    world_id: str
    message_id: str
    channel_id: str
    sender_id: str | None
    recipient_id: str
    sent_world_time: datetime
    arrival_world_time: datetime
    priority: int = Field(ge=0, le=1000)
    status: TransmissionStatus = TransmissionStatus.SCHEDULED


class BeliefProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    proposition_key: str
    value: str
    confidence: float = Field(ge=0, le=1)
    status: BeliefStatus
    reason_code: str
    causal_source_keys: list[str]


class ConversationBudget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    max_turns: int = Field(default=3, ge=1, le=3)
    used_turns: int = Field(default=0, ge=0)
    max_tokens: int = Field(default=1200, ge=1, le=4000)
    used_tokens: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def within_budget(self) -> "ConversationBudget":
        if self.used_turns > self.max_turns or self.used_tokens > self.max_tokens:
            raise ValueError("conversation budget exceeded")
        return self


class RoutePlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    recipient_id: str
    channel: CommunicationChannel
    claim: MessageClaim
    body: str
    priority: int


def stable_route_order(
    transmissions: list[Transmission],
) -> list[Transmission]:
    """Total order independent from worker/database enumeration order."""
    return sorted(
        transmissions,
        key=lambda item: (
            item.arrival_world_time,
            item.priority,
            item.id,
        ),
    )


def revise_belief(
    prior: BeliefProjection | None,
    claim: MessageClaim,
    *,
    reliability: float,
) -> BeliefProjection:
    """Append-only projection rule; callers persist evidence before this result."""
    reliability = max(0.0, min(1.0, reliability))
    if prior is None:
        return BeliefProjection(
            proposition_key=claim.proposition_key,
            value=claim.value,
            confidence=reliability,
            status=BeliefStatus.ACTIVE,
            reason_code="INITIAL_EVIDENCE",
            causal_source_keys=[claim.causal_source_key],
        )
    if claim.causal_source_key in prior.causal_source_keys:
        return prior.model_copy(update={"reason_code": "BELIEF_EVIDENCE_DUPLICATE"})
    sources = [*prior.causal_source_keys, claim.causal_source_key]
    if prior.value == claim.value:
        confidence = min(0.99, prior.confidence + reliability * (1 - prior.confidence) * 0.5)
        return prior.model_copy(
            update={
                "confidence": confidence,
                "status": BeliefStatus.ACTIVE,
                "reason_code": "INDEPENDENT_CORROBORATION",
                "causal_source_keys": sources,
            }
        )
    if claim.stance is ClaimStance.CORRECTED and reliability > prior.confidence:
        return BeliefProjection(
            proposition_key=claim.proposition_key,
            value=claim.value,
            confidence=reliability,
            status=BeliefStatus.ACTIVE,
            reason_code="HIGHER_RELIABILITY_CORRECTION",
            causal_source_keys=sources,
        )
    return prior.model_copy(
        update={
            "confidence": max(prior.confidence, reliability),
            "status": BeliefStatus.CONFLICTED,
            "reason_code": "CONFLICTING_EVIDENCE",
            "causal_source_keys": sources,
        }
    )
