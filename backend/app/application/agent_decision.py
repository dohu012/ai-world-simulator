"""Auditable Observation-only decision orchestration."""

import json
from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.action_lifecycle import (
    DemoActionLifecycleReadModel,
    DemoActionSubmission,
    GrayHarborActionService,
)
from app.application.evolution_service import EvolutionApplicationService
from app.application.gray_harbor import (
    WORLD_ID,
    GrayHarborReadService,
)
from app.application.memory_service import MemoryApplicationService, RetrievalRead
from app.domain.enums import ActionType
from app.infrastructure.database import memory_models as mr
from app.infrastructure.database import models as r
from app.model_gateway.contracts import (
    AgentDecisionProposal,
    ModelGateway,
    ModelOutcome,
    ModelRequest,
)
from app.repositories.worlds import WorldRepository

PROMPT_VERSION = "gray-harbor-decision-v1"
INPUT_VERSION = "agent-decision-input-v1"
TRANSIENT = {"MODEL_TIMEOUT", "MODEL_RATE_LIMITED", "MODEL_PROVIDER_UNAVAILABLE"}


class DecisionSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    idempotency_key: str = Field(min_length=1, max_length=64)


class DecisionAttemptRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    attempt_number: int
    provider: str
    model: str
    provider_request_id: str | None
    failure_code: str | None
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: float | None = None


class AgentDecisionReadModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    decision_id: str
    status: str
    idempotent_replay: bool
    observation_watermark: str
    observation_ids: list[str]
    evolution_context_watermark: str
    identity_version: int
    relationship_versions: dict[str, int]
    prompt_version: str
    prompt_hash: str
    schema_version: str
    schema_hash: str
    attempts: list[DecisionAttemptRead]
    proposal: AgentDecisionProposal | None
    failure_code: str | None
    action: DemoActionLifecycleReadModel | None


class DecisionInProgressError(Exception):
    pass


