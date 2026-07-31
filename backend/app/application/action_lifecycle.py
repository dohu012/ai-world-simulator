"""Transactional, idempotent Gray Harbor action lifecycle."""

from dataclasses import replace
from hashlib import sha256

from pydantic import BaseModel, ConfigDict, Field

from app.application.action_validator import ActionValidator, MoveState
from app.application.gray_harbor import (
    WORLD_ID,
    GrayHarborAgentNotFoundError,
    GrayHarborNotSeededError,
)
from app.application.observation_builder import ObservationBuilder
from app.domain.common import JSONObject
from app.domain.enums import ActionType
from app.domain.schemas import ActionIntent, ActionResult, WorldEvent
from app.repositories.worlds import (
    ActionLifecycleConflictError,
    WorldRepository,
    WorldTransactionError,
)
from app.world_engine.gray_harbor import GrayHarborWorldEngine


class ActionTransactionUnavailableError(Exception):
    """The authoritative transaction could not be completed safely."""


class DemoActionSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    idempotency_key: str = Field(min_length=1, max_length=64)
    action_type: ActionType
    parameters: JSONObject
    reason_summary: str = Field(min_length=1, max_length=500)


class DemoActionLifecycleReadModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    intent: ActionIntent
    result: ActionResult
    event: WorldEvent | None
    idempotent_replay: bool


class GrayHarborActionService:
    def __init__(
        self,
        repository: WorldRepository,
        validator: ActionValidator | None = None,
        engine: GrayHarborWorldEngine | None = None,
        observation_builder: ObservationBuilder | None = None,
    ) -> None:
        self.repository = repository
        self.validator = validator or ActionValidator()
        self.engine = engine or GrayHarborWorldEngine()
        self.observation_builder = observation_builder or ObservationBuilder()

    async def submit(
        self, agent_id: str, submission: DemoActionSubmission
    ) -> DemoActionLifecycleReadModel:
        digest = sha256(f"{WORLD_ID}:{agent_id}:{submission.idempotency_key}".encode()).hexdigest()[
            :20
        ]
        intent_id = f"intent-demo-{digest}"
        existing = await self.repository.get_action_lifecycle(intent_id)
        if existing is not None:
            return self._read(existing, True)

        observer = await self.repository.get_observer_world(WORLD_ID)
        if observer is None:
            raise GrayHarborNotSeededError
        if not any(character.id == agent_id for character in observer.characters):
            raise GrayHarborAgentNotFoundError(agent_id)
        intent = ActionIntent(
            id=intent_id,
            world_id=WORLD_ID,
            actor_id=agent_id,
            action_type=submission.action_type,
            parameters=submission.parameters,
            reason_summary=submission.reason_summary,
            submitted_at=observer.world.current_time,
            expected_duration=0.0,
            correlation_id=f"corr-demo-{digest}",
            schema_version=observer.world.schema_version,
        )
        state: MoveState | None = None
        scenario_state = None
        if intent.action_type is ActionType.MOVE:
            try:
                state = await self.repository.lock_move_state(WORLD_ID, agent_id)
            except WorldTransactionError as exc:
                raise ActionTransactionUnavailableError from exc
            if state is None:
                raise GrayHarborAgentNotFoundError(agent_id)
            concurrent = await self.repository.get_action_lifecycle(intent_id)
            if concurrent is not None:
                await self.repository.rollback()
                return self._read(concurrent, True)
        elif intent.action_type not in {ActionType.WAIT, ActionType.SPEAK, ActionType.CUSTOM}:
            affordance_id = intent.parameters.get("affordance_id")
            if isinstance(affordance_id, str):
                scenario_state = await self.repository.lock_scenario_action_state(affordance_id)

        validation = self.validator.validate(intent, state, scenario_state)
        if validation.accepted and validation.move is not None and state is not None:
            witnesses = await self.repository.destination_witness_ids(
                WORLD_ID, agent_id, validation.move.target_location_id
            )
            state = replace(state, destination_witness_ids=witnesses)
        adjudication = self.engine.adjudicate(intent, validation, state)
        observations = (
            self.observation_builder.build_for_events([adjudication.event], observer.characters)
            if adjudication.event is not None
            and (intent.action_type is ActionType.MOVE or validation.scenario_action is not None)
            else []
        )
        try:
            await self.repository.persist_action_lifecycle(
                intent, adjudication.result, adjudication.event, observations, adjudication.mutation
            )
        except ActionLifecycleConflictError:
            concurrent = await self.repository.get_action_lifecycle(intent_id)
            if concurrent is None:
                raise
            return self._read(concurrent, True)
        except WorldTransactionError as exc:
            raise ActionTransactionUnavailableError from exc
        return DemoActionLifecycleReadModel(
            intent=intent,
            result=adjudication.result,
            event=adjudication.event,
            idempotent_replay=False,
        )

    @staticmethod
    def _read(
        lifecycle: tuple[ActionIntent, ActionResult, WorldEvent | None], replay: bool
    ) -> DemoActionLifecycleReadModel:
        intent, result, event = lifecycle
        return DemoActionLifecycleReadModel(
            intent=intent, result=result, event=event, idempotent_replay=replay
        )
