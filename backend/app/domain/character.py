"""Character and agent-profile contracts."""

from typing import Annotated

from pydantic import Field

from app.domain.common import (
    CharacterId,
    DomainModel,
    JSONObject,
    NonEmptyString,
    NonNegativeInt,
    PositiveInt,
    SchemaVersion,
    Timestamp,
    UnitFloat,
    WorldId,
)
from app.domain.enums import CharacterStatus

type OptionalNonEmptyString = Annotated[str, Field(min_length=1)]


class Character(DomainModel):
    """Objective character data; beliefs and private memories live elsewhere."""

    id: CharacterId
    world_id: WorldId
    name: NonEmptyString
    description: str
    location_id: OptionalNonEmptyString | None
    occupation: str | None
    age: NonNegativeInt | None
    status: CharacterStatus
    is_special_agent: bool
    health: UnitFloat
    resources: JSONObject
    version: PositiveInt
    schema_version: SchemaVersion
    created_at: Timestamp
    updated_at: Timestamp


class AgentProfile(DomainModel):
    """Stable decision configuration for a special character."""

    character_id: CharacterId
    persona_summary: NonEmptyString
    traits: dict[str, UnitFloat]
    values: dict[str, UnitFloat]
    desires: list[str]
    fears: list[str]
    taboos: list[str]
    abilities: list[str]
    decision_biases: dict[str, UnitFloat]
    oracle_relationship: JSONObject
    wake_policy: JSONObject
    schema_version: SchemaVersion
