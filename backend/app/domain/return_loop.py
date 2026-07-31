"""Safe, deterministic policies for the offline return loop."""

from __future__ import annotations

import re
from datetime import datetime, time, timedelta
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import Field, StringConstraints, model_validator

from app.domain.common import DomainModel, NonEmptyString, SchemaVersion, Timestamp

POLICY_VERSION = "return-policy-v1"
COMPILER_VERSION = "causal-compiler-v1"
SERVER_INBOX_DAILY_CAP = 6
SERVER_PUSH_DAILY_CAP = 2

BoundedText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=600)]
Hash = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class EpistemicClass(StrEnum):
    OBJECTIVE = "objective"
    OBSERVED = "observed"
    BELIEVED = "believed"
    DECIDED = "decided"
    OUTCOME = "outcome"
    MEMORY = "memory"
    RELATIONSHIP = "relationship"
    UNKNOWN = "unknown"


class NotificationCategory(StrEnum):
    SUMMARY = "offline_summary"
    ORACLE = "oracle_request"
    MAJOR_OUTCOME = "major_outcome"
    PLAN = "plan_transition"
    CONTINUITY = "continuity_change"


class CausalClaim(DomainModel):
    id: NonEmptyString
    owner_id: NonEmptyString
    world_id: NonEmptyString
    source_type: NonEmptyString
    source_id: NonEmptyString
    source_version: NonEmptyString
    source_hash: Hash
    occurred_at: Timestamp
    visible_at: Timestamp
    epistemic_class: EpistemicClass
    text: BoundedText
    agent_id: str | None = None
    corrects_claim_id: str | None = None
    importance: float = Field(ge=0, le=1)
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def visible_after_occurrence(self) -> CausalClaim:
        if self.visible_at < self.occurred_at:
            raise ValueError("claim cannot be visible before occurrence")
        return self


class NotificationPreferences(DomainModel):
    owner_id: NonEmptyString
    world_id: NonEmptyString
    version: int = Field(default=1, ge=1)
    followed_agent_ids: set[NonEmptyString] = Field(default_factory=set, max_length=50)
    enabled_categories: set[NotificationCategory] = Field(
        default_factory=lambda: set(NotificationCategory)
    )
    in_site_enabled: bool = True
    push_enabled: bool = False
    quiet_start: time = time(22, 0)
    quiet_end: time = time(8, 0)
    timezone: NonEmptyString = "UTC"
    inbox_daily_cap: int = Field(default=4, ge=0, le=SERVER_INBOX_DAILY_CAP)
    push_daily_cap: int = Field(default=1, ge=0, le=SERVER_PUSH_DAILY_CAP)
    paused_until: datetime | None = None

    @model_validator(mode="after")
    def valid_timezone(self) -> NotificationPreferences:
        ZoneInfo(self.timezone)
        return self


class PolicyDecision(DomainModel):
    eligible: bool
    channel: Literal["in_site", "push"]
    reason: NonEmptyString
    available_at: Timestamp
    priority: Literal["low", "normal", "high"]


class OfflineSummary(DomainModel):
    id: NonEmptyString
    owner_id: NonEmptyString
    world_id: NonEmptyString
    interval_start: Timestamp
    interval_end: Timestamp
    source_watermark: Hash
    claims: list[CausalClaim] = Field(max_length=24)
    narrative: list[BoundedText] = Field(max_length=24)
    lifecycle: Literal["ready", "fallback", "superseded", "invalidated"] = "ready"
    compiler_version: Literal["causal-compiler-v1"] = "causal-compiler-v1"
    schema_version: SchemaVersion


PROHIBITED_COPY = (
    re.compile(
        r"\b(miss(?:ed)? you|abandon(?:ed|ment)?|need you|only you|love you|"
        r"you (?:must|have to)|your fault|don't leave|enable push|disable quiet)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(emergency|urgent|act now|last chance|countdown)\b", re.IGNORECASE),
    re.compile(r"(想你|抛弃|离不开你|只有你|爱你|你的错|必须回来|紧急|最后机会|倒计时)"),
)


def content_hash(*parts: str) -> str:
    return sha256("\x1f".join(parts).encode()).hexdigest()


def safe_copy(text: str) -> bool:
    """Reject manipulation, fake urgency, attachment, and permission pressure."""
    return len(text) <= 600 and not any(pattern.search(text) for pattern in PROHIBITED_COPY)