class AgentDecisionApplicationService:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        gateway: ModelGateway,
        *,
        max_attempts: int = 2,
        timeout_seconds: float = 15.0,
        lease_seconds: int = 60,
        after_attempt_hook: Callable[[], Awaitable[None]] | None = None,
        after_action_hook: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        self.sessions, self.gateway = sessions, gateway
        self.max_attempts, self.timeout_seconds, self.lease_seconds = (
            max_attempts,
            timeout_seconds,
            lease_seconds,
        )
        self.after_attempt_hook = after_attempt_hook
        self.after_action_hook = after_action_hook

    async def decide(self, agent_id: str, submission: DecisionSubmission) -> AgentDecisionReadModel:
        digest = sha256(f"{WORLD_ID}:{agent_id}:{submission.idempotency_key}".encode()).hexdigest()[
            :20
        ]
        decision_id = f"decision-demo-{digest}"
        existing = await self._existing(decision_id)
        if existing is not None:
            if existing.status in {"completed", "failed", "rejected"}:
                return await self._read(existing, True)
            return await self._recover(existing, agent_id, digest)
        async with self.sessions() as session:
            input_model = await GrayHarborReadService(WorldRepository(session)).agent_input(
                agent_id
            )
            edges = list(
                (
                    await session.execute(
                        select(r.LocationEdgeRecord.to_location_id).where(
                            r.LocationEdgeRecord.world_id == WORLD_ID,
                            r.LocationEdgeRecord.from_location_id
                            == input_model.character.location_id,
                        )
                    )
                ).scalars()
            )
        observation_ids = [
            x.id
            for x in sorted(input_model.observations, key=lambda x: (x.observed_at, x.id))[-32:]
        ]
        memory_context = await self._memory_context(
            agent_id,
            datetime.fromisoformat(input_model.world.current_time),
            input_model.observations,
            trace_key=decision_id,
        )
        evolution_context, evolution_watermark = await EvolutionApplicationService(
            self.sessions
        ).context(agent_id)
        watermark = self._input_watermark(
            observation_ids, memory_context.context_watermark, evolution_watermark
        )
        affordances: list[dict[str, Any]] = [{"id": "wait", "action": "wait", "parameters": {}}]
        affordances += [
            {
                "id": f"move:{target}",
                "action": "move",
                "parameters": {
                    "target_location_id": target,
                    "expected_character_version": input_model.character.version,
                    "expected_world_version": input_model.world.version,
                },
            }
            for target in sorted(edges)
        ]
        safe_input = {
            "input_version": INPUT_VERSION,
            "world": input_model.world.model_dump(mode="json"),
            "character": input_model.character.model_dump(mode="json"),
            "profile": input_model.agentProfile.model_dump(mode="json"),
            "observations": [x.model_dump(mode="json") for x in input_model.observations],
            "observation_ids": observation_ids,
            "observation_watermark": watermark,
            "memory_context": memory_context.model_dump(mode="json"),
            "evolution_context": evolution_context,
            "affordances": affordances,
        }
        schema = AgentDecisionProposal.model_json_schema()
        schema_hash = sha256(
            json.dumps(schema, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        prompt = json.dumps(safe_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        prompt_hash = sha256(prompt.encode()).hexdigest()
        now = datetime.now(UTC)
        async with self.sessions() as session:
            await session.execute(
                insert(r.PromptVersionRecord)
                .values(
                    id=PROMPT_VERSION,
                    prompt_hash=prompt_hash,
                    schema_hash=schema_hash,
                    payload={"input_version": INPUT_VERSION, "output_schema": schema},
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
            session.add(
                r.AgentDecisionRecord(
                    id=decision_id,
                    world_id=WORLD_ID,
                    agent_id=agent_id,
                    idempotency_key=submission.idempotency_key,
                    status="claimed",
                    claim_owner=decision_id,
                    lease_expires_at=now + timedelta(seconds=self.lease_seconds),
                    claim_token=1,
                    input_payload={
                        "observation_ids": observation_ids,
                        "observation_watermark": watermark,
                        "memory_context_watermark": memory_context.context_watermark,
                        "evolution_context_watermark": evolution_watermark,
                        "evolution_context": evolution_context,
                        "retrieval_id": memory_context.id,
                        "decision_id": decision_id,
                        "prompt_version": PROMPT_VERSION,
                        "prompt_hash": prompt_hash,
                        "schema_version": "1",
                        "schema_hash": schema_hash,
                        "affordances": affordances,
                    },
                )
            )
            retrieval = await session.get(mr.MemoryRetrievalRunRecord, memory_context.id)
            if retrieval is not None:
                retrieval.decision_id = decision_id
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise DecisionInProgressError from None
        outcomes: list[ModelOutcome] = []
        for number in range(1, self.max_attempts + 1):
            outcome = await self.gateway.complete(
                ModelRequest(
                    task="gray_harbor_decide_once",
                    prompt=prompt,
                    output_schema=schema,
                    timeout_seconds=self.timeout_seconds,
                    max_output_tokens=300,
                    correlation_id=decision_id,
                )
            )
            outcomes.append(outcome)
            await self._persist_attempt(decision_id, number, outcome)
            if self.after_attempt_hook is not None:
                await self.after_attempt_hook()
            if outcome.failure_code not in TRANSIENT:
                break
        last = outcomes[-1]
        proposal = None
        failure = last.failure_code
        if failure is None:
            try:
                proposal = AgentDecisionProposal.model_validate(last.output)
            except ValidationError:
                failure = "MODEL_OUTPUT_INVALID"
        offered = {x["id"]: x for x in affordances}
        if proposal is not None and (
            proposal.affordance_id not in offered
            or proposal.action.value != offered[proposal.affordance_id]["action"]
            or proposal.observation_watermark != watermark
            or proposal.observation_ids != observation_ids
        ):
            failure, proposal = "DECISION_OUTPUT_NOT_ALLOWED", None
        if proposal is not None:
            _, fresh_watermark = await self._rebuild_prompt(agent_id, {"affordances": affordances})
            if fresh_watermark != watermark:
                failure, proposal = "DECISION_INPUT_STALE", None

        action = None
        if proposal is not None and not await self._claim_is_current(decision_id, 1):
            raise DecisionInProgressError
        if proposal is not None:
            choice = offered[proposal.affordance_id]
            async with self.sessions() as session:
                action = await GrayHarborActionService(WorldRepository(session)).submit(
                    agent_id,
                    DemoActionSubmission(
                        idempotency_key=f"decision-{digest}",
                        action_type=ActionType(choice["action"]),
                        parameters=choice["parameters"],
                        reason_summary=proposal.rationale_summary,
                    ),
                )
        if action is not None and self.after_action_hook is not None:
            await self.after_action_hook()
        await self._finalize(decision_id, proposal, failure, action, expected_token=1)
        row = await self._existing(decision_id)
        assert row is not None
        return await self._read(row, False)

    async def _recover(
        self, existing: r.AgentDecisionRecord, agent_id: str, digest: str
    ) -> AgentDecisionReadModel:
        now = datetime.now(UTC)
        async with self.sessions() as session:
            row = await session.get(r.AgentDecisionRecord, existing.id, with_for_update=True)
            assert row is not None
            if row.status in {"completed", "failed", "rejected"}:
                return await self._read(row, True)
            if row.lease_expires_at is not None and row.lease_expires_at > now:
                raise DecisionInProgressError
            row.claim_token += 1
            token = row.claim_token
            row.claim_owner = f"{row.id}:takeover:{token}"
            row.lease_expires_at = now + timedelta(seconds=self.lease_seconds)
            await session.commit()
            input_payload = dict(row.input_payload)

        async with self.sessions() as session:
            attempts = list(
                (
                    await session.scalars(
                        select(r.ModelCallAttemptRecord)
                        .where(r.ModelCallAttemptRecord.decision_id == existing.id)
                        .order_by(r.ModelCallAttemptRecord.attempt_number)
                    )
                ).all()
            )
        completed = next(
            (
                ModelOutcome.model_validate(attempt.payload)
                for attempt in reversed(attempts)
                if attempt.status == "completed" and attempt.failure_code is None
            ),
            None,
        )
        if completed is None:
            prompt, current_watermark = await self._rebuild_prompt(agent_id, input_payload)
            if current_watermark != str(input_payload["observation_watermark"]):
                await self._finalize(
                    existing.id,
                    None,
                    "DECISION_INPUT_STALE",
                    None,
                    expected_token=token,
                )
                row = await self._existing(existing.id)
                assert row is not None
                return await self._read(row, False)
            completed = await self.gateway.complete(
                ModelRequest(
                    task="gray_harbor_decide_once_recovery",
                    prompt=prompt,
                    output_schema=AgentDecisionProposal.model_json_schema(),
                    timeout_seconds=self.timeout_seconds,
                    max_output_tokens=300,
                    correlation_id=existing.id,
                )
            )
            await self._persist_attempt(existing.id, len(attempts) + 1, completed)

        proposal: AgentDecisionProposal | None = None
        failure = completed.failure_code
        if failure is None:
            try:
                proposal = AgentDecisionProposal.model_validate(completed.output)
            except ValidationError:
                failure = "MODEL_OUTPUT_INVALID"
        affordances_value = input_payload.get("affordances")
        affordances = affordances_value if isinstance(affordances_value, list) else []
        offered = {
            str(item["id"]): item for item in affordances if isinstance(item, dict) and "id" in item
        }
        observation_ids_value = input_payload.get("observation_ids")
        observation_ids = (
            [str(value) for value in observation_ids_value]
            if isinstance(observation_ids_value, list)
            else []
        )
        watermark = str(input_payload["observation_watermark"])
        if proposal is not None and (
            proposal.affordance_id not in offered
            or proposal.action.value != offered[proposal.affordance_id]["action"]
            or proposal.observation_watermark != watermark
            or proposal.observation_ids != observation_ids
        ):
            proposal, failure = None, "DECISION_OUTPUT_NOT_ALLOWED"

        action: DemoActionLifecycleReadModel | None = None
        if proposal is not None:
            if not await self._claim_is_current(existing.id, token):
                raise DecisionInProgressError
            action_key = f"decision-{digest}"
            action_digest = sha256(f"{WORLD_ID}:{agent_id}:{action_key}".encode()).hexdigest()[:20]
            intent_id = f"intent-demo-{action_digest}"
            async with self.sessions() as session:
                lifecycle = await WorldRepository(session).get_action_lifecycle(intent_id)
            if lifecycle is not None:
                action = GrayHarborActionService._read(lifecycle, True)
            else:
                choice = offered[proposal.affordance_id]
                parameters = choice.get("parameters")
                if not isinstance(parameters, dict):
                    parameters = {}
                async with self.sessions() as session:
                    action = await GrayHarborActionService(WorldRepository(session)).submit(
                        agent_id,
                        DemoActionSubmission(
                            idempotency_key=action_key,
                            action_type=ActionType(str(choice["action"])),
                            parameters=parameters,
                            reason_summary=proposal.rationale_summary,
                        ),
                    )
        await self._finalize(existing.id, proposal, failure, action, expected_token=token)
        row = await self._existing(existing.id)
        assert row is not None
        return await self._read(row, False)

    async def _rebuild_prompt(
        self, agent_id: str, input_payload: dict[str, object]
    ) -> tuple[str, str]:
        async with self.sessions() as session:
            input_model = await GrayHarborReadService(WorldRepository(session)).agent_input(
                agent_id
            )
        observation_ids = [
            item.id
            for item in sorted(
                input_model.observations, key=lambda item: (item.observed_at, item.id)
            )[-32:]
        ]
        memory_context = await self._memory_context(
            agent_id,
            datetime.fromisoformat(input_model.world.current_time),
            input_model.observations,
            trace_key=str(input_payload.get("decision_id", "freshness-check")),
        )
        evolution_context, evolution_watermark = await EvolutionApplicationService(
            self.sessions
        ).context(agent_id)
        watermark = self._input_watermark(
            observation_ids, memory_context.context_watermark, evolution_watermark
        )
        safe_input = {
            "input_version": INPUT_VERSION,
            "world": input_model.world.model_dump(mode="json"),
            "character": input_model.character.model_dump(mode="json"),
            "profile": input_model.agentProfile.model_dump(mode="json"),
            "observations": [item.model_dump(mode="json") for item in input_model.observations],
            "observation_ids": observation_ids,
            "observation_watermark": watermark,
            "memory_context": memory_context.model_dump(mode="json"),
            "evolution_context": evolution_context,
            "affordances": input_payload.get("affordances", []),
        }
        return (
            json.dumps(safe_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
            watermark,
        )

    async def _memory_context(
        self,
        agent_id: str,
        cutoff: datetime,
        observations: Sequence[BaseModel],
        *,
        trace_key: str,
    ) -> RetrievalRead:
        service = MemoryApplicationService(self.sessions)
        await service.sync_observations()
        query = json.dumps(
            [item.model_dump(mode="json") for item in observations[-8:]],
            ensure_ascii=False,
            separators=(",", ":"),
        )[:2000]
        return await service.retrieve_for_owner(
            agent_id,
            query=query,
            cutoff=cutoff,
            final_k=6,
            trace_key=trace_key,
        )

    @staticmethod
    def _input_watermark(
        observation_ids: list[str],
        memory_watermark: str,
        evolution_watermark: str,
    ) -> str:
        return sha256(
            json.dumps(
                {
                    "observations": observation_ids,
                    "memory_context": memory_watermark,
                    "evolution_context": evolution_watermark,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()

    async def _claim_is_current(self, decision_id: str, token: int) -> bool:
        async with self.sessions() as session:
            row = await session.get(r.AgentDecisionRecord, decision_id)
            return row is not None and row.claim_token == token and row.status == "claimed"

    async def _existing(self, decision_id: str) -> r.AgentDecisionRecord | None:
        async with self.sessions() as session:
            return await session.get(r.AgentDecisionRecord, decision_id)

    async def _persist_attempt(self, decision_id: str, number: int, outcome: ModelOutcome) -> None:
        now = datetime.now(UTC)
        async with self.sessions() as session:
            session.add(
                r.ModelCallAttemptRecord(
                    id=f"{decision_id}-attempt-{number}",
                    decision_id=decision_id,
                    attempt_number=number,
                    provider=outcome.provider,
                    model=outcome.model,
                    status="failed" if outcome.failure_code else "completed",
                    provider_request_id=outcome.provider_request_id,
                    failure_code=outcome.failure_code,
                    payload=outcome.model_dump(mode="json"),
                    started_at=now - timedelta(milliseconds=outcome.latency_ms),
                    completed_at=now,
                )
            )
            await session.commit()

    async def _finalize(
        self,
        decision_id: str,
        proposal: AgentDecisionProposal | None,
        failure: str | None,
        action: DemoActionLifecycleReadModel | None,
        expected_token: int,
    ) -> None:
        async with self.sessions() as session:
            row = await session.get(r.AgentDecisionRecord, decision_id, with_for_update=True)
            assert row is not None
            if row.claim_token != expected_token:
                raise DecisionInProgressError
            row.status = "failed" if failure else "completed"
            row.action_intent_id = action.intent.id if action else None
            row.outcome_payload = {
                "proposal": proposal.model_dump(mode="json") if proposal else None,
                "failure_code": failure,
            }
            row.claim_owner = None
            row.lease_expires_at = None
            await session.commit()

    async def _read(self, row: r.AgentDecisionRecord, replay: bool) -> AgentDecisionReadModel:
        async with self.sessions() as session:
            attempts = list(
                (
                    await session.scalars(
                        select(r.ModelCallAttemptRecord)
                        .where(r.ModelCallAttemptRecord.decision_id == row.id)
                        .order_by(r.ModelCallAttemptRecord.attempt_number)
                    )
                ).all()
            )
            lifecycle = (
                await WorldRepository(session).get_action_lifecycle(row.action_intent_id)
                if row.action_intent_id
                else None
            )
        inp, out = row.input_payload, row.outcome_payload or {}
        evolution = inp.get("evolution_context")
        evolution_payload = evolution if isinstance(evolution, dict) else {}
        identity = evolution_payload.get("identity")
        identity_payload = identity if isinstance(identity, dict) else {}
        relationships = evolution_payload.get("relationships")
        relationship_payloads = relationships if isinstance(relationships, list) else []
        return AgentDecisionReadModel(
            decision_id=row.id,
            status=row.status,
            idempotent_replay=replay,
            observation_watermark=str(inp["observation_watermark"]),
            observation_ids=[str(value) for value in inp["observation_ids"]]
            if isinstance(inp["observation_ids"], list)
            else [],
            evolution_context_watermark=str(inp.get("evolution_context_watermark", "")),
            identity_version=int(identity_payload.get("version", 1)),
            relationship_versions={
                f"{item.get('target_type')}:{item.get('target_id')}": int(item.get("version", 1))
                for item in relationship_payloads
                if isinstance(item, dict)
            },
            prompt_version=str(inp["prompt_version"]),
            prompt_hash=str(inp["prompt_hash"]),
            schema_version=str(inp["schema_version"]),
            schema_hash=str(inp["schema_hash"]),
            attempts=[
                DecisionAttemptRead.model_validate(
                    {
                        "attempt_number": x.attempt_number,
                        "provider": x.provider,
                        "model": x.model,
                        "provider_request_id": x.provider_request_id,
                        "failure_code": x.failure_code,
                        "latency_ms": x.payload.get("latency_ms", 0),
                        "input_tokens": x.payload.get("input_tokens"),
                        "output_tokens": x.payload.get("output_tokens"),
                    }
                )
                for x in attempts
            ],
            proposal=AgentDecisionProposal.model_validate(out["proposal"])
            if out.get("proposal")
            else None,
            failure_code=str(out["failure_code"]) if out.get("failure_code") else None,
            action=GrayHarborActionService._read(lifecycle, True) if lifecycle else None,
        )
