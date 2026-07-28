"""Real PostgreSQL causal propagation, restart, isolation, and dialogue proof."""

import asyncio
import os
from datetime import timedelta

import pytest
from sqlalchemy import delete, func, select

from app.application.gray_harbor import WORLD_ID
from app.application.social_runtime import CHEN_ID, LIN_ID, ZHOU_ID, SocialRuntimeService
from app.core.config import Settings
from app.infrastructure.database import models as db
from app.infrastructure.database import runtime_models as runtime_db
from app.infrastructure.database import social_models as social_db
from app.infrastructure.database.session import Database
from app.services.seed_gray_harbor import seed_gray_harbor

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")


async def reset_social(database: Database) -> None:
    async with database.session_factory() as session:
        await session.execute(
            delete(social_db.ConversationRecord).where(
                social_db.ConversationRecord.world_id == WORLD_ID
            )
        )
        await session.execute(
            delete(social_db.BeliefRevisionRecord).where(
                social_db.BeliefRevisionRecord.world_id == WORLD_ID
            )
        )
        await session.execute(
            delete(social_db.BeliefEvidenceRecord).where(
                social_db.BeliefEvidenceRecord.world_id == WORLD_ID
            )
        )
        await session.execute(
            delete(social_db.TransmissionRecord).where(
                social_db.TransmissionRecord.world_id == WORLD_ID
            )
        )
        await session.execute(
            delete(social_db.MessageRecord).where(social_db.MessageRecord.world_id == WORLD_ID)
        )
        await session.execute(
            delete(social_db.CommunicationChannelRecord).where(
                social_db.CommunicationChannelRecord.world_id == WORLD_ID
            )
        )
        await session.execute(
            delete(runtime_db.AgentWakeRecord).where(
                runtime_db.AgentWakeRecord.world_id == WORLD_ID,
                runtime_db.AgentWakeRecord.id.like("wake-transmission-%"),
            )
        )
        await session.execute(
            delete(db.ObservationRecord).where(
                db.ObservationRecord.world_id == WORLD_ID,
                db.ObservationRecord.id.like("obs-transmission-%"),
            )
        )
        await session.commit()


async def test_three_branches_restart_two_workers_and_correction() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
            world = await session.get(db.WorldRecord, WORLD_ID)
            assert world is not None
            runtime = await session.get(
                runtime_db.WorldRuntimeRecord, WORLD_ID, with_for_update=True
            )
            if runtime is None:
                runtime = runtime_db.WorldRuntimeRecord(
                    world_id=WORLD_ID,
                    status="running",
                    current_world_time=world.current_time,
                    generation=1,
                )
                session.add(runtime)
            else:
                runtime.status = "running"
                runtime.current_world_time = world.current_time
            await session.commit()
        await reset_social(database)

        first = SocialRuntimeService(database.session_factory)
        await first.seed_scenario()
        await asyncio.gather(first.deliver_due(), first.deliver_due())
        assert [item.agent_id for item in await first.beliefs()] == [LIN_ID]

        async with database.session_factory() as session:
            runtime = await session.get(
                runtime_db.WorldRuntimeRecord, WORLD_ID, with_for_update=True
            )
            assert runtime is not None
            runtime.current_world_time += timedelta(minutes=20)
            await session.commit()

        restarted = SocialRuntimeService(database.session_factory)
        await asyncio.gather(restarted.deliver_due(), restarted.deliver_due())
        beliefs = await restarted.beliefs()
        assert {item.agent_id: item.value for item in beliefs} == {
            LIN_ID: "north gate closes at 12:00",
            ZHOU_ID: "north gate closes at 12:00",
            CHEN_ID: "all gates may close at 11:30",
        }
        await restarted.open_correction_dialogue()

        for _ in range(2):
            async with database.session_factory() as session:
                runtime = await session.get(
                    runtime_db.WorldRuntimeRecord, WORLD_ID, with_for_update=True
                )
                assert runtime is not None
                runtime.current_world_time += timedelta(minutes=5)
                await session.commit()
            await SocialRuntimeService(database.session_factory).deliver_due()

        chen = await restarted.beliefs(CHEN_ID)
        assert chen[-1].value == "north gate closes at 12:00"
        assert chen[-1].reason_code == "HIGHER_RELIABILITY_CORRECTION"
        conversation = (await restarted.conversations())[0]
        assert conversation.state == "completed"
        assert conversation.terminal_reason == "correction_delivered"
        assert conversation.turn_count == 2

        async with database.session_factory() as session:
            counts = (
                await session.scalar(
                    select(func.count())
                    .select_from(social_db.TransmissionRecord)
                    .where(social_db.TransmissionRecord.status == "delivered")
                ),
                await session.scalar(
                    select(func.count())
                    .select_from(db.ObservationRecord)
                    .where(db.ObservationRecord.id.like("obs-transmission-%"))
                ),
                await session.scalar(
                    select(func.count())
                    .select_from(social_db.BeliefEvidenceRecord)
                    .where(social_db.BeliefEvidenceRecord.world_id == WORLD_ID)
                ),
            )
            assert counts == (5, 5, 5)
    finally:
        await database.dispose()
