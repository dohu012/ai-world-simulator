"""TASK-016 durable claim and crash recovery closure."""

import os
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, select

from app.application.agent_decision import AgentDecisionApplicationService, DecisionSubmission
from app.application.gray_harbor import WORLD_ID
from app.core.config import Settings
from app.infrastructure.database import models as r
from app.infrastructure.database.session import Database
from app.model_gateway.adapters import ScriptedModelGateway
from app.services.seed_gray_harbor import seed_gray_harbor

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")


async def seed_clean(session) -> None:
    await session.execute(
        delete(r.ObservationRecord).where(r.ObservationRecord.id.like("obs-inference-race-%"))
    )
    await session.commit()
    await seed_gray_harbor(session)


def decision_id(key: str) -> str:
    digest = sha256(f"{WORLD_ID}:char-chen-mo:{key}".encode()).hexdigest()[:20]
    return f"decision-demo-{digest}"


async def expire(database: Database, identity: str) -> None:
    async with database.session_factory() as session:
        row = await session.get(r.AgentDecisionRecord, identity, with_for_update=True)
        assert row is not None
        row.lease_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        await session.commit()


async def crash() -> None:
    raise RuntimeError("injected crash checkpoint")


async def test_takeover_after_persisted_model_completion_makes_no_second_call() -> None:
    database = Database(Settings().database_url)
    key = f"recover-model-{uuid4().hex}"
    try:
        async with database.session_factory() as session:
            await seed_clean(session)
        first_gateway = ScriptedModelGateway()
        first = AgentDecisionApplicationService(
            database.session_factory, first_gateway, after_attempt_hook=crash
        )
        with pytest.raises(RuntimeError, match="checkpoint"):
            await first.decide("char-chen-mo", DecisionSubmission(idempotency_key=key))
        await expire(database, decision_id(key))
        recovery_gateway = ScriptedModelGateway()
        recovered = await AgentDecisionApplicationService(
            database.session_factory, recovery_gateway
        ).decide("char-chen-mo", DecisionSubmission(idempotency_key=key))
        assert recovered.status == "completed"
        assert len(first_gateway.requests) == 1
        assert recovery_gateway.requests == []
        assert recovered.action is not None
    finally:
        await database.dispose()


async def test_takeover_after_action_submission_creates_no_second_action() -> None:
    database = Database(Settings().database_url)
    key = f"recover-action-{uuid4().hex}"
    try:
        async with database.session_factory() as session:
            await seed_clean(session)
        first = AgentDecisionApplicationService(
            database.session_factory, ScriptedModelGateway(), after_action_hook=crash
        )
        with pytest.raises(RuntimeError, match="checkpoint"):
            await first.decide("char-chen-mo", DecisionSubmission(idempotency_key=key))
        identity = decision_id(key)
        await expire(database, identity)
        recovery_gateway = ScriptedModelGateway()
        recovered = await AgentDecisionApplicationService(
            database.session_factory, recovery_gateway
        ).decide("char-chen-mo", DecisionSubmission(idempotency_key=key))
        assert recovered.status == "completed" and recovered.action is not None
        assert recovered.action.idempotent_replay is True
        assert recovery_gateway.requests == []
        async with database.session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(r.ActionResultRecord)
                .where(r.ActionResultRecord.action_id == recovered.action.intent.id)
            )
            assert count == 1
    finally:
        await database.dispose()


async def test_two_takeover_workers_issue_only_one_recovery_model_call() -> None:
    import asyncio

    class CrashGateway:
        async def complete(self, _request):
            raise RuntimeError("crash before provider completion")

    database = Database(Settings().database_url)
    key = f"recover-race-{uuid4().hex}"
    try:
        async with database.session_factory() as session:
            await seed_clean(session)
        with pytest.raises(RuntimeError, match="before provider"):
            await AgentDecisionApplicationService(database.session_factory, CrashGateway()).decide(
                "char-chen-mo", DecisionSubmission(idempotency_key=key)
            )
        await expire(database, decision_id(key))
        gateways = [ScriptedModelGateway(), ScriptedModelGateway()]
        results = await asyncio.gather(
            *[
                AgentDecisionApplicationService(database.session_factory, gateway).decide(
                    "char-chen-mo", DecisionSubmission(idempotency_key=key)
                )
                for gateway in gateways
            ],
            return_exceptions=True,
        )
        assert sum(len(gateway.requests) for gateway in gateways) == 1
        completed = [result for result in results if not isinstance(result, Exception)]
        assert completed and all(result.status == "completed" for result in completed)
    finally:
        await database.dispose()


async def test_new_observation_after_inference_rejects_stale_action() -> None:
    database = Database(Settings().database_url)
    key = f"stale-inference-{uuid4().hex}"

    async def inject_observation() -> None:
        async with database.session_factory() as session:
            source = await session.scalar(
                select(r.ObservationRecord)
                .where(r.ObservationRecord.agent_id == "char-chen-mo")
                .limit(1)
            )
            assert source is not None
            payload = dict(source.payload)
            payload["id"] = f"obs-inference-race-{uuid4().hex}"
            payload["observed_at"] = datetime.now(UTC).isoformat()
            session.add(
                r.ObservationRecord(
                    id=str(payload["id"]),
                    world_id=source.world_id,
                    agent_id=source.agent_id,
                    observed_at=datetime.now(UTC),
                    source_event_id=None,
                    source_message_id=None,
                    schema_version=source.schema_version,
                    payload=payload,
                )
            )
            await session.commit()

    try:
        async with database.session_factory() as session:
            await seed_clean(session)
        outcome = await AgentDecisionApplicationService(
            database.session_factory,
            ScriptedModelGateway(),
            after_attempt_hook=inject_observation,
        ).decide("char-chen-mo", DecisionSubmission(idempotency_key=key))
        assert outcome.status == "failed"
        assert outcome.failure_code == "DECISION_INPUT_STALE"
        assert outcome.action is None
    finally:
        await database.dispose()
