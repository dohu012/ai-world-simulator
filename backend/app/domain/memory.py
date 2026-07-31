"""Auditable owner-scoped long-term memory contracts and deterministic policies."""

from __future__ import annotations

import math
import re
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal, Protocol

from pydantic import Field, StringConstraints, model_validator

from app.domain.common import DomainModel, NonEmptyString, SchemaVersion, Timestamp, UnitFloat

MemoryText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]

ADMISSION_POLICY_VERSION = "memory-admission-v1"
RETRIEVAL_POLICY_VERSION = "memory-retrieval-v1"
PROMPT_PACKING_VERSION = "memory-context-v1"
EMBEDDING_REVISION = "deterministic-hash-v1"


class MemoryType(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    EMOTIONAL = "emotional"
    ORACLE = "oracle"
    STAGE_SUMMARY = "stage_summary"


class EpistemicStatus(StrEnum):
    OBSERVED = "observed"
    SUBJECTIVE = "subjective"
    INFERRED = "inferred"


class SourceReference(DomainModel):
    source_type: Literal[
        "observation",
        "event",
        "action",
        "action_result",
        "message",
        "oracle",
        "belief",
        "plan",
        "memory",
    ]
    source_id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString


class ImportanceFeatures(DomainModel):
    goal_change: UnitFloat = 0.0
    personal_risk: UnitFloat = 0.0
    resource_impact: UnitFloat = 0.0
    irreversible: UnitFloat = 0.0
    contradiction: UnitFloat = 0.0
    oracle_relevance: UnitFloat = 0.0
    novelty: UnitFloat = 0.0
    repetition: UnitFloat = 0.0


class MemoryItem(DomainModel):
    id: NonEmptyString
    world_id: NonEmptyString
    owner_id: NonEmptyString
    memory_type: MemoryType
    summary: MemoryText
    occurred_at: Timestamp
    ended_at: Timestamp | None = None
    sources: list[SourceReference] = Field(min_length=1, max_length=32)
    involved_entity_ids: list[NonEmptyString] = Field(default_factory=list, max_length=32)
    location_ids: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    goal_ids: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    plan_ids: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    emotion_labels: list[NonEmptyString] = Field(default_factory=list, max_length=8)
    emotion_intensity: UnitFloat = 0.0
    importance_features: ImportanceFeatures
    admission_score: UnitFloat
    confidence: UnitFloat
    epistemic_status: EpistemicStatus
    policy_version: NonEmptyString
    model_revision: str | None = None
    version: int = Field(ge=1)
    supersedes_id: str | None = None
    tombstoned_at: Timestamp | None = None
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def validate_provenance(self) -> MemoryItem:
        if self.ended_at is not None and self.ended_at < self.occurred_at:
            raise ValueError("memory interval is reversed")
        keys = {(source.source_type, source.source_id) for source in self.sources}
        if len(keys) != len(self.sources):
            raise ValueError("duplicate memory source")
        if any(
            source.world_id != self.world_id or source.owner_id != self.owner_id
            for source in self.sources
        ):
            raise ValueError("cross-owner or cross-world provenance")
        for values in (
            self.involved_entity_ids,
            self.location_ids,
            self.goal_ids,
            self.plan_ids,
            self.emotion_labels,
        ):
            if len(set(values)) != len(values):
                raise ValueError("duplicate memory metadata")
        return self


class EpisodicMemory(MemoryItem):
    memory_type: Literal[MemoryType.EPISODIC]


class SemanticMemory(MemoryItem):
    memory_type: Literal[MemoryType.SEMANTIC]
    subject: NonEmptyString
    predicate: NonEmptyString
    object: NonEmptyString
    valid_from: Timestamp
    valid_until: Timestamp | None = None
    supporting_memory_ids: list[NonEmptyString] = Field(default_factory=list, max_length=32)
    contradicting_memory_ids: list[NonEmptyString] = Field(default_factory=list, max_length=32)
    last_reinforced_at: Timestamp

    @model_validator(mode="after")
    def validate_semantic_interval(self) -> SemanticMemory:
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("semantic validity interval is reversed")
        return self


class EmotionalMemory(MemoryItem):
    memory_type: Literal[MemoryType.EMOTIONAL]
    association: MemoryText


class OracleMemory(MemoryItem):
    memory_type: Literal[MemoryType.ORACLE]
    advice_observation_id: str | None
    silence_reason: str | None
    interpretation: MemoryText
    chosen_action_id: str | None
    outcome_event_id: str | None
    outcome_summary: MemoryText | None

    @model_validator(mode="after")
    def advice_or_silence(self) -> OracleMemory:
        if (self.advice_observation_id is None) == (self.silence_reason is None):
            raise ValueError("oracle memory requires exactly one of advice or silence")
        return self


class StageSummaryMemory(MemoryItem):
    memory_type: Literal[MemoryType.STAGE_SUMMARY]
    stage_id: NonEmptyString
    contributing_memory_ids: list[NonEmptyString] = Field(min_length=1, max_length=64)
    unresolved_contradiction_ids: list[NonEmptyString] = Field(default_factory=list, max_length=32)
    token_estimate: int = Field(ge=1, le=600)


class EmbeddingRecord(DomainModel):
    memory_id: NonEmptyString
    provider: NonEmptyString
    model: NonEmptyString
    revision: NonEmptyString
    dimensions: int = Field(ge=1, le=4096)
    distance_metric: Literal["cosine"]
    normalized: bool
    content_hash: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    vector: list[float] = Field(min_length=1, max_length=4096)
    created_at: Timestamp
    schema_version: SchemaVersion

    @model_validator(mode="after")
    def validate_vector(self) -> EmbeddingRecord:
        if len(self.vector) != self.dimensions or not all(math.isfinite(x) for x in self.vector):
            raise ValueError("invalid embedding dimensions or non-finite value")
        return self


class RetrievalRequest(DomainModel):
    world_id: NonEmptyString
    owner_id: NonEmptyString
    decision_world_time: Timestamp
    query_text: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)]
    goal_ids: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    entity_ids: list[NonEmptyString] = Field(default_factory=list, max_length=32)
    location_ids: list[NonEmptyString] = Field(default_factory=list, max_length=16)
    allowed_types: set[MemoryType] = Field(default_factory=lambda: set(MemoryType))
    final_k: int = Field(default=6, ge=1, le=12)
    character_budget: int = Field(default=4000, ge=256, le=12000)


