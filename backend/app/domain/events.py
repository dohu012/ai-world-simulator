"""World event contract."""

from app.domain.common import (
    ActionId,
    CharacterId,
    DomainModel,
    FactId,
    JSONObject,
    NonEmptyString,
    SchemaVersion,
    Timestamp,
    WorldId,
)
from app.domain.enums import EventType, FactVisibility


class WorldEvent(DomainModel):
    """An occurrence that has happened in the objective world."""

    id: str
    world_id: WorldId
    event_type: EventType
    title: NonEmptyString
    description: str
    occurred_at: Timestamp
    location_id: str | None
    participant_ids: list[CharacterId]
    fact_ids: list[FactId]
    source_action_id: ActionId | None
    visibility: FactVisibility
    correlation_id: str
    metadata: JSONObject
    schema_version: SchemaVersion
    created_at: Timestamp
