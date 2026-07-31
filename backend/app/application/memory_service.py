"""Exactly-once memory admission, derived embedding work, and owner-safe retrieval."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.gray_harbor import WORLD_ID
from app.domain.memory import (
    EMBEDDING_REVISION,
    RETRIEVAL_POLICY_VERSION,
    EmotionalMemory,
    EpisodicMemory,
    EpistemicStatus,
    ImportanceFeatures,
    MemoryItem,
    MemoryType,
    OracleMemory,
    RetrievalRequest,
    ScoreComponents,
    SemanticMemory,
    SourceReference,
    StageSummaryMemory,
    admission_score,
    context_watermark,
    deterministic_embedding,
    pack_context,
    retrieve,
    should_admit,
)
from app.domain.observation import Observation
from app.infrastructure.database import memory_models as mr
from app.infrastructure.database import models as r
from app.infrastructure.database import runtime_models as rr


class MemoryRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    memory_type: str
    summary: str
    occurred_at: datetime
    importance: float
    confidence: float
    source_count: int
    embedding_status: str
    superseded: bool


class CandidateRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    memory: MemoryRead
    rank: int
    selected: bool
    exclusion_reason: str
    scores: ScoreComponents


class RetrievalRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    policy_version: str
    mode: str
    context_watermark: str
    character_budget: int
    characters_used: int
    candidates: list[CandidateRead]


class MemorySyncRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    examined: int
    admitted: int
    rejected: int
    deduplicated: int
    jobs_created: int


class ConsolidationRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    memory_id: str | None
    source_count: int
    idempotent_replay: bool


class EmbeddingOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    vector: list[float] | None = None
    failure_code: str | None = None
    latency_ms: int = 0


EmbeddingProvider = Callable[[str], Awaitable[EmbeddingOutcome]]


async def deterministic_embedding_provider(text: str) -> EmbeddingOutcome:
    return EmbeddingOutcome(vector=deterministic_embedding(text), latency_ms=0)


def classify_embedding_failure(failure_code: str) -> str:
    if failure_code in {
        "EMBEDDING_TIMEOUT",
        "EMBEDDING_RATE_LIMITED",
        "EMBEDDING_PROVIDER_UNAVAILABLE",
    }:
        return "transient"
    return "permanent"


def _observation_summary(observation: Observation) -> str:
    parts = [
        *(entity.description or entity.name for entity in observation.visible_entities),
        *(statement.content for statement in observation.heard_statements),
        *(message.content for message in observation.received_messages),
        *(change.description for change in observation.felt_changes),
    ]
    safe = " ".join(part.strip() for part in parts if part.strip())
    return safe[:2000] or f"I experienced an {observation.observation_type.value} observation."


def _features(observation: Observation, summary: str) -> ImportanceFeatures:
    normalized = summary.casefold()
    important = {
        "medicine": ("medicine", "药", "ill", "injur"),
        "resource": ("ration", "food", "shipment", "cache", "resource", "配给"),
        "irreversible": ("rescue", "death", "surviv", "abandon", "rejected", "救援"),
        "goal": ("plan", "goal", "clinic", "checkpoint", "计划"),
        "oracle": ("oracle", "advice", "silence", "神谕"),
    }

    def hit(group: str) -> float:
        return 1.0 if any(term in normalized for term in important[group]) else 0.0

    intensity = max((change.intensity for change in observation.felt_changes), default=0.0)
    return ImportanceFeatures(
        goal_change=hit("goal") * 0.8,
        personal_risk=max(intensity, hit("medicine") * 0.7),
        resource_impact=hit("resource"),
        irreversible=hit("irreversible"),
        oracle_relevance=max(hit("oracle"), float(observation.observation_type.value == "oracle")),
        novelty=0.8,
    )


def _parse_memory(payload: object) -> MemoryItem:
    raw = json.dumps(payload)
    data = payload if isinstance(payload, dict) else {}
    memory_type = data.get("memory_type")
    contracts: dict[object, type[MemoryItem]] = {
        MemoryType.EPISODIC.value: EpisodicMemory,
        MemoryType.SEMANTIC.value: SemanticMemory,
        MemoryType.EMOTIONAL.value: EmotionalMemory,
        MemoryType.ORACLE.value: OracleMemory,
        MemoryType.STAGE_SUMMARY.value: StageSummaryMemory,
    }
    contract = contracts.get(memory_type, MemoryItem)
    return contract.model_validate_json(raw)


class MemoryApplicationService:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        *,
        embedding_provider: EmbeddingProvider = deterministic_embedding_provider,
        max_embedding_attempts: int = 2,
    ) -> None:
        self.sessions = sessions
        self.embedding_provider = embedding_provider
        self.max_embedding_attempts = max_embedding_attempts

    async def sync_observations(self) -> MemorySyncRead:
        """Admit eligible owner-visible observations; never calls a model."""
        async with self.sessions() as session:
            observations = list(
                (
                    await session.scalars(
                        select(r.ObservationRecord)
                        .where(r.ObservationRecord.world_id == WORLD_ID)
                        .order_by(
                            r.ObservationRecord.observed_at,
                            r.ObservationRecord.agent_id,
                            r.ObservationRecord.id,
                        )
                    )
                ).all()
            )
            admitted = rejected = deduplicated = jobs = 0
            for row in observations:
                observation = Observation.model_validate_json(json.dumps(row.payload))
                summary = _observation_summary(observation)
                features = _features(observation, summary)
                accepted, reason = should_admit(features)
                logical_key = sha256(
                    f"{row.world_id}:{row.agent_id}:observation:{row.id}".encode()
                ).hexdigest()
                memory_id = f"memory-{logical_key[:24]}"
                if await session.get(mr.MemoryItemRecord, memory_id) is not None:
                    deduplicated += 1
                    continue
                if not accepted:
                    rejected += 1
                    continue
                score = admission_score(features)
                episodic = EpisodicMemory(
                    id=memory_id,
                    world_id=row.world_id,
                    owner_id=row.agent_id,
                    memory_type=MemoryType.EPISODIC,
                    summary=summary,
                    occurred_at=row.observed_at,
                    sources=[
                        SourceReference(
                            source_type="observation",
                            source_id=row.id,
                            world_id=row.world_id,
                            owner_id=row.agent_id,
                        )
                    ],
                    involved_entity_ids=[
                        entity.entity.entity_id for entity in observation.visible_entities
                    ],
                    location_ids=[],
                    goal_ids=[],
                    plan_ids=[],
                    emotion_labels=[],
                    emotion_intensity=max(
                        (change.intensity for change in observation.felt_changes), default=0.0
                    ),
                    importance_features=features,
                    admission_score=score,
                    confidence=1.0,
                    epistemic_status=EpistemicStatus.OBSERVED,
                    policy_version="memory-admission-v1",
                    version=1,
                    schema_version="1.0",
                )
                memory: MemoryItem = episodic
                if observation.observation_type.value == "oracle":
                    oracle_window = await session.scalar(
                        select(rr.OracleWindowRecord).where(
                            rr.OracleWindowRecord.delivered_observation_id == observation.id
                        )
                    )
                    chosen_action_id: str | None = None
                    outcome_event_id: str | None = observation.source_event_id
                    outcome_summary: str | None = None
                    if oracle_window is not None and oracle_window.final_decision_id is not None:
                        decision = await session.get(
                            r.AgentDecisionRecord, oracle_window.final_decision_id
                        )
                        if decision is not None:
                            chosen_action_id = decision.action_intent_id
                            if chosen_action_id is not None:
                                result = await session.scalar(
                                    select(r.ActionResultRecord).where(
                                        r.ActionResultRecord.action_id == chosen_action_id
                                    )
                                )
                                if result is not None:
                                    event_ids = result.payload.get("generated_event_ids", [])
                                    if isinstance(event_ids, list) and event_ids:
                                        outcome_event_id = str(event_ids[0])
                                    outcome_summary = (
                                        str(result.payload.get("consequence_summary", ""))[:2000]
                                        or None
                                    )
                    payload = episodic.model_dump(mode="json")
                    if oracle_window is not None:
                        payload["sources"].append(
                            SourceReference(
                                source_type="oracle",
                                source_id=oracle_window.id,
                                world_id=row.world_id,
                                owner_id=row.agent_id,
                            ).model_dump(mode="json")
                        )
                    payload.update(
                        {
                            "memory_type": MemoryType.ORACLE.value,
                            "advice_observation_id": observation.id,
                            "silence_reason": None,
                            "interpretation": summary,
                            "chosen_action_id": chosen_action_id,
                            "outcome_event_id": outcome_event_id,
                            "outcome_summary": outcome_summary,
                        }
                    )
                    memory = OracleMemory.model_validate_json(json.dumps(payload))
                elif episodic.emotion_intensity >= 0.7:
                    payload = episodic.model_dump(mode="json")
                    payload.update(
                        {
                            "memory_type": MemoryType.EMOTIONAL.value,
                            "association": summary,
                        }
                    )
                    memory = EmotionalMemory.model_validate_json(json.dumps(payload))
                elif observation.heard_statements:
                    payload = episodic.model_dump(mode="json")
                    payload.update(
                        {
                            "memory_type": MemoryType.SEMANTIC.value,
                            "epistemic_status": EpistemicStatus.SUBJECTIVE.value,
                            "subject": "heard_claim",
                            "predicate": "states",
                            "object": observation.heard_statements[0].content[:256],
                            "valid_from": observation.observed_at.isoformat(),
                            "valid_until": None,
                            "supporting_memory_ids": [],
                            "contradicting_memory_ids": [],
                            "last_reinforced_at": observation.observed_at.isoformat(),
                        }
                    )
                    memory = SemanticMemory.model_validate_json(json.dumps(payload))
                session.add(
                    mr.MemoryItemRecord(
                        id=memory.id,
                        world_id=memory.world_id,
                        owner_id=memory.owner_id,
                        logical_key=logical_key,
                        memory_type=memory.memory_type.value,
                        summary=memory.summary,
                        occurred_at=memory.occurred_at,
                        ended_at=None,
                        admission_score=memory.admission_score,
                        confidence=memory.confidence,
                        policy_version=memory.policy_version,
                        version=memory.version,
                        metadata_payload={
                            "contract": memory.model_dump(mode="json"),
                            "admission_reason": reason,
                        },
                    )
                )
                if isinstance(memory, OracleMemory) and len(memory.sources) > 1:
                    oracle_source = memory.sources[1]
                    session.add(
                        mr.MemorySourceRecord(
                            id=f"source-{memory.id}-{oracle_source.source_id}",
                            memory_id=memory.id,
                            world_id=row.world_id,
                            owner_id=row.agent_id,
                            source_type=oracle_source.source_type,
                            source_id=oracle_source.source_id,
                        )
                    )
                await session.flush()
                session.add(
                    mr.MemorySourceRecord(
                        id=f"source-{memory.id}-{row.id}",
                        memory_id=memory.id,
                        world_id=row.world_id,
                        owner_id=row.agent_id,
                        source_type="observation",
                        source_id=row.id,
                    )
                )
                session.add(
                    mr.MemoryEmbeddingJobRecord(
                        id=f"embedding-job-{memory.id}-{EMBEDDING_REVISION}",
                        memory_id=memory.id,
                        model_revision=EMBEDDING_REVISION,
                        status="pending",
                        attempts=0,
                        claim_token=0,
                    )
                )
                admitted += 1
                jobs += 1
            await session.commit()
            return MemorySyncRead(
                examined=len(observations),
                admitted=admitted,
                rejected=rejected,
                deduplicated=deduplicated,
                jobs_created=jobs,
            )

    async def process_embedding_jobs(self, *, worker_id: str, limit: int = 32) -> int:
        """Claim and finish deterministic embedding jobs with fencing in one short transaction."""
        now = datetime.now(UTC)
        async with self.sessions() as session:
            jobs = list(
                (
                    await session.scalars(
                        select(mr.MemoryEmbeddingJobRecord)
                        .where(
                            mr.MemoryEmbeddingJobRecord.status.in_(["pending", "retry"]),
                            (
                                mr.MemoryEmbeddingJobRecord.retry_at.is_(None)
                                | (mr.MemoryEmbeddingJobRecord.retry_at <= now)
                            ),
                        )
                        .order_by(mr.MemoryEmbeddingJobRecord.id)
                        .limit(max(1, min(limit, 32)))
                        .with_for_update(skip_locked=True)
                    )
                ).all()
            )
            for job in jobs:
                job.status = "claimed"
                job.claim_owner = worker_id
                job.claim_token += 1
                job.attempts += 1
                job.lease_expires_at = now + timedelta(seconds=60)
            await session.commit()

        completed = 0
        for claimed in jobs:
            memory_text: str | None = None
            async with self.sessions() as session:
                current_job = await session.get(mr.MemoryEmbeddingJobRecord, claimed.id)
                if (
                    current_job is None
                    or current_job.status != "claimed"
                    or current_job.claim_owner != worker_id
                    or current_job.claim_token != claimed.claim_token
                ):
                    continue
                memory = await session.get(mr.MemoryItemRecord, current_job.memory_id)
                assert memory is not None
                memory_text = memory.summary

            assert memory_text is not None
            outcome = await self.embedding_provider(memory_text)

            async with self.sessions() as session:
                current_job = await session.get(
                    mr.MemoryEmbeddingJobRecord, claimed.id, with_for_update=True
                )
                if (
                    current_job is None
                    or current_job.status != "claimed"
                    or current_job.claim_owner != worker_id
                    or current_job.claim_token != claimed.claim_token
                ):
                    continue
                if outcome.failure_code is not None:
                    current_job.failure_code = outcome.failure_code
                    current_job.lease_expires_at = None
                    if (
                        classify_embedding_failure(outcome.failure_code) == "transient"
                        and current_job.attempts < self.max_embedding_attempts
                    ):
                        current_job.status = "retry"
                        current_job.retry_at = now + timedelta(
                            seconds=2 ** max(0, current_job.attempts - 1)
                        )
                    else:
                        current_job.status = "dead"
                        current_job.retry_at = None
                    await session.commit()
                    continue
                vector = outcome.vector
                if vector is None:
                    current_job.status = "dead"
                    current_job.failure_code = "EMBEDDING_OUTPUT_INVALID"
                    current_job.lease_expires_at = None
                    await session.commit()
                    continue
                content_hash = sha256(memory_text.encode()).hexdigest()
                await session.execute(
                    insert(mr.MemoryEmbeddingRecord)
                    .values(
                        id=f"embedding-{memory.id}-{EMBEDDING_REVISION}",
                        memory_id=memory.id,
                        provider="deterministic-fake",
                        model="sha256-normalized",
                        model_revision=EMBEDDING_REVISION,
                        dimensions=len(vector),
                        content_hash=content_hash,
                        vector=vector,
                        active=True,
                        metrics={
                            "tokens": 0,
                            "cost_usd": 0.0,
                            "latency_ms": outcome.latency_ms,
                        },
                    )
                    .on_conflict_do_nothing(
                        index_elements=["memory_id", "model_revision", "content_hash"]
                    )
                )
                current_job.status = "completed"
                current_job.lease_expires_at = None
                current_job.failure_code = None
                await session.commit()
                completed += 1
        return completed

    async def memories(self, owner_id: str) -> list[MemoryRead]:
        async with self.sessions() as session:
            rows = list(
                (
                    await session.scalars(
                        select(mr.MemoryItemRecord)
                        .where(
                            mr.MemoryItemRecord.world_id == WORLD_ID,
                            mr.MemoryItemRecord.owner_id == owner_id,
                        )
                        .order_by(mr.MemoryItemRecord.occurred_at.desc(), mr.MemoryItemRecord.id)
                    )
                ).all()
            )
            return [await self._read(session, row) for row in rows]

    async def consolidate_stage(self, owner_id: str) -> ConsolidationRead:
        """Create one bounded, regenerable summary without deleting raw memories."""
        async with self.sessions() as session:
            rows = list(
                (
                    await session.scalars(
                        select(mr.MemoryItemRecord)
                        .where(
                            mr.MemoryItemRecord.world_id == WORLD_ID,
                            mr.MemoryItemRecord.owner_id == owner_id,
                            mr.MemoryItemRecord.memory_type != MemoryType.STAGE_SUMMARY.value,
                            mr.MemoryItemRecord.tombstoned_at.is_(None),
                        )
                        .order_by(mr.MemoryItemRecord.occurred_at, mr.MemoryItemRecord.id)
                        .limit(32)
                    )
                ).all()
            )
            if not rows:
                return ConsolidationRead(memory_id=None, source_count=0, idempotent_replay=False)
            source_digest = sha256("\x1f".join(row.id for row in rows).encode()).hexdigest()
            summary_id = f"memory-stage-{owner_id}-{source_digest[:16]}"
            if await session.get(mr.MemoryItemRecord, summary_id) is not None:
                return ConsolidationRead(
                    memory_id=summary_id,
                    source_count=len(rows),
                    idempotent_replay=True,
                )
            summary_text = " | ".join(row.summary for row in rows)
            summary_text = summary_text[:2000]
            occurred_at = max(row.occurred_at for row in rows)
            features = ImportanceFeatures(goal_change=0.8, irreversible=0.5, novelty=0.8)
            contract = StageSummaryMemory(
                id=summary_id,
                world_id=WORLD_ID,
                owner_id=owner_id,
                memory_type=MemoryType.STAGE_SUMMARY,
                summary=summary_text,
                occurred_at=occurred_at,
                sources=[
                    SourceReference(
                        source_type="memory",
                        source_id=row.id,
                        world_id=WORLD_ID,
                        owner_id=owner_id,
                    )
                    for row in rows
                ],
                importance_features=features,
                admission_score=admission_score(features),
                confidence=min(row.confidence for row in rows),
                epistemic_status=EpistemicStatus.SUBJECTIVE,
                policy_version="memory-consolidation-v1",
                model_revision="deterministic-summary-v1",
                version=1,
                schema_version="1.0",
                stage_id="gray-harbor-crisis-stage-1",
                contributing_memory_ids=[row.id for row in rows],
                unresolved_contradiction_ids=[],
                token_estimate=max(1, min(600, len(summary_text) // 4)),
            )
            session.add(
                mr.MemoryItemRecord(
                    id=summary_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    logical_key=source_digest,
                    memory_type=MemoryType.STAGE_SUMMARY.value,
                    summary=summary_text,
                    occurred_at=occurred_at,
                    admission_score=contract.admission_score,
                    confidence=contract.confidence,
                    policy_version=contract.policy_version,
                    version=1,
                    metadata_payload={"contract": contract.model_dump(mode="json")},
                )
            )
            await session.flush()
            for row in rows:
                session.add(
                    mr.MemorySourceRecord(
                        id=f"source-{summary_id}-{row.id}",
                        memory_id=summary_id,
                        world_id=WORLD_ID,
                        owner_id=owner_id,
                        source_type="memory",
                        source_id=row.id,
                    )
                )
            await session.commit()
            return ConsolidationRead(
                memory_id=summary_id,
                source_count=len(rows),
                idempotent_replay=False,
            )

    async def retrieve_for_owner(
        self,
        owner_id: str,
        *,
        query: str,
        cutoff: datetime,
        final_k: int = 6,
        trace_key: str = "adhoc",
    ) -> RetrievalRead:
        async with self.sessions() as session:
            rows = list(
                (
                    await session.scalars(
                        select(mr.MemoryItemRecord).where(
                            mr.MemoryItemRecord.world_id == WORLD_ID,
                            mr.MemoryItemRecord.owner_id == owner_id,
                            mr.MemoryItemRecord.occurred_at <= cutoff,
                            mr.MemoryItemRecord.tombstoned_at.is_(None),
                        )
                    )
                ).all()
            )
            memories = [_parse_memory(row.metadata_payload["contract"]) for row in rows]
            embedding_rows = list(
                (
                    await session.scalars(
                        select(mr.MemoryEmbeddingRecord).where(
                            mr.MemoryEmbeddingRecord.memory_id.in_([item.id for item in memories]),
                            mr.MemoryEmbeddingRecord.active.is_(True),
                            mr.MemoryEmbeddingRecord.model_revision == EMBEDDING_REVISION,
                        )
                    )
                ).all()
            )
            embedding_map = {
                row.memory_id: [float(value) for value in row.vector] for row in embedding_rows
            }
            mode = "hybrid" if embedding_map else "lexical_structured_fallback"
            request = RetrievalRequest(
                world_id=WORLD_ID,
                owner_id=owner_id,
                decision_world_time=cutoff,
                query_text=query,
                final_k=final_k,
                character_budget=4000,
            )
            ranked = retrieve(memories, request, embeddings=embedding_map or None)
            selected, reasons, used = pack_context(
                ranked, final_k=request.final_k, character_budget=request.character_budget
            )
            selected_ids = {item.id for item in selected}
            watermark = context_watermark([], selected, cutoff=cutoff, retrieval_mode=mode)
            retrieval_id = (
                "retrieval-"
                + sha256(
                    f"{trace_key}:{owner_id}:{cutoff.isoformat()}:{query}:{watermark}".encode()
                ).hexdigest()[:24]
            )
            await session.execute(
                insert(mr.MemoryRetrievalRunRecord)
                .values(
                    id=retrieval_id,
                    decision_id=None,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    cutoff=cutoff,
                    policy_version=RETRIEVAL_POLICY_VERSION,
                    embedding_revision=EMBEDDING_REVISION if embedding_map else None,
                    mode=mode,
                    context_watermark=watermark,
                    token_budget=request.character_budget,
                    token_used=used,
                )
                .on_conflict_do_nothing()
            )
            candidates: list[CandidateRead] = []
            for rank, (memory, scores) in enumerate(ranked, 1):
                await session.execute(
                    insert(mr.MemoryRetrievalCandidateRecord)
                    .values(
                        id=f"{retrieval_id}:{memory.id}",
                        retrieval_id=retrieval_id,
                        memory_id=memory.id,
                        rank=rank,
                        selected=memory.id in selected_ids,
                        exclusion_reason=reasons[memory.id],
                        score_components=scores.model_dump(mode="json"),
                    )
                    .on_conflict_do_nothing()
                )
                row = next(item for item in rows if item.id == memory.id)
                candidates.append(
                    CandidateRead(
                        memory=await self._read(session, row),
                        rank=rank,
                        selected=memory.id in selected_ids,
                        exclusion_reason=reasons[memory.id],
                        scores=scores,
                    )
                )
            await session.commit()
            return RetrievalRead(
                id=retrieval_id,
                policy_version=RETRIEVAL_POLICY_VERSION,
                mode=mode,
                context_watermark=watermark,
                character_budget=request.character_budget,
                characters_used=used,
                candidates=candidates,
            )

    async def latest_retrieval(self, owner_id: str) -> RetrievalRead | None:
        async with self.sessions() as session:
            run = await session.scalar(
                select(mr.MemoryRetrievalRunRecord)
                .where(
                    mr.MemoryRetrievalRunRecord.world_id == WORLD_ID,
                    mr.MemoryRetrievalRunRecord.owner_id == owner_id,
                )
                .order_by(
                    mr.MemoryRetrievalRunRecord.created_at.desc(),
                    mr.MemoryRetrievalRunRecord.id.desc(),
                )
                .limit(1)
            )
            if run is None:
                return None
            rows = list(
                (
                    await session.scalars(
                        select(mr.MemoryRetrievalCandidateRecord)
                        .where(mr.MemoryRetrievalCandidateRecord.retrieval_id == run.id)
                        .order_by(mr.MemoryRetrievalCandidateRecord.rank)
                    )
                ).all()
            )
            candidates: list[CandidateRead] = []
            for row in rows:
                memory = await session.get(mr.MemoryItemRecord, row.memory_id)
                assert memory is not None
                candidates.append(
                    CandidateRead(
                        memory=await self._read(session, memory),
                        rank=row.rank,
                        selected=row.selected,
                        exclusion_reason=row.exclusion_reason,
                        scores=ScoreComponents.model_validate(row.score_components),
                    )
                )
            return RetrievalRead(
                id=run.id,
                policy_version=run.policy_version,
                mode=run.mode,
                context_watermark=run.context_watermark,
                character_budget=run.token_budget,
                characters_used=run.token_used,
                candidates=candidates,
            )

    @staticmethod
    async def _read(session: AsyncSession, row: mr.MemoryItemRecord) -> MemoryRead:
        source_count = len(
            list(
                (
                    await session.scalars(
                        select(mr.MemorySourceRecord.id).where(
                            mr.MemorySourceRecord.memory_id == row.id
                        )
                    )
                ).all()
            )
        )
        read_job = await session.scalar(
            select(mr.MemoryEmbeddingJobRecord).where(
                mr.MemoryEmbeddingJobRecord.memory_id == row.id
            )
        )
        return MemoryRead(
            id=row.id,
            memory_type=row.memory_type,
            summary=row.summary,
            occurred_at=row.occurred_at,
            importance=row.admission_score,
            confidence=row.confidence,
            source_count=source_count,
            embedding_status=read_job.status if read_job is not None else "fallback_only",
            superseded=row.supersedes_id is not None,
        )
