import os
from asyncio import gather

import pytest
from sqlalchemy import delete, func, select

from app.application.evolution_service import EvolutionApplicationService
from app.application.memory_service import MemoryApplicationService
from app.core.config import Settings
from app.infrastructure.database import evolution_models as er
from app.infrastructure.database.session import Database
from app.services.seed_gray_harbor import seed_gray_harbor

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")


async def clear_evolution(database: Database) -> None:
    async with database.session_factory() as session:
        await session.execute(delete(er.evolution_evidence_links))
        await session.execute(delete(er.evolution_deltas))
        await session.execute(delete(er.reflection_jobs))
        await session.execute(delete(er.relationship_snapshots))
        await session.execute(delete(er.identity_snapshots))
        await session.execute(delete(er.identity_baselines))
        await session.commit()


async def test_two_workers_commit_once_and_edges_are_owner_isolated() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
        await clear_evolution(database)
        await MemoryApplicationService(database.session_factory).sync_observations()
        service = EvolutionApplicationService(database.session_factory)
        first, second = await gather(
            service.reflect("char-chen-mo"),
            service.reflect("char-chen-mo"),
        )
        assert {first.idempotent_replay, second.idempotent_replay} == {False, True}
        state = await service.state("char-chen-mo")
        assert state.baseline.generation == 1
        assert state.identity.version >= 1
        assert state.relationships
        assert all(item.target_id != "char-lin-zhixia" for item in state.relationships)
        lin = await service.state("char-lin-zhixia")
        assert lin.context_watermark != state.context_watermark
        async with database.session_factory() as session:
            jobs = await session.scalar(select(func.count()).select_from(er.reflection_jobs))
            assert jobs == 1
    finally:
        await database.dispose()
