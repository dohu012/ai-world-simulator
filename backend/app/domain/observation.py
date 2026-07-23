"""Agent-scoped observation contracts."""

from app.domain.common import (
    CharacterId,
    DomainModel,
    EntityReference,
    EventId,
    JSONObject,
    NonEmptyString,
    ObservationId,
    SchemaVersion,
    Timestamp,
    UnitFloat,
    WorldId,
)
from app.domain.enums import ActionType, ObservationType


class ObservedEntity(DomainModel):
    """A partial entity view visible to the observing agent."""

    entity: EntityReference
    name: NonEmptyString
    description: str | None
    attributes: JSONObject


class HeardStatement(DomainModel):
    """A statement heard by the agent, without asserting its truth."""

    speaker_id: CharacterId | None
    content: NonEmptyString


class ReceivedMessage(DomainModel):
    """A message delivered to the agent."""

    message_id: str
    sender_id: CharacterId | None
    content: NonEmptyString
    sent_at: Timestamp


class FeltChange(DomainModel):
    """A local, possibly imprecise sensation of change."""

    description: NonEmptyString
    intensity: UnitFloat


class AvailableAction(DomainModel):
    """An action affordance exposed to the agent, not an action result."""

    action_type: ActionType
    description: NonEmptyString
    parameter_hints: JSONObject


class Observation(DomainModel):
    """Only the local information made available to a particular agent."""

    id: ObservationId
    world_id: WorldId
    agent_id: CharacterId
    observed_at: Timestamp
    observation_type: ObservationType
    source_event_id: EventId | None
    source_message_id: str | None
    visible_entities: list[ObservedEntity]
    heard_statements: list[HeardStatement]
    received_messages: list[ReceivedMessage]
    felt_changes: list[FeltChange]
    available_actions: list[AvailableAction]
    metadata: JSONObject
    schema_version: SchemaVersion
