import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

from app.core.config import Settings
from app.infrastructure.database.session import Database
from app.infrastructure.redis.client import create_redis_client

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INFRA_TESTS") != "1",
    reason="set RUN_INFRA_TESTS=1 with PostgreSQL and Redis running",
)


async def test_database_session_can_be_created() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            assert await session.scalar(text("SELECT 1")) == 1
    finally:
        await database.dispose()


async def test_redis_ping() -> None:
    client = create_redis_client(Settings().redis_url)
    try:
        assert await client.ping() is True
    finally:
        await client.aclose()


def test_alembic_upgrade_head() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).parents[1],
        check=False,
    )
    assert result.returncode == 0


async def test_gray_harbor_seed_is_idempotent_and_repository_reads_replay() -> None:
    from sqlalchemy import func, or_, select

    from app.infrastructure.database.models import (
        ObservationRecord,
        WorldEventRecord,
        WorldRecord,
    )
    from app.repositories.worlds import WorldRepository
    from app.services.seed_gray_harbor import seed_gray_harbor

    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
            await seed_gray_harbor(session)
            assert await session.scalar(select(func.count()).select_from(WorldRecord)) == 1
            seeded_event_ids = {
                "event-day1-fever",
                "event-day1-pathogen",
                "event-day2-panic-buying",
                "event-day2-north-gate-plan",
                "event-day3-guards",
                "event-chen-action-result",
            }
            assert await session.scalar(
                select(func.count())
                .select_from(WorldEventRecord)
                .where(WorldEventRecord.id.in_(seeded_event_ids))
            ) == len(seeded_event_ids)
            assert (
                await session.scalar(
                    select(func.count())
                    .select_from(ObservationRecord)
                    .where(
                        or_(
                            ObservationRecord.source_event_id.in_(seeded_event_ids),
                            ObservationRecord.source_message_id
                            == "oracle-response-chen-north-gate",
                        )
                    )
                )
                == 9
            )
            repository = WorldRepository(session)
            world = await repository.get_observer_world("world-gray-harbor-lockdown")
            assert world is not None
            replay = await repository.get_replay("world-gray-harbor-lockdown")
            assert replay is not None
            assert [x.occurred_at for x in replay.events] == sorted(
                x.occurred_at for x in replay.events
            )
            chen = next(x for x in replay.chains if x.correlation_id == "corr-chen-oracle-decision")
            assert chen.action_result_ids == ["result-chen-contact-courier"]
            lin = await repository.get_agent_perspective(
                "world-gray-harbor-lockdown", "char-lin-zhixia"
            )
            assert lin is not None
            assert lin.oracleRequests == []
            assert all(item.actor_id == "char-lin-zhixia" for item in lin.actionIntents)
            assert all(item.actor_id == "char-lin-zhixia" for item in lin.actionResults)
            assert "result-chen-contact-courier" not in {item.id for item in lin.actionResults}
            assert all(item.agent_id == "char-lin-zhixia" for item in lin.observations)
            assert all(item.observation_type != "oracle" for item in lin.observations)
            chen_input = await repository.get_agent_perspective(
                "world-gray-harbor-lockdown", "char-chen-mo"
            )
            assert chen_input is not None
            assert any(
                item.id == "obs-oracle-response-chen-north-gate" for item in chen_input.observations
            )
    finally:
        await database.dispose()


