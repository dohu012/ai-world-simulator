"""Action intent and adjudicated result contracts."""

from typing import Self

from pydantic import model_validator

from app.domain.common import (
    ActionId,
    CharacterId,
    DomainModel,
    EventId,
    JSONObject,
    NonEmptyString,
    NonNegativeFloat,
    SchemaVersion,
    StateChange,
    Timestamp,
    WorldId,
)
from app.domain.enums import ActionStatus, ActionType


class ActionIntent(DomainModel):
    """An agent's request to attempt an action; it makes no success claim."""

    id: ActionId
    world_id: WorldId
    actor_id: CharacterId
    action_type: ActionType
    parameters: JSONObject
    reason_summary: NonEmptyString
    submitted_at: Timestamp
    expected_duration: NonNegativeFloat | None
    correlation_id: str
    schema_version: SchemaVersion


class ActionResult(DomainModel):
    """The world adjudicator's outcome for an action intent."""

    id: str
    world_id: WorldId
    action_id: ActionId
    actor_id: CharacterId
    status: ActionStatus
    started_at: Timestamp
    completed_at: Timestamp | None
    failure_code: str | None
    failure_reason: str | None
    state_changes: list[StateChange]
    generated_event_ids: list[EventId]
    witness_character_ids: list[CharacterId]
    correlation_id: str
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def coherent_outcome(self) -> Self:
        """Keep completion time and success failure details coherent."""
        if self.completed_at is not None and self.completed_at < self.started_at:
            raise ValueError("completed_at must not be earlier than started_at")
        if self.status is ActionStatus.SUCCEEDED and (
            self.failure_code is not None or self.failure_reason is not None
        ):
            raise ValueError("a succeeded action cannot contain failure details")
        return self
