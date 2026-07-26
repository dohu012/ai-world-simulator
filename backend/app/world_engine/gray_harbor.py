"""Authoritative deterministic Gray Harbor adjudication."""

from dataclasses import dataclass

from app.application.action_validator import ActionValidation, MoveState
from app.domain.common import StateChange
from app.domain.enums import ActionStatus, ActionType, EventType, FactVisibility
from app.domain.schemas import ActionIntent, ActionResult, Character, World, WorldEvent


@dataclass(frozen=True)
class MoveMutationPlan:
    character: Character
    world: World


@dataclass(frozen=True)
class Adjudication:
    result: ActionResult
    event: WorldEvent | None = None
    mutation: MoveMutationPlan | None = None


class GrayHarborWorldEngine:
    """Create results and typed mutation plans without persistence access."""

    def adjudicate(
        self,
        intent: ActionIntent,
        validation: ActionValidation,
        state: MoveState | None = None,
    ) -> Adjudication:
        result_id = intent.id.replace("intent-", "result-", 1)
        if not validation.accepted:
            return Adjudication(self._result(intent, result_id, ActionStatus.REJECTED, validation))
        if intent.action_type is ActionType.MOVE:
            if state is None or validation.move is None or state.actor.location_id is None:
                raise ValueError("accepted move requires validated state")
            old_location = state.actor.location_id
            target = validation.move.target_location_id
            character = state.actor.model_copy(
                update={
                    "location_id": target,
                    "version": state.actor.version + 1,
                    "updated_at": state.world.current_time,
                }
            )
            world = state.world.model_copy(
                update={"version": state.world.version + 1, "updated_at": state.world.current_time}
            )
            witnesses = sorted({intent.actor_id, *state.destination_witness_ids})
            event_id = intent.id.replace("intent-", "event-", 1)
            event = WorldEvent(
                id=event_id,
                world_id=intent.world_id,
                event_type=EventType.MOVEMENT,
                title=f"{state.actor.name} moves",
                description=f"{state.actor.name} arrived at {target}.",
                occurred_at=intent.submitted_at,
                location_id=target,
                participant_ids=witnesses,
                fact_ids=[],
                source_action_id=intent.id,
                visibility=FactVisibility.RESTRICTED,
                correlation_id=intent.correlation_id,
                metadata={
                    "engine": "gray-harbor-deterministic-v1",
                    "action": "move",
                    "from_location_id": old_location,
                    "actor_id": intent.actor_id,
                },
                schema_version=intent.schema_version,
                created_at=intent.submitted_at,
            )
            changes = [
                StateChange(
                    entity_type="character",
                    entity_id=state.actor.id,
                    field="location_id",
                    old_value=old_location,
                    new_value=target,
                ),
                StateChange(
                    entity_type="character",
                    entity_id=state.actor.id,
                    field="version",
                    old_value=state.actor.version,
                    new_value=character.version,
                ),
                StateChange(
                    entity_type="world",
                    entity_id=state.world.id,
                    field="version",
                    old_value=state.world.version,
                    new_value=world.version,
                ),
            ]
            result = self._result(
                intent,
                result_id,
                ActionStatus.SUCCEEDED,
                validation,
                changes,
                [event.id],
                witnesses,
            )
            return Adjudication(result, event, MoveMutationPlan(character, world))

        event_id = intent.id.replace("intent-", "event-", 1)
        event = WorldEvent(
            id=event_id,
            world_id=intent.world_id,
            event_type=EventType.STATE_CHANGED,
            title="Agent waits and observes",
            description="The agent remains in place and waits for new information.",
            occurred_at=intent.submitted_at,
            location_id=None,
            participant_ids=[intent.actor_id],
            fact_ids=[],
            source_action_id=intent.id,
            visibility=FactVisibility.PRIVATE,
            correlation_id=intent.correlation_id,
            metadata={"engine": "gray-harbor-deterministic-v1", "action": "wait"},
            schema_version=intent.schema_version,
            created_at=intent.submitted_at,
        )
        return Adjudication(
            self._result(intent, result_id, ActionStatus.SUCCEEDED, validation, events=[event.id]),
            event,
        )

    @staticmethod
    def _result(
        intent: ActionIntent,
        result_id: str,
        status: ActionStatus,
        validation: ActionValidation,
        changes: list[StateChange] | None = None,
        events: list[str] | None = None,
        witnesses: list[str] | None = None,
    ) -> ActionResult:
        return ActionResult(
            id=result_id,
            world_id=intent.world_id,
            action_id=intent.id,
            actor_id=intent.actor_id,
            status=status,
            started_at=intent.submitted_at,
            completed_at=intent.submitted_at,
            failure_code=validation.failure_code,
            failure_reason=validation.failure_reason,
            state_changes=changes or [],
            generated_event_ids=events or [],
            witness_character_ids=witnesses or [intent.actor_id],
            correlation_id=intent.correlation_id,
            schema_version=intent.schema_version,
        )
