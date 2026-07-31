"""Deterministic fixed-corpus execution against the production retrieval policy."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.domain.memory import (
    EpisodicMemory,
    EpistemicStatus,
    EvaluationCaseResult,
    EvaluationMetrics,
    ImportanceFeatures,
    MemoryItem,
    MemoryType,
    RetrievalRequest,
    SourceReference,
    admission_score,
    deterministic_embedding,
    evaluate_rankings,
    pack_context,
    retrieve,
)

CORPUS_PATH = Path(__file__).parents[1] / "scenarios" / "gray_harbor_memory_eval_v1.json"
WORLD_ID = "world-gray-harbor-lockdown"
BASE_TIME = datetime(2026, 7, 23, tzinfo=UTC)


class EvaluationModeRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    mode: str
    metrics: EvaluationMetrics
    failed_case_ids: list[str]


class MemoryEvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    corpus_version: str
    case_count: int
    hybrid: EvaluationModeRead
    fallback: EvaluationModeRead


class EvaluationFixtureCase(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    owner_id: str
    cutoff_day: int
    query: str
    required: list[str]
    relevant: list[str]
    optional: list[str]
    forbidden: list[str]
    maximum_k: int
    character_budget: int
    lanes: list[str]
    fallback: str


class EvaluationFixture(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    version: str
    thresholds: dict[str, float | int]
    cases: list[EvaluationFixtureCase]


def _memory(
    identifier: str,
    *,
    owner_id: str,
    summary: str,
    occurred_at: datetime,
    world_id: str = WORLD_ID,
) -> EpisodicMemory:
    features = ImportanceFeatures(resource_impact=0.8, novelty=0.9)
    return EpisodicMemory(
        id=identifier,
        world_id=world_id,
        owner_id=owner_id,
        memory_type=MemoryType.EPISODIC,
        summary=summary,
        occurred_at=occurred_at,
        sources=[
            SourceReference(
                source_type="observation",
                source_id=f"eval-source-{identifier}",
                world_id=world_id,
                owner_id=owner_id,
            )
        ],
        importance_features=features,
        admission_score=admission_score(features),
        confidence=1.0,
        epistemic_status=EpistemicStatus.OBSERVED,
        policy_version="memory-admission-v1",
        version=1,
        schema_version="1.0",
    )


def _execute_case(case: EvaluationFixtureCase, *, embeddings_enabled: bool) -> EvaluationCaseResult:
    owner_id = case.owner_id
    query = case.query
    cutoff_day = case.cutoff_day
    cutoff = BASE_TIME + timedelta(days=cutoff_day)
    required = set(case.required)
    relevant = set(case.relevant)
    optional = set(case.optional)
    forbidden = set(case.forbidden)
    memories: list[MemoryItem] = [
        *[
            _memory(
                identifier,
                owner_id=owner_id,
                summary=f"{query} authoritative owner-visible episode {identifier}",
                occurred_at=cutoff - timedelta(days=2),
            )
            for identifier in sorted(required)
        ],
        *[
            _memory(
                identifier,
                owner_id=owner_id,
                summary=f"{query} related episode {identifier}",
                occurred_at=cutoff - timedelta(days=1),
            )
            for identifier in sorted(relevant | optional)
        ],
    ]
    # Each forbidden category is represented by a hard-filter adversary.
    for index, identifier in enumerate(sorted(forbidden)):
        owner = "char-cross-owner-decoy" if index % 3 == 0 else owner_id
        world = "world-cross-world-decoy" if index % 3 == 1 else WORLD_ID
        occurred_at = cutoff + timedelta(days=1) if index % 3 == 2 else cutoff
        memories.append(
            _memory(
                identifier,
                owner_id=owner,
                world_id=world,
                summary=f"{query} adversarial exact-match private future decoy",
                occurred_at=occurred_at,
            )
        )
    embeddings = (
        {memory.id: deterministic_embedding(memory.summary) for memory in memories}
        if embeddings_enabled
        else None
    )
    request = RetrievalRequest(
        world_id=WORLD_ID,
        owner_id=owner_id,
        decision_world_time=cutoff,
        query_text=query,
        final_k=case.maximum_k,
        character_budget=case.character_budget,
    )
    ranked = retrieve(memories, request, embeddings=embeddings)
    selected, _reasons, _used = pack_context(
        ranked, final_k=request.final_k, character_budget=request.character_budget
    )
    return EvaluationCaseResult(
        case_id=case.id,
        ranked_memory_ids=[memory.id for memory in selected],
        required_memory_ids=required,
        forbidden_memory_ids=forbidden,
    )


def run_fixed_evaluation() -> MemoryEvaluationReport:
    corpus = EvaluationFixture.model_validate_json(CORPUS_PATH.read_text(encoding="utf-8"))
    cases = corpus.cases
    hybrid_results = [_execute_case(case, embeddings_enabled=True) for case in cases]
    fallback_results = [_execute_case(case, embeddings_enabled=False) for case in cases]

    def mode(name: str, results: list[EvaluationCaseResult]) -> EvaluationModeRead:
        metrics = evaluate_rankings(results)
        failed = [
            result.case_id
            for result in results
            if not result.required_memory_ids.issubset(result.ranked_memory_ids)
            or bool(result.forbidden_memory_ids & set(result.ranked_memory_ids))
        ]
        return EvaluationModeRead(mode=name, metrics=metrics, failed_case_ids=failed)

    return MemoryEvaluationReport(
        corpus_version=f"{corpus.id}/{corpus.version}",
        case_count=len(cases),
        hybrid=mode("hybrid", hybrid_results),
        fallback=mode("lexical_structured_fallback", fallback_results),
    )
