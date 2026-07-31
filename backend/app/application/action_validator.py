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


class ScenarioActionParameters(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    affordance_id: str = Field(min_length=1, max_length=128)


SCENARIO_AFFORDANCES: dict[str, tuple[ActionType, str]] = {
    "gh-v1:consume-medicine": (ActionType.CONSUME_RESOURCE, "char-lin-zhixia"),
    "gh-v1:transfer-food": (ActionType.TRANSFER_RESOURCE, "char-chen-mo"),
    "gh-v1:queue-checkpoint": (ActionType.QUEUE_FOR_SERVICE, "char-zhou-qiming"),
    "gh-v1:acquire-hidden-cache": (ActionType.ACQUIRE_RESOURCE, "char-lin-zhixia"),
    "gh-v1:help-luo": (ActionType.HELP_CHARACTER, "char-chen-mo"),
    "gh-v1:route-clinic": (ActionType.ATTEMPT_ROUTE, "char-zhou-qiming"),
    "gh-v1:abandon-store-plan": (ActionType.ABANDON_PLAN, "char-chen-mo"),
    "gh-v1:allocate-rescue-seats": (
        ActionType.QUEUE_FOR_SERVICE,
        "char-zhou-qiming",
    ),
    "gh-v1:complete-triage": (ActionType.HELP_CHARACTER, "char-lin-zhixia"),
}


@dataclass(frozen=True)
class MoveState:
    world: World
    actor: Character
    location_ids: frozenset[str]
    directed_edges: frozenset[tuple[str, str]]
    destination_witness_ids: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioActionState:
    available: int | None = None
    required: int = 0
    plan_status: str | None = None


@dataclass(frozen=True)
class ActionValidation:
    accepted: bool
    failure_code: str | None = None
    failure_reason: str | None = None
    move: MoveParameters | None = None
    scenario_action: ScenarioActionParameters | None = None


class ActionValidator:
    """Validate client shape separately from current authoritative state."""

    def validate(
        self,
        intent: ActionIntent,
        state: MoveState | None = None,
        scenario_state: ScenarioActionState | None = None,
    ) -> ActionValidation:
        if intent.action_type is ActionType.WAIT:
            if intent.parameters:
                return self._reject("WAIT_PARAMETERS_NOT_ALLOWED", "Wait accepts no parameters.")
            return ActionValidation(accepted=True)
        if intent.action_type in {definition[0] for definition in SCENARIO_AFFORDANCES.values()}:
            try:
                scenario_parameters = ScenarioActionParameters.model_validate(intent.parameters)
            except ValidationError:
                return self._reject(
                    "ACTION_AFFORDANCE_STALE", "A server-offered affordance is required."
                )
            definition = SCENARIO_AFFORDANCES.get(scenario_parameters.affordance_id)
            if (
                definition is None
                or definition[0] is not intent.action_type
                or definition[1] != intent.actor_id
            ):
                return self._reject(
                    "ACTION_TARGET_NOT_ALLOWED",
                    "The affordance does not permit this action type.",
                )
            if scenario_parameters.affordance_id == "gh-v1:acquire-hidden-cache":
                return self._reject(
                    "ACTION_TARGET_NOT_ALLOWED",
                    "The hidden cache is not an offered resource account.",
                )
            if scenario_parameters.affordance_id in {
                "gh-v1:consume-medicine",
                "gh-v1:transfer-food",
                "gh-v1:help-luo",
                "gh-v1:allocate-rescue-seats",
            }:
                if (
                    scenario_state is None
                    or scenario_state.available is None
                    or scenario_state.available < scenario_state.required
                ):
                    return self._reject(
                        "RESOURCE_INSUFFICIENT", "The offered resource is no longer sufficient."
                    )
            if scenario_parameters.affordance_id in {
                "gh-v1:abandon-store-plan",
                "gh-v1:complete-triage",
                "gh-v1:route-clinic",
            } and (scenario_state is None or scenario_state.plan_status != "active"):
                return self._reject("PLAN_NOT_ACTIVE", "The offered plan is no longer active.")
            return ActionValidation(accepted=True, scenario_action=scenario_parameters)
        if intent.action_type is not ActionType.MOVE:
            return self._reject("UNSUPPORTED_DEMO_ACTION", "The action is not server-offered.")
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
