"""Canonical public imports and registry for domain contracts."""

from app.domain.actions import ActionIntent, ActionResult
from app.domain.character import AgentProfile, Character
from app.domain.common import DomainModel
from app.domain.events import WorldEvent
from app.domain.evolution import (
    EvolutionEvidence,
    IdentityBaseline,
    IdentitySnapshot,
    RelationshipSnapshot,
)
from app.domain.facts import AgentBelief, WorldFact
from app.domain.memory import (
    EmotionalMemory,
    EpisodicMemory,
    OracleMemory,
    SemanticMemory,
    StageSummaryMemory,
)
from app.domain.observation import Observation
from app.domain.oracle import OracleRequest, OracleResponse
from app.domain.return_loop import CausalClaim, OfflineSummary
from app.domain.seven_day import (
    AdjudicationRecord,
    AgentGoal,
    AgentPlan,
    ConditionalWorldEvent,
    ResourceAccount,
    ResourceDefinition,
    ResourceLedgerEntry,
)
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
    "resource-definition": ResourceDefinition,
    "resource-account": ResourceAccount,
    "resource-ledger-entry": ResourceLedgerEntry,
    "agent-goal": AgentGoal,
    "agent-plan": AgentPlan,
    "conditional-world-event": ConditionalWorldEvent,
    "adjudication-record": AdjudicationRecord,
    "episodic-memory": EpisodicMemory,
    "semantic-memory": SemanticMemory,
    "emotional-memory": EmotionalMemory,
    "oracle-memory": OracleMemory,
    "stage-summary-memory": StageSummaryMemory,
    "identity-baseline": IdentityBaseline,
    "identity-snapshot": IdentitySnapshot,
    "relationship-snapshot": RelationshipSnapshot,
    "evolution-evidence": EvolutionEvidence,
    "causal-claim": CausalClaim,
    "offline-summary": OfflineSummary,
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
