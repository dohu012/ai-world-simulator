"""Pure contracts for the durable Gray Harbor runtime.

Persistence adapters coordinate these rules; they never author world facts or action results.
"""

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RuntimeStatus(StrEnum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    FAULTED = "faulted"


class DeadlineWinner(StrEnum):
    REPLY = "reply"
    WORLD_TIMEOUT = "world_timeout"
    REAL_TIMEOUT = "real_timeout"
    WAITING = "waiting"


class WorldClock(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    world_id: str
    current_world_time: datetime
    status: RuntimeStatus = RuntimeStatus.STOPPED
    speed_milli: int = Field(default=1000, ge=1, le=100_000)
    version: int = Field(default=1, ge=1)
    generation: int = Field(default=0, ge=0)
    catch_up_limit: int = Field(default=25, ge=1, le=1000)

    def advance(self, delta: timedelta, *, expected_generation: int) -> "WorldClock":
        if expected_generation != self.generation:
            raise RuntimeGenerationConflict
        if self.status is RuntimeStatus.PAUSED:
            raise RuntimePaused
        if self.status is not RuntimeStatus.RUNNING:
            raise RuntimeNotRunning
        if delta < timedelta(0):
            raise WorldTimeRegression
        return self.model_copy(
            update={
                "current_world_time": self.current_world_time + delta,
                "version": self.version + 1,
            }
        )


class ScheduledItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    due_world_time: datetime
    priority: int = 100
    created_at: datetime


class OracleDeadline(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    world_deadline: datetime
    real_deadline: datetime

    @model_validator(mode="after")
    def aware(self) -> "OracleDeadline":
        if self.world_deadline.tzinfo is None or self.real_deadline.tzinfo is None:
            raise ValueError("deadlines must be timezone-aware")
        return self


class MajorDecisionAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    major_decision: bool
    seek_oracle: bool
    risk: str
    reversible: bool
    rationale_summary: str = Field(min_length=1, max_length=300)


class OraclePolicyContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    oracle_enabled: bool
    contact_available: bool
    cooldown_clear: bool
    budget_available: bool
    existing_open_window: bool


class OraclePolicyResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    eligible: bool
    rejection_code: str | None = None


class WorldRuntimePort(Protocol):
    async def activate(self, world_id: str, worker_id: str) -> WorldClock: ...
    async def advance(self, world_id: str, delta: timedelta, generation: int) -> WorldClock: ...


class RuntimeGenerationConflict(Exception):
    pass


class RuntimePaused(Exception):
    pass


class RuntimeNotRunning(Exception):
    pass


class WorldTimeRegression(Exception):
    pass


class AdvanceLimitExceeded(Exception):
    pass


def order_scheduled(items: list[ScheduledItem]) -> list[ScheduledItem]:
    return sorted(
        items, key=lambda item: (item.due_world_time, item.priority, item.created_at, item.id)
    )


def bounded_due(items: list[ScheduledItem], now: datetime, limit: int) -> list[ScheduledItem]:
    due = [item for item in order_scheduled(items) if item.due_world_time <= now]
    if len(due) > limit:
        raise AdvanceLimitExceeded
    return due


def deadline_winner(
    *,
    world_now: datetime,
    real_now: datetime,
    deadline: OracleDeadline,
    reply_at: datetime | None = None,
) -> DeadlineWinner:
    """First persisted instant wins; equal instants prefer an already accepted reply."""
    candidates = [
        (deadline.world_deadline, DeadlineWinner.WORLD_TIMEOUT),
        (deadline.real_deadline, DeadlineWinner.REAL_TIMEOUT),
    ]
    if reply_at is not None:
        candidates.append((reply_at, DeadlineWinner.REPLY))
    instant, winner = min(
        candidates,
        key=lambda value: (value[0], 0 if value[1] is DeadlineWinner.REPLY else 1, value[1].value),
    )
    if winner is DeadlineWinner.REPLY:
        return winner
    clock_now = world_now if winner is DeadlineWinner.WORLD_TIMEOUT else real_now
    return winner if clock_now >= instant else DeadlineWinner.WAITING


def evaluate_oracle(
    assessment: MajorDecisionAssessment, context: OraclePolicyContext
) -> OraclePolicyResult:
    checks = (
        (assessment.major_decision, "NOT_MAJOR"),
        (assessment.seek_oracle, "MODEL_DID_NOT_SEEK"),
        (
            assessment.risk in {"high", "critical"} or not assessment.reversible,
            "LOW_REVERSIBLE_RISK",
        ),
        (context.oracle_enabled, "ORACLE_DISABLED"),
        (context.contact_available, "CONTACT_UNAVAILABLE"),
        (context.cooldown_clear, "ORACLE_COOLDOWN"),
        (context.budget_available, "ORACLE_BUDGET_EXHAUSTED"),
        (not context.existing_open_window, "ORACLE_REQUEST_ALREADY_OPEN"),
    )
    for accepted, code in checks:
        if not accepted:
            return OraclePolicyResult(eligible=False, rejection_code=code)
    return OraclePolicyResult(eligible=True)


def should_wake(agent_id: str, observation_agent_id: str, reason: str) -> bool:
    return agent_id == observation_agent_id and reason in {
        "relevant_observation",
        "oracle_reply",
        "oracle_timeout",
        "action_completed",
        "action_failed",
    }
