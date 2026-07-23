"""World contract."""

from app.domain.common import (
    DomainModel,
    NonEmptyString,
    PositiveFloat,
    PositiveInt,
    SchemaVersion,
    Timestamp,
    WorldId,
)
from app.domain.enums import WorldStatus


class World(DomainModel):
    """Objective top-level metadata and clock for one simulated world."""

    id: WorldId
    name: NonEmptyString
    description: str
    status: WorldStatus
    current_time: Timestamp
    time_scale: PositiveFloat
    version: PositiveInt
    schema_version: SchemaVersion
    created_at: Timestamp
    updated_at: Timestamp
