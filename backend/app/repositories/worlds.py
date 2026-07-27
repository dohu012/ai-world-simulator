"""Database-backed observer and replay read models."""

import json
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.action_validator import MoveState
from app.domain.schemas import (
    ActionIntent,
    ActionResult,
    AgentBelief,
    AgentProfile,
    Character,
    Observation,
    OracleRequest,
    OracleResponse,
    World,
    WorldEvent,
    WorldFact,
)
from app.infrastructure.database import models as r
from app.infrastructure.database import runtime_models as rr
from app.services.demo_world import (
    DemoAgentPerspectiveReadModel,
    DemoWorldReadModel,
    DemoWorldSummaryReadModel,
)
from app.world_engine.gray_harbor import MoveMutationPlan


class ActionLifecycleConflictError(Exception):
    """A concurrent request persisted the same deterministic lifecycle."""


class WorldTransactionError(Exception):
    """A database lock/deadlock/serialization failure, never a domain rejection."""


class ReplayChain(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    correlation_id: str
    oracle_request_ids: list[str]
    oracle_response_ids: list[str]
    action_intent_ids: list[str]
    action_result_ids: list[str]
    event_ids: list[str]
    decision_ids: list[str] = Field(default_factory=list)


class WorldReplayReadModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    world_id: str
    events: list[WorldEvent]
    observations: list[Observation]
    oracle_requests: list[OracleRequest]
    oracle_responses: list[OracleResponse]
    action_intents: list[ActionIntent]
    action_results: list[ActionResult]
    chains: list[ReplayChain]

    decisions: list["DecisionReplayItem"] = Field(default_factory=list)


class DecisionReplayItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    decision_id: str
    agent_id: str
    status: str
    observation_ids: list[str]
    prompt_hash: str
    failure_code: str | None
    action_intent_id: str | None


def _from_json(contract: Any, payload: dict[str, Any]) -> Any:
    """Validate a JSONB payload through the domain contract's JSON path."""
    return contract.model_validate_json(json.dumps(payload))


def _string_list(value: object) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


class WorldRepository:
    """Map persistence records through the canonical Pydantic contracts."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        lock_timeout_ms: int = 5_000,
        before_commit_hook: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        self.session = session
        self.lock_timeout_ms = lock_timeout_ms
        self.before_commit_hook = before_commit_hook

    async def _rows(self, record_type: Any, world_id: str, *ordering: Any) -> list[Any]:
        query = select(record_type).where(record_type.world_id == world_id)
        if ordering:
            query = query.order_by(*ordering)
        return list((await self.session.scalars(query)).all())

    async def get_observer_world(self, world_id: str) -> DemoWorldReadModel | None:
        world_row = await self.session.get(r.WorldRecord, world_id)
        if world_row is None:
            return None
        specs: list[tuple[str, Any, Any, tuple[Any, ...]]] = [
            ("characters", r.CharacterRecord, Character, (r.CharacterRecord.id,)),
            (
                "agentProfiles",
                r.AgentProfileRecord,
                AgentProfile,
                (r.AgentProfileRecord.character_id,),
            ),
            (
                "events",
                r.WorldEventRecord,
                WorldEvent,
                (r.WorldEventRecord.occurred_at, r.WorldEventRecord.id),
            ),
            (
                "observations",
                r.ObservationRecord,
                Observation,
                (r.ObservationRecord.observed_at, r.ObservationRecord.id),
            ),
            (
                "beliefs",
                r.AgentBeliefRecord,
                AgentBelief,
                (r.AgentBeliefRecord.learned_at, r.AgentBeliefRecord.id),
            ),
            (
                "oracleRequests",
                r.OracleRequestRecord,
                OracleRequest,
                (r.OracleRequestRecord.requested_at,),
            ),
            (
                "oracleResponses",
                r.OracleResponseRecord,
                OracleResponse,
                (r.OracleResponseRecord.responded_at,),
            ),
            (
                "actionIntents",
                r.ActionIntentRecord,
                ActionIntent,
                (r.ActionIntentRecord.submitted_at,),
            ),
            (
                "actionResults",
                r.ActionResultRecord,
                ActionResult,
                (r.ActionResultRecord.started_at,),
            ),
        ]
        values: dict[str, Any] = {"world": _from_json(World, world_row.payload)}
        for key, record_type, contract, ordering in specs:
            values[key] = [
                _from_json(contract, x.payload)
                for x in await self._rows(record_type, world_id, *ordering)
            ]
        return DemoWorldReadModel.model_validate(values)

    async def get_world_facts(self, world_id: str) -> list[WorldFact]:
        rows = await self._rows(
            r.WorldFactRecord,
            world_id,
            r.WorldFactRecord.valid_from,
            r.WorldFactRecord.id,
        )
        return [_from_json(WorldFact, row.payload) for row in rows]

    async def get_agent_perspective(
        self, world_id: str, agent_id: str
    ) -> DemoAgentPerspectiveReadModel | None:
        world = await self.get_observer_world(world_id)
        if world is None:
            return None
        character = next((x for x in world.characters if x.id == agent_id), None)
        profile = next((x for x in world.agentProfiles if x.character_id == agent_id), None)
        if character is None or profile is None:
            return None
        return DemoAgentPerspectiveReadModel(
            world=DemoWorldSummaryReadModel(
                id=world.world.id,
                name=world.world.name,
                current_time=world.world.current_time.isoformat(),
                schema_version=world.world.schema_version,
                version=world.world.version,
            ),
            character=character,
            agentProfile=profile,
            observations=[x for x in world.observations if x.agent_id == agent_id],
            beliefs=[x for x in world.beliefs if x.agent_id == agent_id],
            oracleRequests=[x for x in world.oracleRequests if x.agent_id == agent_id],
            oracleResponses=[x for x in world.oracleResponses if x.agent_id == agent_id],
            actionIntents=[x for x in world.actionIntents if x.actor_id == agent_id],
            actionResults=[x for x in world.actionResults if x.actor_id == agent_id],
        )

    async def get_replay(self, world_id: str) -> WorldReplayReadModel | None:
        world = await self.get_observer_world(world_id)
        if world is None:
            return None
        decision_rows = list(
            (
                await self.session.scalars(
                    select(r.AgentDecisionRecord)
                    .where(r.AgentDecisionRecord.world_id == world_id)
                    .order_by(r.AgentDecisionRecord.created_at, r.AgentDecisionRecord.id)
                )
            ).all()
        )
        windows = list(
            (
                await self.session.scalars(
                    select(rr.OracleWindowRecord).where(rr.OracleWindowRecord.world_id == world_id)
                )
            ).all()
        )
        decisions = [
            DecisionReplayItem(
                decision_id=row.id,
                agent_id=row.agent_id,
                status=row.status,
                observation_ids=_string_list(row.input_payload.get("observation_ids")),
                prompt_hash=str(row.input_payload.get("prompt_hash", "")),
                failure_code=str((row.outcome_payload or {}).get("failure_code"))
                if (row.outcome_payload or {}).get("failure_code")
                else None,
                action_intent_id=row.action_intent_id,
            )
            for row in decision_rows
        ]
        correlations = (
            {x.correlation_id for x in world.events}
            | {x.decision_correlation_id for x in world.oracleRequests}
            | {x.correlation_id for x in world.actionIntents}
            | {x.correlation_id for x in world.actionResults}
            | {window.decision_correlation_id for window in windows}
        )
        chains = []
        for correlation_id in sorted(correlations):
            requests = [
                x.id for x in world.oracleRequests if x.decision_correlation_id == correlation_id
            ]
            action_ids = [x.id for x in world.actionIntents if x.correlation_id == correlation_id]
            window_decisions = {
                window.final_decision_id
                for window in windows
                if window.decision_correlation_id == correlation_id
                and window.final_decision_id is not None
            }

            chains.append(
                ReplayChain(
                    correlation_id=correlation_id,
                    oracle_request_ids=requests,
                    oracle_response_ids=[
                        x.id for x in world.oracleResponses if x.request_id in requests
                    ],
                    action_intent_ids=action_ids,
                    action_result_ids=[
                        x.id for x in world.actionResults if x.correlation_id == correlation_id
                    ],
                    event_ids=[x.id for x in world.events if x.correlation_id == correlation_id],
                    decision_ids=[
                        decision.decision_id
                        for decision in decisions
                        if decision.decision_id in window_decisions
                        or decision.action_intent_id in action_ids
                    ],
                )
            )
        return WorldReplayReadModel(
            world_id=world_id,
            events=world.events,
            observations=world.observations,
            oracle_requests=world.oracleRequests,
            oracle_responses=world.oracleResponses,
            action_intents=world.actionIntents,
            action_results=world.actionResults,
            chains=chains,
            decisions=decisions,
        )

    async def get_action_lifecycle(
        self, intent_id: str
    ) -> tuple[ActionIntent, ActionResult, WorldEvent | None] | None:
        intent_row = await self.session.get(r.ActionIntentRecord, intent_id)
        if intent_row is None:
            return None
        result_row = await self.session.scalar(
            select(r.ActionResultRecord).where(r.ActionResultRecord.action_id == intent_id)
        )
        if result_row is None:
            return None
        event_row = await self.session.scalar(
            select(r.WorldEventRecord).where(r.WorldEventRecord.source_action_id == intent_id)
        )
        return (
            _from_json(ActionIntent, intent_row.payload),
            _from_json(ActionResult, result_row.payload),
            _from_json(WorldEvent, event_row.payload) if event_row else None,
        )

    async def lock_move_state(self, world_id: str, actor_id: str) -> MoveState | None:
        """Lock the world serialization boundary, then load deterministic move state."""
        try:
            await self.session.scalar(
                select(func.set_config("lock_timeout", f"{self.lock_timeout_ms}ms", True))
            )
            world_row = await self.session.scalar(
                select(r.WorldRecord).where(r.WorldRecord.id == world_id).with_for_update()
            )
        except DBAPIError as exc:
            await self.session.rollback()
            raise WorldTransactionError("world lock acquisition failed") from exc
        if world_row is None:
            return None
        actor_row = await self.session.scalar(
            select(r.CharacterRecord).where(
                r.CharacterRecord.world_id == world_id, r.CharacterRecord.id == actor_id
            )
        )
        if actor_row is None:
            return None
        locations = list(
            (
                await self.session.scalars(
                    select(r.LocationRecord).where(r.LocationRecord.world_id == world_id)
                )
            ).all()
        )
        edges = list(
            (
                await self.session.scalars(
                    select(r.LocationEdgeRecord).where(r.LocationEdgeRecord.world_id == world_id)
                )
            ).all()
        )
        actor = _from_json(Character, actor_row.payload)
        return MoveState(
            world=_from_json(World, world_row.payload),
            actor=actor,
            location_ids=frozenset(row.id for row in locations),
            directed_edges=frozenset((row.from_location_id, row.to_location_id) for row in edges),
            destination_witness_ids=(),
        )

    async def destination_witness_ids(
        self, world_id: str, actor_id: str, target_location_id: str
    ) -> tuple[str, ...]:
        rows = await self._rows(r.CharacterRecord, world_id, r.CharacterRecord.id)
        return tuple(
            character.id
            for row in rows
            if (character := _from_json(Character, row.payload)).id != actor_id
            and character.location_id == target_location_id
        )

    async def persist_action_lifecycle(
        self,
        intent: ActionIntent,
        result: ActionResult,
        event: WorldEvent | None,
        observations: list[Observation] | None = None,
        mutation: MoveMutationPlan | None = None,
    ) -> None:
        """Flush one already adjudicated lifecycle and objective mutation, then commit once."""
        if mutation is not None:
            world_row = await self.session.get(r.WorldRecord, mutation.world.id)
            character_row = await self.session.get(r.CharacterRecord, mutation.character.id)
            if world_row is None or character_row is None:
                raise RuntimeError("locked mutation rows disappeared")
            world_row.version = mutation.world.version
            world_row.payload = mutation.world.model_dump(mode="json")
            character_row.version = mutation.character.version
            character_row.payload = mutation.character.model_dump(mode="json")
        self.session.add(
            r.ActionIntentRecord(
                id=intent.id,
                world_id=intent.world_id,
                actor_id=intent.actor_id,
                submitted_at=intent.submitted_at,
                correlation_id=intent.correlation_id,
                schema_version=intent.schema_version,
                payload=intent.model_dump(mode="json"),
            )
        )
        self.session.add(
            r.ActionResultRecord(
                id=result.id,
                world_id=result.world_id,
                action_id=result.action_id,
                actor_id=result.actor_id,
                started_at=result.started_at,
                completed_at=result.completed_at,
                correlation_id=result.correlation_id,
                schema_version=result.schema_version,
                payload=result.model_dump(mode="json"),
            )
        )
        if event is not None:
            self.session.add(
                r.WorldEventRecord(
                    id=event.id,
                    world_id=event.world_id,
                    event_type=event.event_type.value,
                    occurred_at=event.occurred_at,
                    visibility=event.visibility.value,
                    correlation_id=event.correlation_id,
                    source_action_id=event.source_action_id,
                    schema_version=event.schema_version,
                    payload=event.model_dump(mode="json"),
                )
            )
        for observation in observations or []:
            self.session.add(
                r.ObservationRecord(
                    id=observation.id,
                    world_id=observation.world_id,
                    agent_id=observation.agent_id,
                    observed_at=observation.observed_at,
                    source_event_id=observation.source_event_id,
                    source_message_id=observation.source_message_id,
                    schema_version=observation.schema_version,
                    payload=observation.model_dump(mode="json"),
                )
            )
        try:
            await self.session.flush()
            if self.before_commit_hook is not None:
                await self.before_commit_hook()
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ActionLifecycleConflictError from exc
        except DBAPIError as exc:
            await self.session.rollback()
            raise WorldTransactionError("world transaction failed") from exc
        except Exception:
            await self.session.rollback()
            raise

    async def rollback(self) -> None:
        await self.session.rollback()
