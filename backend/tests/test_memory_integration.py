import os
from asyncio import gather

import pytest
from sqlalchemy import delete, func, select

from app.application.memory_service import EmbeddingOutcome, MemoryApplicationService
from app.core.config import Settings
from app.infrastructure.database import evolution_models as er
from app.infrastructure.database import memory_models as mr
from app.infrastructure.database.session import Database
from app.services.seed_gray_harbor import seed_gray_harbor

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")


async def clear_memory(database: Database) -> None:
    async with database.session_factory() as session:
        await session.execute(delete(er.evolution_evidence_links))
        await session.execute(delete(er.evolution_deltas))
        await session.execute(delete(er.reflection_jobs))
        await session.execute(delete(er.relationship_snapshots))
        await session.execute(delete(er.identity_snapshots))
        await session.execute(delete(er.identity_baselines))
        await session.execute(delete(mr.MemoryRetrievalCandidateRecord))
        await session.execute(delete(mr.MemoryRetrievalRunRecord))
        await session.execute(delete(mr.MemoryEmbeddingRecord))
        await session.execute(delete(mr.MemoryEmbeddingJobRecord))
        await session.execute(delete(mr.MemorySourceRecord))
        await session.execute(delete(mr.MemoryItemRecord))
        await session.commit()


async def test_exact_once_admission_two_worker_embedding_and_owner_filter() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
        await clear_memory(database)
        service = MemoryApplicationService(database.session_factory)
        first = await service.sync_observations()
        replay = await service.sync_observations()
        assert first.admitted > 0
        assert replay.admitted == 0
        assert replay.deduplicated == first.admitted

        completed = await gather(
            service.process_embedding_jobs(worker_id="worker-a"),
            service.process_embedding_jobs(worker_id="worker-b"),
        )
        assert sum(completed) == first.admitted
        async with database.session_factory() as session:
            assert (
                await session.scalar(select(func.count()).select_from(mr.MemoryEmbeddingRecord))
                == first.admitted
            )
            memory_types = set(
                (await session.scalars(select(mr.MemoryItemRecord.memory_type))).all()
            )
            assert "episodic" in memory_types
            assert memory_types <= {"episodic", "semantic", "emotional", "oracle"}

        chen = await service.memories("char-chen-mo")
        lin = await service.memories("char-lin-zhixia")
        assert chen and lin
        cutoff = max(item.occurred_at for item in chen)
        trace = await service.retrieve_for_owner(
            "char-chen-mo",
            query="clinic medicine food shipment",
            cutoff=cutoff,
            trace_key="integration-owner-filter",
        )
        assert trace.mode == "hybrid"
        assert trace.candidates
        chen_ids = {item.id for item in chen}
        assert all(candidate.memory.id in chen_ids for candidate in trace.candidates)
        assert not ({item.id for item in lin} & {item.memory.id for item in trace.candidates})
    finally:
        await database.dispose()


async def test_consolidation_is_idempotent_and_preserves_raw_sources() -> None:
    database = Database(Settings().database_url)
    try:
        service = MemoryApplicationService(database.session_factory)
        await service.sync_observations()
        before = await service.memories("char-chen-mo")
        first = await service.consolidate_stage("char-chen-mo")
        replay = await service.consolidate_stage("char-chen-mo")
        after = await service.memories("char-chen-mo")
        assert first.memory_id is not None
        assert replay.idempotent_replay is True
        assert replay.memory_id == first.memory_id
        assert len(after) == len(before) + 1
        assert all(item.id in {current.id for current in after} for item in before)
    finally:
        await database.dispose()


async def test_provider_failure_is_durable_and_inference_holds_no_job_lock() -> None:
    database = Database(Settings().database_url)

    async def unavailable(_text: str) -> EmbeddingOutcome:
        async with database.session_factory() as probe:
            unlocked = await probe.scalar(
                select(mr.MemoryEmbeddingJobRecord.id)
                .where(mr.MemoryEmbeddingJobRecord.status == "claimed")
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            assert unlocked is not None
            await probe.rollback()
        return EmbeddingOutcome(failure_code="EMBEDDING_PROVIDER_UNAVAILABLE")

    try:
        await clear_memory(database)
        service = MemoryApplicationService(database.session_factory, embedding_provider=unavailable)
        seeded = await service.sync_observations()
        assert seeded.admitted > 0
        assert await service.process_embedding_jobs(worker_id="failure-worker", limit=1) == 0
        async with database.session_factory() as session:
            job = await session.scalar(
                select(mr.MemoryEmbeddingJobRecord)
                .where(mr.MemoryEmbeddingJobRecord.failure_code.is_not(None))
                .limit(1)
            )
            assert job is not None
            assert job.status == "retry"
            assert job.failure_code == "EMBEDDING_PROVIDER_UNAVAILABLE"
            assert job.retry_at is not None

        memories = await service.memories("char-chen-mo")
        cutoff = max(item.occurred_at for item in memories)
        trace = await service.retrieve_for_owner(
            "char-chen-mo",
            query="clinic",
            cutoff=cutoff,
            trace_key="provider-outage-fallback",
        )
        assert trace.mode == "lexical_structured_fallback"
        assert trace.candidates
    finally:
        await database.dispose()
