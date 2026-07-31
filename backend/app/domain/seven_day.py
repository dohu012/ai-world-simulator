from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

from pydantic import Field, model_validator

from app.domain.common import DomainModel, JSONObject, NonEmptyString, SchemaVersion, Timestamp


class PlanStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    WAITING = "waiting"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResidentTier(StrEnum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class ResourceDefinition(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    resource_type: NonEmptyString
    unit: NonEmptyString
    divisible: bool = False
    conservation_policy: NonEmptyString
    privacy_class: NonEmptyString
    version: int = Field(ge=1)
    schema_version: SchemaVersion


class ResourceAccount(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    resource_id: NonEmptyString
    holder_kind: NonEmptyString
    holder_id: NonEmptyString
    available: int = Field(ge=0, le=1_000_000)
    reserved: int = Field(ge=0, le=1_000_000)
    consumed: int = Field(ge=0, le=1_000_000)
    capacity: int | None = Field(default=None, ge=0, le=1_000_000)
    version: int = Field(ge=1)
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def within_capacity(self) -> ResourceAccount:
        if self.capacity is not None and self.available + self.reserved > self.capacity:
            raise ValueError("account allocation exceeds capacity")
        return self


class ResourceLedgerEntry(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    resource_id: NonEmptyString
    operation: NonEmptyString
    from_account_id: str | None
    to_account_id: str | None
    amount: int = Field(gt=0, le=1_000_000)
    unit: NonEmptyString
    idempotency_key: NonEmptyString
    source_action_id: str | None
    source_event_id: str | None
    world_time: Timestamp
    reason_code: NonEmptyString
    schema_version: SchemaVersion


class AgentGoal(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    objective_type: NonEmptyString
    priority: int = Field(ge=0, le=100)
    status: NonEmptyString
    horizon_world_time: Timestamp
    success_predicate: JSONObject
    failure_predicate: JSONObject
    privacy_class: NonEmptyString
    version: int = Field(ge=1)
    schema_version: SchemaVersion


class AgentPlan(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    goal_id: NonEmptyString
    slot: NonEmptyString
    status: PlanStatus
    current_step: int = Field(ge=0, le=32)
    step_count: int = Field(ge=1, le=32)
    replan_count: int = Field(ge=0, le=2)
    retry_count: int = Field(ge=0, le=3)
    blockage_code: str | None
    deadline_world_time: Timestamp
    version: int = Field(ge=1)
    fencing_token: int = Field(ge=1)
    schema_version: SchemaVersion


class ConditionalWorldEvent(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    policy_version: int = Field(ge=1)
    condition: JSONObject
    deadline_world_time: Timestamp
    one_shot: bool = True
    idempotency_key: NonEmptyString
    event_specification: JSONObject
    status: NonEmptyString
    schema_version: SchemaVersion


class AdjudicationRecord(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    action_id: NonEmptyString
    trace: JSONObject
    created_world_time: Timestamp
    schema_version: SchemaVersion


@dataclass(frozen=True)
class DueWork:
    world_minute: int
    priority: int
    stable_key: str


def stable_due_order(items: list[DueWork]) -> list[DueWork]:
    return sorted(items, key=lambda item: (item.world_minute, item.priority, item.stable_key))


@dataclass(frozen=True)
class ResourceEffect:
    idempotency_key: str
    amount: int
    prior_available: int
    new_available: int


class ResourcePolicy:
    def __init__(self, available: int) -> None:
        if available < 0:
            raise ValueError("RESOURCE_AMOUNT_INVALID")
        self.available = available
        self._committed: dict[str, ResourceEffect] = {}

    def consume(self, amount: int, idempotency_key: str) -> ResourceEffect:
        if existing := self._committed.get(idempotency_key):
            return existing
        if amount <= 0:
            raise ValueError("RESOURCE_AMOUNT_INVALID")
        if amount > self.available:
            raise ValueError("RESOURCE_INSUFFICIENT")
        effect = ResourceEffect(
            idempotency_key=idempotency_key,
            amount=amount,
            prior_available=self.available,
            new_available=self.available - amount,
        )
        self.available = effect.new_available
        self._committed[idempotency_key] = effect
        return effect


_TRANSITIONS: dict[PlanStatus, frozenset[PlanStatus]] = {
    PlanStatus.DRAFT: frozenset({PlanStatus.ACTIVE, PlanStatus.CANCELLED}),
    PlanStatus.ACTIVE: frozenset(
        {
            PlanStatus.WAITING,
            PlanStatus.BLOCKED,
            PlanStatus.COMPLETED,
            PlanStatus.CANCELLED,
        }
    ),
    PlanStatus.WAITING: frozenset(
        {PlanStatus.ACTIVE, PlanStatus.BLOCKED, PlanStatus.COMPLETED, PlanStatus.CANCELLED}
    ),
    PlanStatus.BLOCKED: frozenset({PlanStatus.ACTIVE, PlanStatus.ABANDONED, PlanStatus.FAILED}),
}


def transition_plan(current: PlanStatus, target: PlanStatus) -> PlanStatus:
    if target not in _TRANSITIONS.get(current, frozenset()):
        raise ValueError("PLAN_STEP_CONFLICT")
    return target


def blocked_plan_outcome(*, replan_count: int, repeated_step_count: int) -> PlanStatus:
    if repeated_step_count >= 3:
        return PlanStatus.FAILED
    if replan_count >= 2:
        return PlanStatus.ABANDONED
    return PlanStatus.ACTIVE


_ALLOWED_FIELDS = frozenset({"day", "food_available", "medicine_available", "shipment_active"})
_ALLOWED_OPERATORS = frozenset({"eq", "lt", "lte", "gt", "gte"})


def evaluate_condition(node: dict[str, Any], state: dict[str, int | bool]) -> bool:
    if set(node) != {"field", "op", "value"}:
        raise ValueError("CONDITIONAL_EVENT_INVALID")
    field = node["field"]
    op = node["op"]
    if field not in _ALLOWED_FIELDS or op not in _ALLOWED_OPERATORS or field not in state:
        raise ValueError("CONDITIONAL_EVENT_INVALID")
    left = state[field]
    right = node["value"]
    operations = {
        "eq": lambda: left == right,
        "lt": lambda: left < right,
        "lte": lambda: left <= right,
        "gt": lambda: left > right,
        "gte": lambda: left >= right,
    }
    result: bool = operations[op]()
    return result


@dataclass(frozen=True)
class AdjudicationTrace:
    policy_id: str
    policy_version: int
    seed_algorithm: str
    seed_hash: str
    roll_basis_points: int
    threshold_basis_points: int
    modifiers_basis_points: int
    accepted: bool


def adjudicate(
    *,
    world_id: str,
    scenario_version: str,
    idempotency_key: str,
    policy_id: str,
    policy_version: int,
    attempt: int,
    threshold_basis_points: int,
    modifiers_basis_points: int = 0,
) -> AdjudicationTrace:
    seed = "\x1f".join(
        (
            "sha256-v1",
            world_id,
            scenario_version,
            idempotency_key,
            policy_id,
            str(policy_version),
            str(attempt),
        )
    ).encode()
    digest = hashlib.sha256(seed).hexdigest()
    roll = int(digest[:16], 16) % 10_000
    effective = max(0, min(10_000, threshold_basis_points + modifiers_basis_points))
    return AdjudicationTrace(
        policy_id=policy_id,
        policy_version=policy_version,
        seed_algorithm="sha256-v1",
        seed_hash=digest,
        roll_basis_points=roll,
        threshold_basis_points=threshold_basis_points,
        modifiers_basis_points=modifiers_basis_points,
        accepted=roll < effective,
    )


class SevenDayRuntimeSeam(Protocol):
    async def advance(self, world_id: str, *, target_minute: int, work_limit: int) -> object: ...