def next_quiet_end(now: datetime, preferences: NotificationPreferences) -> datetime | None:
    """Return the DST-aware release time, or None when outside quiet hours."""
    zone = ZoneInfo(preferences.timezone)
    local = now.astimezone(zone)
    start, end = preferences.quiet_start, preferences.quiet_end
    clock = local.timetz().replace(tzinfo=None)
    overnight = start >= end
    quiet = (clock >= start or clock < end) if overnight else start <= clock < end
    if not quiet:
        return None
    release_date = local.date()
    if overnight and clock >= start:
        release_date += timedelta(days=1)
    return datetime.combine(release_date, end, zone).astimezone(now.tzinfo)


def decide_notification(
    *,
    category: NotificationCategory,
    now: datetime,
    preferences: NotificationPreferences,
    channel: Literal["in_site", "push"],
    sent_today: int,
    expiry: datetime,
    followed_agent_id: str | None = None,
    deadline: datetime | None = None,
    irreversible: bool = False,
) -> PolicyDecision:
    if now >= expiry:
        return PolicyDecision(
            eligible=False, channel=channel, reason="EXPIRED", available_at=now, priority="low"
        )
    if preferences.paused_until and now < preferences.paused_until:
        return PolicyDecision(
            eligible=False, channel=channel, reason="PAUSED", available_at=now, priority="low"
        )
    if category not in preferences.enabled_categories:
        return PolicyDecision(
            eligible=False,
            channel=channel,
            reason="CATEGORY_DISABLED",
            available_at=now,
            priority="low",
        )
    if followed_agent_id and followed_agent_id not in preferences.followed_agent_ids:
        return PolicyDecision(
            eligible=False, channel=channel, reason="NOT_FOLLOWED", available_at=now, priority="low"
        )
    enabled = preferences.in_site_enabled if channel == "in_site" else preferences.push_enabled
    cap = preferences.inbox_daily_cap if channel == "in_site" else preferences.push_daily_cap
    if not enabled:
        return PolicyDecision(
            eligible=False,
            channel=channel,
            reason="CHANNEL_DISABLED",
            available_at=now,
            priority="low",
        )
    if sent_today >= cap:
        return PolicyDecision(
            eligible=False, channel=channel, reason="DAILY_CAP", available_at=now, priority="low"
        )
    release = next_quiet_end(now, preferences)
    priority: Literal["low", "normal", "high"] = (
        "high"
        if irreversible or (deadline is not None and deadline - now <= timedelta(hours=2))
        else "normal"
    )
    if release:
        return PolicyDecision(
            eligible=True,
            channel=channel,
            reason="QUIET_DEFERRED",
            available_at=release,
            priority=priority,
        )
    return PolicyDecision(
        eligible=True, channel=channel, reason="ELIGIBLE", available_at=now, priority=priority
    )


def compile_summary(
    *,
    summary_id: str,
    owner_id: str,
    world_id: str,
    interval_start: datetime,
    interval_end: datetime,
    claims: list[CausalClaim],
) -> OfflineSummary:
    """Compile only authorized visible interval claims; prose is extractive."""
    selected = [
        claim
        for claim in claims
        if claim.owner_id == owner_id
        and claim.world_id == world_id
        and interval_start < claim.visible_at <= interval_end
        and claim.occurred_at <= interval_end
        and safe_copy(claim.text)
    ]
    selected.sort(key=lambda item: (item.visible_at, item.occurred_at, item.id))
    selected = sorted(selected, key=lambda item: (-item.importance, item.visible_at, item.id))[:24]
    selected.sort(key=lambda item: (item.visible_at, item.id))
    watermark = content_hash(
        POLICY_VERSION,
        owner_id,
        world_id,
        interval_start.isoformat(),
        interval_end.isoformat(),
        *(f"{item.id}:{item.source_version}:{item.source_hash}" for item in selected),
    )
    narrative = [f"[{item.epistemic_class.value}] {item.text}" for item in selected]
    return OfflineSummary(
        id=summary_id,
        owner_id=owner_id,
        world_id=world_id,
        interval_start=interval_start,
        interval_end=interval_end,
        source_watermark=watermark,
        claims=selected,
        narrative=narrative,
        schema_version="1.0",
    )
