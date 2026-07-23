"""Shared primitives and validation configuration for domain contracts."""

from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]
type JSONObject = dict[str, JSONValue]
type SchemaVersion = Literal["1.0"]

type NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
type UnitFloat = Annotated[float, Field(ge=0.0, le=1.0)]
type PositiveFloat = Annotated[float, Field(gt=0.0)]
type NonNegativeFloat = Annotated[float, Field(ge=0.0)]
type PositiveInt = Annotated[int, Field(ge=1)]
type NonNegativeInt = Annotated[int, Field(ge=0)]
type Timestamp = AwareDatetime

type WorldId = str
type CharacterId = str
type EventId = str
type FactId = str
type ObservationId = str
type ActionId = str


class DomainModel(BaseModel):
    """Strict, transport-safe base configuration shared by all contracts."""

    model_config = ConfigDict(extra="forbid", strict=True)


class EntityReference(DomainModel):
    """A lightweight reference to a domain entity."""

    entity_type: NonEmptyString
    entity_id: NonEmptyString


class StateChange(DomainModel):
    """A single field-level change produced by world adjudication."""

    entity_type: NonEmptyString
    entity_id: NonEmptyString
    field: NonEmptyString
    old_value: JSONValue
    new_value: JSONValue
