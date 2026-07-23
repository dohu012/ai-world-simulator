"""Oracle request and response contracts."""

from typing import Self

from pydantic import model_validator

from app.domain.common import (
    CharacterId,
    DomainModel,
    NonEmptyString,
    SchemaVersion,
    Timestamp,
    UnitFloat,
    WorldId,
)
from app.domain.enums import OracleRequestStatus


class OracleRequest(DomainModel):
    """An agent's request for player-provided information."""

    id: str
    world_id: WorldId
    agent_id: CharacterId
    question: NonEmptyString
    context_summary: str
    requested_at: Timestamp
    world_deadline: Timestamp | None
    real_deadline: Timestamp | None
    status: OracleRequestStatus
    decision_correlation_id: str
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def deadlines_follow_request(self) -> Self:
        """Reject deadlines that precede creation of the request."""
        if self.world_deadline is not None and self.world_deadline < self.requested_at:
            raise ValueError("world_deadline must not be earlier than requested_at")
        if self.real_deadline is not None and self.real_deadline < self.requested_at:
            raise ValueError("real_deadline must not be earlier than requested_at")
        return self


class OracleResponse(DomainModel):
    """Player-provided information that may later become an observation."""

    id: str
    request_id: str
    world_id: WorldId
    agent_id: CharacterId
    content: NonEmptyString
    clarity: UnitFloat
    responded_at: Timestamp
    schema_version: SchemaVersion
