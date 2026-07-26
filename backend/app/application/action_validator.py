"""Pure shape and state-aware validation for deterministic demo actions."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.domain.enums import ActionType, CharacterStatus
from app.domain.schemas import ActionIntent, Character, World


class MoveParameters(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    target_location_id: str = Field(min_length=1)
    expected_character_version: int = Field(ge=1)
    expected_world_version: int = Field(ge=1)


@dataclass(frozen=True)
class MoveState:
    world: World
    actor: Character
    location_ids: frozenset[str]
    directed_edges: frozenset[tuple[str, str]]
    destination_witness_ids: tuple[str, ...]


@dataclass(frozen=True)
class ActionValidation:
    accepted: bool
    failure_code: str | None = None
    failure_reason: str | None = None
    move: MoveParameters | None = None


class ActionValidator:
    """Validate client shape separately from current authoritative state."""

    def validate(self, intent: ActionIntent, state: MoveState | None = None) -> ActionValidation:
        if intent.action_type is ActionType.WAIT:
            if intent.parameters:
                return self._reject("WAIT_PARAMETERS_NOT_ALLOWED", "Wait accepts no parameters.")
            return ActionValidation(accepted=True)
        if intent.action_type is not ActionType.MOVE:
            return self._reject("UNSUPPORTED_DEMO_ACTION", "The demo supports wait and move.")
        try:
            parameters = MoveParameters.model_validate(intent.parameters)
        except ValidationError:
            return self._reject(
                "MOVE_PARAMETERS_INVALID",
                "Move requires target_location_id and positive expected character/world versions.",
            )
        if state is None:
            return self._reject("ACTOR_LOCATION_UNKNOWN", "Move state is unavailable.")
        actor = state.actor
        if actor.status is not CharacterStatus.ACTIVE:
            return self._reject("ACTOR_NOT_ACTIVE", "The actor is not active.")
        if actor.location_id is None or actor.location_id not in state.location_ids:
            return self._reject("ACTOR_LOCATION_UNKNOWN", "The actor has no known world location.")
        if parameters.expected_character_version != actor.version:
            return self._reject("CHARACTER_VERSION_CONFLICT", "Character version is stale.")
        if parameters.expected_world_version != state.world.version:
            return self._reject("WORLD_VERSION_CONFLICT", "World version is stale.")
        if parameters.target_location_id not in state.location_ids:
            return self._reject("TARGET_LOCATION_NOT_FOUND", "Target is not in this world.")
        if parameters.target_location_id == actor.location_id:
            return self._reject("MOVE_SAME_LOCATION", "Actor is already at the target.")
        if (actor.location_id, parameters.target_location_id) not in state.directed_edges:
            return self._reject("MOVE_NOT_REACHABLE", "No directed edge reaches the target.")
        return ActionValidation(accepted=True, move=parameters)

    @staticmethod
    def _reject(code: str, reason: str) -> ActionValidation:
        return ActionValidation(accepted=False, failure_code=code, failure_reason=reason)
