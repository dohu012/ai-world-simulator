"""Database-backed observer and replay read models."""

import json
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app.application.action_validator import MoveState, ScenarioActionState
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
from app.infrastructure.database import memory_models as mr
from app.infrastructure.database import models as r
from app.infrastructure.database import runtime_models as rr
from app.infrastructure.database import seven_day_models as sr
from app.services.demo_world import (
    DemoAgentPerspectiveReadModel,
    DemoWorldReadModel,
    DemoWorldSummaryReadModel,
)
from app.world_engine.gray_harbor import MoveMutationPlan, ScenarioMutationPlan


class ActionLifecycleConflictError(Exception):
    """A concurrent request persisted the same deterministic lifecycle."""


class WorldTransactionError(Exception):
    """A database lock/deadlock/serialization failure, never a domain rejection."""


class MutationConflictError(Exception):
    """The authoritative row moved or vanished between validation and write.

    This is a lost optimistic race, not a caller mistake: the same request may
    succeed on retry, so the lifecycle records a rejection rather than a 5xx.
    """

    failure_code = "MUTATION_STATE_CONFLICT"
    failure_reason = "Authoritative state changed before the mutation was written."


class MutationRejectedError(Exception):
    """The objective mutation is impossible against current authoritative state.

    Validation ran against a snapshot; this is the write-time re-check, so the
    caller gets the same stable failure code an up-front rejection would carry.
    """

    def __init__(self, failure_code: str, failure_reason: str) -> None:
        super().__init__(failure_code)
        self.failure_code = failure_code
        self.failure_reason = failure_reason


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
    retrieval_id: str | None = None
    retrieval_mode: str | None = None
    selected_memory_ids: list[str] = Field(default_factory=list)
    memory_context_watermark: str | None = None
    memory_characters_used: int | None = None
    evolution_context_watermark: str | None = None
    identity_version: int | None = None
    relationship_versions: dict[str, int] = Field(default_factory=dict)


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
        retrieval_rows = list(
            (
                await self.session.scalars(
                    select(mr.MemoryRetrievalRunRecord).where(
                        mr.MemoryRetrievalRunRecord.world_id == world_id,
                        mr.MemoryRetrievalRunRecord.decision_id.is_not(None),
                    )
                )
            ).all()
        )
        retrieval_by_decision = {
            row.decision_id: row for row in retrieval_rows if row.decision_id is not None
        }
        selected_by_retrieval: dict[str, list[str]] = {}
        if retrieval_rows:
            candidate_rows = list(
                (
                    await self.session.scalars(
                        select(mr.MemoryRetrievalCandidateRecord)
                        .where(
                            mr.MemoryRetrievalCandidateRecord.retrieval_id.in_(
                                [row.id for row in retrieval_rows]
                            ),
                            mr.MemoryRetrievalCandidateRecord.selected.is_(True),
                        )
                        .order_by(
                            mr.MemoryRetrievalCandidateRecord.retrieval_id,
                            mr.MemoryRetrievalCandidateRecord.rank,
                        )
                    )
                ).all()
            )
            for candidate in candidate_rows:
                selected_by_retrieval.setdefault(candidate.retrieval_id, []).append(
                    candidate.memory_id
                )
        windows = list(
            (
                await self.session.scalars(
                    select(rr.OracleWindowRecord).where(rr.OracleWindowRecord.world_id == world_id)
                )
            ).all()
        )
        decisions = []
        for row in decision_rows:
            retrieval = retrieval_by_decision.get(row.id)
            evolution = row.input_payload.get("evolution_context")
            evolution_payload = evolution if isinstance(evolution, dict) else {}
            identity = evolution_payload.get("identity")
            identity_payload = identity if isinstance(identity, dict) else {}
            relationship_value = evolution_payload.get("relationships")
            relationship_payloads = (
                relationship_value if isinstance(relationship_value, list) else []
            )
            decisions.append(
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
                    retrieval_id=retrieval.id if retrieval is not None else None,
                    retrieval_mode=retrieval.mode if retrieval is not None else None,
                    selected_memory_ids=selected_by_retrieval.get(retrieval.id, [])
                    if retrieval is not None
                    else [],
                    memory_context_watermark=retrieval.context_watermark
                    if retrieval is not None
                    else None,
                    memory_characters_used=retrieval.token_used if retrieval is not None else None,
                    evolution_context_watermark=str(
                        row.input_payload.get("evolution_context_watermark", "")
                    )
                    or None,
                    identity_version=int(identity_payload["version"])
                    if isinstance(identity_payload.get("version"), int)
                    else None,
                    relationship_versions={
                        f"{item.get('target_type')}:{item.get('target_id')}": int(
                            item.get("version", 1)
                        )
                        for item in relationship_payloads
                        if isinstance(item, dict)
                    },
                )
            )
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
            # populate_existing overwrites any copy this session loaded before the
            # lock (observer reads run first), so validation sees the row as it is
            # under FOR UPDATE rather than the identity map's pre-lock snapshot.
            world_row = await self.session.scalar(
                select(r.WorldRecord)
                .where(r.WorldRecord.id == world_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        except DBAPIError as exc:
            await self.session.rollback()
            raise WorldTransactionError("world lock acquisition failed") from exc
        if world_row is None:
            return None
        actor_row = await self.session.scalar(
            select(r.CharacterRecord)
            .where(r.CharacterRecord.world_id == world_id, r.CharacterRecord.id == actor_id)
            .execution_options(populate_existing=True)
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

    async def lock_scenario_action_state(self, affordance_id: str) -> ScenarioActionState:
        resource_requirements = {
            "gh-v1:consume-medicine": ("account-clinic-medicine", 1),
            "gh-v1:transfer-food": ("account-store-food", 4),
            "gh-v1:help-luo": ("account-store-food", 2),
            "gh-v1:allocate-rescue-seats": ("account-rescue-seats", 10),
        }
        requirement = resource_requirements.get(affordance_id)
        if requirement is not None:
            account = await self.session.get(
                sr.ResourceAccountRecord,
                requirement[0],
                with_for_update=True,
                populate_existing=True,
            )
            return ScenarioActionState(
                available=account.available if account is not None else None,
                required=requirement[1],
            )
        plan_id = {
            "gh-v1:abandon-store-plan": "plan-chen-supplies",
            "gh-v1:complete-triage": "plan-lin-triage",
            "gh-v1:route-clinic": "plan-zhou-rescue",
        }.get(affordance_id)
        if plan_id is not None:
            plan = await self.session.get(
                sr.AgentPlanRecord, plan_id, with_for_update=True, populate_existing=True
            )
            return ScenarioActionState(plan_status=plan.status if plan is not None else None)
        return ScenarioActionState()

    async def persist_action_lifecycle(
        self,
        intent: ActionIntent,
        result: ActionResult,
        event: WorldEvent | None,
        observations: list[Observation] | None = None,
        mutation: MoveMutationPlan | ScenarioMutationPlan | None = None,
    ) -> None:
        """Flush one already adjudicated lifecycle and objective mutation, then commit once."""
        try:
            if isinstance(mutation, MoveMutationPlan):
                world_row = await self.session.get(r.WorldRecord, mutation.world.id)
                character_row = await self.session.get(r.CharacterRecord, mutation.character.id)
                if world_row is None or character_row is None:
                    raise MutationConflictError("locked mutation rows disappeared")
                world_row.version = mutation.world.version
                world_row.payload = mutation.world.model_dump(mode="json")
                character_row.version = mutation.character.version
                character_row.payload = mutation.character.model_dump(mode="json")
            elif isinstance(mutation, ScenarioMutationPlan):
                await self._apply_scenario_mutation(intent, mutation)
        except (MutationConflictError, MutationRejectedError):
            # Discard the partial mutation so the caller can record a rejected
            # lifecycle on a clean transaction instead of losing the audit trail.
            await self.session.rollback()
            raise
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
        except StaleDataError as exc:
            # version_id_col matched no row: another writer committed a newer
            # version after this transaction read it.
            await self.session.rollback()
            raise MutationConflictError(str(exc)) from exc
        except DBAPIError as exc:
            await self.session.rollback()
            raise WorldTransactionError("world transaction failed") from exc
        except Exception:
            await self.session.rollback()
            raise

    async def _apply_scenario_mutation(
        self, intent: ActionIntent, mutation: ScenarioMutationPlan
    ) -> None:
        if mutation.plan_id is not None:
            plan = await self.session.get(
                sr.AgentPlanRecord,
                mutation.plan_id,
                with_for_update=True,
                populate_existing=True,
            )
            if plan is None or mutation.plan_status is None:
                raise MutationConflictError("scenario plan mutation target disappeared")
            plan.status = mutation.plan_status
            plan.version += 1
            plan.payload = {**plan.payload, "status": mutation.plan_status, "version": plan.version}
            return
        if mutation.resource_id is None:
            raise RuntimeError("resource mutation is missing its resource definition")
        for index, leg in enumerate(mutation.legs):
            account = await self.session.get(
                sr.ResourceAccountRecord,
                leg.account_id,
                with_for_update=True,
                populate_existing=True,
            )
            if account is None:
                raise MutationConflictError("scenario resource account disappeared")
            new_available = account.available + leg.delta_available
            new_consumed = account.consumed + leg.delta_consumed
            if new_available < 0 or new_consumed < 0:
                raise MutationRejectedError(
                    "RESOURCE_INSUFFICIENT", "The offered resource is no longer sufficient."
                )
            prior_version = account.version
            account.available = new_available
            account.consumed = new_consumed
            account.version += 1
            account.payload = {
                **account.payload,
                "available": new_available,
                "consumed": new_consumed,
                "version": account.version,
            }
            self.session.add(
                sr.ResourceLedgerRecord(
                    id=f"ledger-{intent.id}-{index}",
                    world_id=intent.world_id,
                    resource_id=mutation.resource_id,
                    idempotency_key=f"{intent.id}:{index}",
                    operation=mutation.operation,
                    amount=abs(leg.delta_available) or leg.delta_consumed,
                    world_time=intent.submitted_at,
                    payload={
                        "account_id": leg.account_id,
                        "prior_version": prior_version,
                        "new_version": account.version,
                        "delta_available": leg.delta_available,
                        "delta_consumed": leg.delta_consumed,
                        "source_action_id": intent.id,
                    },
                )
            )

    async def rollback(self) -> None:
        await self.session.rollback()