async def test_action_lifecycle_is_idempotent_and_replayable() -> None:
    from sqlalchemy import func, select

    from app.application.action_lifecycle import (
        DemoActionSubmission,
        GrayHarborActionService,
    )
    from app.domain.enums import ActionType
    from app.infrastructure.database.models import (
        ActionIntentRecord,
        ActionResultRecord,
        WorldEventRecord,
    )
    from app.repositories.worlds import WorldRepository
    from app.services.seed_gray_harbor import seed_gray_harbor

    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
            repository = WorldRepository(session)
            service = GrayHarborActionService(repository)
            submission = DemoActionSubmission(
                idempotency_key="infra-lin-wait-v1",
                action_type=ActionType.WAIT,
                parameters={},
                reason_summary="Wait for verified information.",
            )
            first = await service.submit("char-lin-zhixia", submission)
            assert first.event is not None
            counts_after_first = (
                await session.scalar(select(func.count()).select_from(ActionIntentRecord)),
                await session.scalar(select(func.count()).select_from(ActionResultRecord)),
                await session.scalar(select(func.count()).select_from(WorldEventRecord)),
            )
            second = await service.submit("char-lin-zhixia", submission)
            counts_after_second = (
                await session.scalar(select(func.count()).select_from(ActionIntentRecord)),
                await session.scalar(select(func.count()).select_from(ActionResultRecord)),
                await session.scalar(select(func.count()).select_from(WorldEventRecord)),
            )
            assert second.idempotent_replay is True
            assert second.intent.id == first.intent.id
            assert counts_after_second == counts_after_first
            replay = await repository.get_replay("world-gray-harbor-lockdown")
            assert replay is not None
            chain = next(
                item for item in replay.chains if item.correlation_id == first.intent.correlation_id
            )
            assert chain.action_intent_ids == [first.intent.id]
            assert chain.action_result_ids == [first.result.id]
            assert chain.event_ids == [first.event.id]
            chen = await repository.get_agent_perspective(
                "world-gray-harbor-lockdown", "char-chen-mo"
            )
            assert chen is not None
            assert first.intent.id not in {item.id for item in chen.actionIntents}
    finally:
        await database.dispose()


async def test_concurrent_stale_moves_mutate_world_exactly_once() -> None:
    import asyncio
    from uuid import uuid4

    from app.application.action_lifecycle import DemoActionSubmission, GrayHarborActionService
    from app.domain.enums import ActionType
    from app.infrastructure.database.models import CharacterRecord, WorldRecord
    from app.repositories.worlds import WorldRepository
    from app.services.seed_gray_harbor import seed_gray_harbor

    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as seed_session:
            await seed_gray_harbor(seed_session)
        suffix = uuid4().hex

        def submission(key: str) -> DemoActionSubmission:
            return DemoActionSubmission(
                idempotency_key=key,
                action_type=ActionType.MOVE,
                parameters={
                    "target_location_id": "north-market-street",
                    "expected_character_version": 1,
                    "expected_world_version": 1,
                },
                reason_summary="Concurrent deterministic move.",
            )

        async def submit(key: str):
            async with database.session_factory() as session:
                return await GrayHarborActionService(WorldRepository(session)).submit(
                    "char-chen-mo", submission(key)
                )

        first, second = await asyncio.gather(
            submit(f"infra-move-a-{suffix}"), submit(f"infra-move-b-{suffix}")
        )
        assert sorted([first.result.status.value, second.result.status.value]) == [
            "rejected",
            "succeeded",
        ]
        rejected = first if first.result.status.value == "rejected" else second
        assert rejected.result.failure_code in {
            "CHARACTER_VERSION_CONFLICT",
            "WORLD_VERSION_CONFLICT",
        }
        assert rejected.event is None
        async with database.session_factory() as verify:
            world = await verify.get(WorldRecord, "world-gray-harbor-lockdown")
            character = await verify.get(CharacterRecord, "char-chen-mo")
            assert world is not None and character is not None
            assert world.version == 2 and world.payload["version"] == 2
            assert character.version == 2 and character.payload["version"] == 2
            assert character.payload["location_id"] == "north-market-street"
    finally:
        await database.dispose()


