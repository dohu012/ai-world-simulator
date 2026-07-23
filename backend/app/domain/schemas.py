"""Canonical public imports and registry for domain contracts."""

from app.domain.actions import ActionIntent, ActionResult
from app.domain.character import AgentProfile, Character
from app.domain.common import DomainModel
from app.domain.events import WorldEvent
from app.domain.facts import AgentBelief, WorldFact
from app.domain.observation import Observation
from app.domain.oracle import OracleRequest, OracleResponse
from app.domain.world import World

DOMAIN_MODELS: dict[str, type[DomainModel]] = {
    "world": World,
    "character": Character,
    "agent-profile": AgentProfile,
    "world-fact": WorldFact,
    "agent-belief": AgentBelief,
    "observation": Observation,
    "action-intent": ActionIntent,
    "action-result": ActionResult,
    "world-event": WorldEvent,
    "oracle-request": OracleRequest,
    "oracle-response": OracleResponse,
}

__all__ = [
    "DOMAIN_MODELS",
    "ActionIntent",
    "ActionResult",
    "AgentBelief",
    "AgentProfile",
    "Character",
    "Observation",
    "OracleRequest",
    "OracleResponse",
    "World",
    "WorldEvent",
    "WorldFact",
]