class ScoreComponents(DomainModel):
    lexical: UnitFloat
    semantic: UnitFloat
    recency: UnitFloat
    importance: UnitFloat
    goal: UnitFloat
    entity: UnitFloat
    location: UnitFloat
    emotion: UnitFloat
    contradiction: UnitFloat
    oracle: UnitFloat
    diversity_penalty: UnitFloat
    total: UnitFloat


class RetrievalCandidate(DomainModel):
    memory_id: NonEmptyString
    occurred_at: Timestamp
    memory_type: MemoryType
    scores: ScoreComponents
    selected: bool
    exclusion_reason: Literal[
        "SELECTED",
        "LOW_SCORE",
        "TOKEN_BUDGET",
        "DIVERSITY_LIMIT",
    ]
    rank: int = Field(ge=1)


class MemoryWriterPort(Protocol):
    async def admit(self, memory: MemoryItem) -> MemoryItem: ...


class MemoryRetrieverPort(Protocol):
    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalCandidate]: ...


class EvaluationCaseResult(DomainModel):
    case_id: NonEmptyString
    ranked_memory_ids: list[NonEmptyString]
    required_memory_ids: set[NonEmptyString]
    forbidden_memory_ids: set[NonEmptyString]


class EvaluationMetrics(DomainModel):
    case_count: int = Field(ge=0)
    required_recall_at_k: UnitFloat
    precision_at_k: UnitFloat
    mean_reciprocal_rank: UnitFloat
    forbidden_exposure_count: int = Field(ge=0)
    forbidden_exposure_rate: UnitFloat
    hard_gates_passed: bool


def evaluate_rankings(results: list[EvaluationCaseResult]) -> EvaluationMetrics:
    required_total = sum(len(result.required_memory_ids) for result in results)
    retrieved_required = sum(
        len(set(result.ranked_memory_ids) & result.required_memory_ids) for result in results
    )
    retrieved_total = sum(len(result.ranked_memory_ids) for result in results)
    forbidden = sum(
        len(set(result.ranked_memory_ids) & result.forbidden_memory_ids) for result in results
    )
    reciprocal_ranks: list[float] = []
    for result in results:
        ranks = [
            index
            for index, identifier in enumerate(result.ranked_memory_ids, 1)
            if identifier in result.required_memory_ids
        ]
        reciprocal_ranks.append(1 / min(ranks) if ranks else 0.0)
    recall = retrieved_required / required_total if required_total else 1.0
    precision = retrieved_required / retrieved_total if retrieved_total else 1.0
    exposure_rate = forbidden / retrieved_total if retrieved_total else 0.0
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 1.0
    return EvaluationMetrics(
        case_count=len(results),
        required_recall_at_k=round(recall, 6),
        precision_at_k=round(precision, 6),
        mean_reciprocal_rank=round(mrr, 6),
        forbidden_exposure_count=forbidden,
        forbidden_exposure_rate=round(exposure_rate, 6),
        hard_gates_passed=recall == 1.0 and forbidden == 0,
    )


def admission_score(features: ImportanceFeatures) -> float:
    score = (
        features.goal_change * 0.18
        + features.personal_risk * 0.16
        + features.resource_impact * 0.13
        + features.irreversible * 0.18
        + features.contradiction * 0.10
        + features.oracle_relevance * 0.12
        + features.novelty * 0.13
        - features.repetition * 0.20
    )
    return round(max(0.0, min(1.0, score)), 6)


def should_admit(features: ImportanceFeatures, *, threshold: float = 0.32) -> tuple[bool, str]:
    score = admission_score(features)
    if features.repetition >= 0.9 and features.novelty <= 0.1:
        return False, "ROUTINE_DUPLICATE"
    return (True, "ADMITTED_IMPORTANT") if score >= threshold else (False, "BELOW_THRESHOLD")


