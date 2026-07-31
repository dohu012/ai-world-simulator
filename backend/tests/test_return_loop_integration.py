import os

import pytest
from sqlalchemy import delete, func, select

from app.application.return_loop_service import ReturnLoopService
from app.infrastructure.database import return_loop_models as rr
from app.infrastructure.database.session import Database

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")


@pytest.mark.asyncio
async def test_projection_is_idempotent_owner_isolated_and_mutable() -> None:
    database = Database("postgresql+asyncpg://simulator:simulator@localhost:5432/simulator")
    owner = "char-chen-mo"
    service = ReturnLoopService(database.session_factory)
    async with database.session_factory.begin() as session:
        await session.execute(
            delete(rr.PlaytestEventRecord).where(rr.PlaytestEventRecord.owner_id == owner)
        )
        await session.execute(
            delete(rr.InboxItemRecord).where(rr.InboxItemRecord.owner_id == owner)
        )
        await session.execute(
            delete(rr.OfflineSummaryClaimRecord).where(
                rr.OfflineSummaryClaimRecord.owner_id == owner
            )
        )
        await session.execute(
            delete(rr.OfflineSummaryRecord).where(rr.OfflineSummaryRecord.owner_id == owner)
        )
        await session.execute(
            delete(rr.OfflineIntervalRecord).where(rr.OfflineIntervalRecord.owner_id == owner)
        )
        await session.execute(
            delete(rr.NotificationPreferenceRecord).where(
                rr.NotificationPreferenceRecord.owner_id == owner
            )
        )
    try:
        first = await service.state(owner)
        second = await service.state(owner)
        assert first.summary.source_watermark == second.summary.source_watermark
        assert first.inbox[0].id == second.inbox[0].id
        async with database.session_factory() as session:
            inbox_count = await session.scalar(
                select(func.count())
                .select_from(rr.InboxItemRecord)
                .where(rr.InboxItemRecord.owner_id == owner)
            )
            claim_count = await session.scalar(
                select(func.count())
                .select_from(rr.OfflineSummaryClaimRecord)
                .where(rr.OfflineSummaryClaimRecord.owner_id == owner)
            )
        assert inbox_count == 1
        assert claim_count == 4
        assert await service.mark(owner, first.inbox[0].id, "read")
        assert not await service.mark(owner, first.inbox[0].id, "read")
        assert not await service.mark("char-lin-zhixia", first.inbox[0].id, "dismiss")
        await service.record_event(owner, "summary_view", "return-test-once")
        await service.record_event(owner, "summary_view", "return-test-once")
        async with database.session_factory() as session:
            event_count = await session.scalar(
                select(func.count())
                .select_from(rr.PlaytestEventRecord)
                .where(
                    rr.PlaytestEventRecord.owner_id == owner,
                    rr.PlaytestEventRecord.idempotency_key == "return-test-once",
                )
            )
        assert event_count == 1
    finally:
        await database.dispose()