async def test_concurrent_same_key_move_creates_one_lifecycle() -> None:
    import asyncio
    from uuid import uuid4

    from sqlalchemy import func, select

    from app.application.action_lifecycle import DemoActionSubmission, GrayHarborActionService
    from app.domain.enums import ActionType
    from app.infrastructure.database.models import ActionIntentRecord, ActionResultRecord
    from app.repositories.worlds import WorldRepository
    from app.services.seed_gray_harbor import seed_gray_harbor

    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as seed_session:
            await seed_gray_harbor(seed_session)
        submission = DemoActionSubmission(
            idempotency_key=f"infra-same-move-{uuid4().hex}",
            action_type=ActionType.MOVE,
            parameters={
                "target_location_id": "north-market-street",
                "expected_character_version": 1,
                "expected_world_version": 1,
            },
            reason_summary="Same-key concurrent move.",
        )

        async def submit():
            async with database.session_factory() as session:
                return await GrayHarborActionService(WorldRepository(session)).submit(
                    "char-chen-mo", submission
                )

        first, second = await asyncio.gather(submit(), submit())
        assert first.intent.id == second.intent.id
        assert sorted([first.idempotent_replay, second.idempotent_replay]) == [False, True]
        async with database.session_factory() as verify:
            assert (
                await verify.scalar(
                    select(func.count())
                    .select_from(ActionIntentRecord)
                    .where(ActionIntentRecord.id == first.intent.id)
                )
                == 1
            )
            assert (
                await verify.scalar(
                    select(func.count())
                    .select_from(ActionResultRecord)
                    .where(ActionResultRecord.action_id == first.intent.id)
                )
                == 1
            )
    finally:
        await database.dispose()


async def test_injected_precommit_failure_rolls_back_state_and_lifecycle() -> None:
    from uuid import uuid4

    from sqlalchemy import func, select

    from app.application.action_lifecycle import DemoActionSubmission, GrayHarborActionService
    from app.domain.enums import ActionType
    from app.infrastructure.database.models import (
        ActionIntentRecord,
        CharacterRecord,
        ObservationRecord,
        WorldEventRecord,
        WorldRecord,
    )
    from app.repositories.worlds import WorldRepository
    from app.services.seed_gray_harbor import seed_gray_harbor

    async def fail_before_commit() -> None:
        raise RuntimeError("injected pre-commit failure")

    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as seed_session:
            await seed_gray_harbor(seed_session)
        async with database.session_factory() as session:
            counts_before = []
            for record in (ActionIntentRecord, WorldEventRecord, ObservationRecord):
                counts_before.append(await session.scalar(select(func.count()).select_from(record)))
            service = GrayHarborActionService(
                WorldRepository(session, before_commit_hook=fail_before_commit)
            )
            with pytest.raises(RuntimeError, match="injected pre-commit failure"):
                await service.submit(
                    "char-chen-mo",
                    DemoActionSubmission(
                        idempotency_key=f"infra-rollback-{uuid4().hex}",
                        action_type=ActionType.MOVE,
                        parameters={
                            "target_location_id": "north-market-street",
                            "expected_character_version": 1,
                            "expected_world_version": 1,
                        },
                        reason_summary="This transaction must roll back.",
                    ),
                )
        async with database.session_factory() as verify:
            counts_after = []
            for record in (ActionIntentRecord, WorldEventRecord, ObservationRecord):
                counts_after.append(await verify.scalar(select(func.count()).select_from(record)))
            world = await verify.get(WorldRecord, "world-gray-harbor-lockdown")
            character = await verify.get(CharacterRecord, "char-chen-mo")
            assert counts_after == counts_before
            assert world is not None and world.version == 1 and world.payload["version"] == 1
            assert character is not None and character.version == 1
            assert character.payload["location_id"] == "north-market-store"
    finally:
        await database.dispose()


async def test_world_lock_timeout_is_operational_error() -> None:
    from app.repositories.worlds import WorldRepository, WorldTransactionError
    from app.services.seed_gray_harbor import seed_gray_harbor

    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as seed_session:
            await seed_gray_harbor(seed_session)
        async with (
            database.session_factory() as holder_session,
            database.session_factory() as contender_session,
        ):
            holder = WorldRepository(holder_session)
            assert (
                await holder.lock_move_state("world-gray-harbor-lockdown", "char-chen-mo")
                is not None
            )
            contender = WorldRepository(contender_session, lock_timeout_ms=100)
            with pytest.raises(WorldTransactionError):
                await contender.lock_move_state("world-gray-harbor-lockdown", "char-chen-mo")
            await holder.rollback()
    finally:
        await database.dispose()