def deterministic_embedding(text: str, *, dimensions: int = 16) -> list[float]:
    """Offline fake embedding; deterministic and deliberately not semantic production authority."""
    values: list[float] = []
    counter = 0
    while len(values) < dimensions:
        digest = sha256(f"{EMBEDDING_REVISION}:{counter}:{text}".encode()).digest()
        values.extend((byte / 127.5) - 1.0 for byte in digest)
        counter += 1
    vector = values[:dimensions]
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 9) for value in vector]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.casefold()))


def _cosine(left: list[float], right: list[float]) -> float:
    return max(0.0, min(1.0, (sum(a * b for a, b in zip(left, right, strict=True)) + 1) / 2))


def retrieve(
    memories: list[MemoryItem],
    request: RetrievalRequest,
    *,
    embeddings: dict[str, list[float]] | None = None,
) -> list[tuple[MemoryItem, ScoreComponents]]:
    """Hard-filter first, then deterministic transparent weighted fusion."""
    query_tokens = _tokens(request.query_text)
    query_vector = deterministic_embedding(request.query_text)
    scored: list[tuple[MemoryItem, ScoreComponents]] = []
    for memory in memories:
        if (
            memory.world_id != request.world_id
            or memory.owner_id != request.owner_id
            or memory.occurred_at > request.decision_world_time
            or memory.tombstoned_at is not None
            or memory.memory_type not in request.allowed_types
        ):
            continue
        memory_tokens = _tokens(memory.summary)
        lexical = len(query_tokens & memory_tokens) / max(1, len(query_tokens))
        semantic = (
            _cosine(query_vector, embeddings[memory.id])
            if embeddings is not None and memory.id in embeddings
            else 0.0
        )
        age_days = max(
            0.0, (request.decision_world_time - memory.occurred_at).total_seconds() / 86400
        )
        recency = 1 / (1 + age_days / 7)
        goal = len(set(request.goal_ids) & set(memory.goal_ids)) / max(1, len(request.goal_ids))
        entity = len(set(request.entity_ids) & set(memory.involved_entity_ids)) / max(
            1, len(request.entity_ids)
        )
        location = len(set(request.location_ids) & set(memory.location_ids)) / max(
            1, len(request.location_ids)
        )
        contradiction = float(
            isinstance(memory, SemanticMemory) and bool(memory.contradicting_memory_ids)
        )
        oracle = float(memory.memory_type is MemoryType.ORACLE)
        total = (
            lexical * 0.20
            + semantic * 0.20
            + recency * 0.10
            + memory.admission_score * 0.18
            + goal * 0.10
            + entity * 0.07
            + location * 0.04
            + memory.emotion_intensity * 0.04
            + contradiction * 0.03
            + oracle * 0.04
        )
        components = ScoreComponents(
            lexical=round(lexical, 6),
            semantic=round(semantic, 6),
            recency=round(recency, 6),
            importance=memory.admission_score,
            goal=round(goal, 6),
            entity=round(entity, 6),
            location=round(location, 6),
            emotion=memory.emotion_intensity,
            contradiction=contradiction,
            oracle=oracle,
            diversity_penalty=0.0,
            total=round(max(0.0, min(1.0, total)), 6),
        )
        scored.append((memory, components))
    return sorted(
        scored, key=lambda item: (-item[1].total, -item[0].occurred_at.timestamp(), item[0].id)
    )


def pack_context(
    ranked: list[tuple[MemoryItem, ScoreComponents]], *, final_k: int, character_budget: int
) -> tuple[list[MemoryItem], dict[str, str], int]:
    selected: list[MemoryItem] = []
    reasons: dict[str, str] = {}
    used = 0
    source_counts: dict[tuple[str, str], int] = {}
    for memory, _score in ranked:
        if len(selected) >= final_k:
            reasons[memory.id] = "LOW_SCORE"
            continue
        source_key = (memory.sources[0].source_type, memory.sources[0].source_id)
        if source_counts.get(source_key, 0) >= 1:
            reasons[memory.id] = "DIVERSITY_LIMIT"
            continue
        record_size = len(memory.summary)
        if used + record_size > character_budget:
            reasons[memory.id] = "TOKEN_BUDGET"
            continue
        selected.append(memory)
        source_counts[source_key] = source_counts.get(source_key, 0) + 1
        reasons[memory.id] = "SELECTED"
        used += record_size
    return selected, reasons, used


def context_watermark(
    observation_hashes: list[str],
    memories: list[MemoryItem],
    *,
    cutoff: datetime,
    retrieval_mode: str,
) -> str:
    payload = "\x1f".join(
        [
            PROMPT_PACKING_VERSION,
            RETRIEVAL_POLICY_VERSION,
            retrieval_mode,
            cutoff.isoformat(),
            *sorted(observation_hashes),
            *(f"{memory.id}:{memory.version}" for memory in memories),
        ]
    )
    return sha256(payload.encode()).hexdigest()
