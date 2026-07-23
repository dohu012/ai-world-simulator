"""Objective fact and subjective belief contracts."""

from typing import Self

from pydantic import model_validator

from app.domain.common import (
    CharacterId,
    DomainModel,
    EventId,
    FactId,
    JSONValue,
    NonEmptyString,
    PositiveInt,
    SchemaVersion,
    Timestamp,
    UnitFloat,
    WorldId,
)
from app.domain.enums import BeliefSourceType, FactVisibility


class WorldFact(DomainModel):
    """An objective proposition in world state, independent of any agent belief."""

    id: FactId
    world_id: WorldId
    subject: NonEmptyString
    predicate: NonEmptyString
    object: JSONValue
    valid_from: Timestamp
    valid_until: Timestamp | None
    visibility: FactVisibility
    source_event_id: EventId | None
    version: PositiveInt
    schema_version: SchemaVersion
    created_at: Timestamp

    @model_validator(mode="after")
    def valid_interval(self) -> Self:
        """Reject an interval whose end precedes its start."""
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("valid_until must not be earlier than valid_from")
        return self


class AgentBelief(DomainModel):
    """A fallible subjective proposition held by one agent."""

    id: str
    world_id: WorldId
    agent_id: CharacterId
    subject: NonEmptyString
    predicate: NonEmptyString
    object: JSONValue
    confidence: UnitFloat
    source_type: BeliefSourceType
    source_id: str | None
    learned_at: Timestamp
    last_updated_at: Timestamp
    schema_version: SchemaVersion
