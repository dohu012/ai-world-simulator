from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.application.memory_evaluation import run_fixed_evaluation
from app.application.memory_service import classify_embedding_failure
from app.domain.memory import (
    EmbeddingRecord,
    EpisodicMemory,
    EpistemicStatus,
    EvaluationCaseResult,
    ImportanceFeatures,
    MemoryType,
    RetrievalRequest,
    SourceReference,
    admission_score,
    context_watermark,
    deterministic_embedding,
    evaluate_rankings,
    pack_context,
    retrieve,
    should_admit,
)

NOW = datetime(2026, 7, 30, tzinfo=UTC)


def memory(
    identifier: str, *, owner: str = "chen", days_old: int = 1, summary: str = "food clinic"
) -> EpisodicMemory:
    features = ImportanceFeatures(resource_impact=0.8, novelty=0.8)
    return EpisodicMemory(
        id=identifier,
        world_id="gray",
        owner_id=owner,
        memory_type=MemoryType.EPISODIC,
        summary=summary,
        occurred_at=NOW - timedelta(days=days_old),
        sources=[
            SourceReference(
                source_type="observation",
                source_id=f"obs-{identifier}",
                world_id="gray",
                owner_id=owner,
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


def test_provenance_rejects_cross_owner_and_reversed_time() -> None:
    data = memory("m1").model_dump()
    data["sources"][0]["owner_id"] = "lin"
    with pytest.raises(ValidationError, match="cross-owner"):
        EpisodicMemory.model_validate(data)
    data = memory("m1").model_dump()
    data["ended_at"] = NOW - timedelta(days=2)
    with pytest.raises(ValidationError, match="reversed"):
        EpisodicMemory.model_validate(data)


def test_admission_rejects_routine_duplicates() -> None:
    accepted = ImportanceFeatures(irreversible=1.0, personal_risk=1.0, novelty=1.0)
    assert should_admit(accepted)[0]
    routine = ImportanceFeatures(repetition=1.0)
    assert should_admit(routine) == (False, "ROUTINE_DUPLICATE")


def test_embedding_is_deterministic_finite_and_dimension_checked() -> None:
    assert deterministic_embedding("药品 medicine") == deterministic_embedding("药品 medicine")
    with pytest.raises(ValidationError, match="dimensions"):
        EmbeddingRecord(
            memory_id="m1",
            provider="fake",
            model="hash",
            revision="v1",
            dimensions=2,
            distance_metric="cosine",
            normalized=True,
            content_hash="a" * 64,
            vector=[0.1],
            created_at=NOW,
            schema_version="1.0",
        )


def test_hard_filters_run_before_ranking_and_fallback_is_stable() -> None:
    allowed = memory("allowed", summary="medicine shortage clinic")
    other_owner = memory("private-decoy", owner="lin", summary="medicine shortage secret")
    future = memory("future-decoy", days_old=-1, summary="medicine rescue")
    request = RetrievalRequest(
        world_id="gray",
        owner_id="chen",
        decision_world_time=NOW,
        query_text="medicine clinic",
        final_k=2,
        character_budget=1000,
    )
    first = retrieve([future, other_owner, allowed], request)
    second = retrieve(list(reversed([future, other_owner, allowed])), request)
    assert [item[0].id for item in first] == [item[0].id for item in second] == ["allowed"]
    assert first[0][1].semantic == 0.0


def test_context_packing_never_partially_truncates_and_watermark_changes() -> None:
    ranked = retrieve(
        [memory("one", summary="12345"), memory("two", days_old=2, summary="67890")],
        RetrievalRequest(world_id="gray", owner_id="chen", decision_world_time=NOW, query_text=""),
    )
    selected, reasons, used = pack_context(ranked, final_k=2, character_budget=6)
    assert len(selected) == 1
    assert used == 5
    assert set(reasons.values()) == {"SELECTED", "TOKEN_BUDGET"}
    before = context_watermark(["obs:a"], selected, cutoff=NOW, retrieval_mode="lexical")
    after = context_watermark(["obs:a"], [memory("changed")], cutoff=NOW, retrieval_mode="lexical")
    assert before != after


def test_offline_evaluation_reports_metrics_and_zero_leakage() -> None:
    metrics = evaluate_rankings(
        [
            EvaluationCaseResult(
                case_id="chen",
                ranked_memory_ids=["required-a", "relevant-b"],
                required_memory_ids={"required-a"},
                forbidden_memory_ids={"lin-private", "future-day7"},
            ),
            EvaluationCaseResult(
                case_id="lin",
                ranked_memory_ids=["required-c"],
                required_memory_ids={"required-c"},
                forbidden_memory_ids={"chen-oracle"},
            ),
        ]
    )
    assert metrics.required_recall_at_k == 1.0
    assert metrics.precision_at_k == pytest.approx(2 / 3, abs=1e-6)
    assert metrics.mean_reciprocal_rank == 1.0
    assert metrics.forbidden_exposure_count == 0
    assert metrics.hard_gates_passed is True


@pytest.mark.parametrize(
    ("code", "classification"),
    [
        ("EMBEDDING_TIMEOUT", "transient"),
        ("EMBEDDING_RATE_LIMITED", "transient"),
        ("EMBEDDING_PROVIDER_UNAVAILABLE", "transient"),
        ("EMBEDDING_INPUT_TOO_LARGE", "permanent"),
        ("EMBEDDING_OUTPUT_INVALID", "permanent"),
    ],
)
def test_embedding_failures_have_stable_classification(code: str, classification: str) -> None:
    assert classify_embedding_failure(code) == classification


def test_versioned_corpus_runs_hybrid_and_outage_fallback_with_zero_forbidden() -> None:
    report = run_fixed_evaluation()
    assert report.corpus_version == "gray-harbor-memory-eval/1.0.0"
    assert report.case_count == 3
    for mode in (report.hybrid, report.fallback):
        assert mode.metrics.required_recall_at_k == 1.0
        assert mode.metrics.forbidden_exposure_count == 0
        assert mode.metrics.hard_gates_passed is True
        assert mode.failed_case_ids == []
