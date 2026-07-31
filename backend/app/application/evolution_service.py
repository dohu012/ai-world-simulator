"""Exactly-once deterministic reflection and owner-safe evolution reads."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.gray_harbor import WORLD_ID
from app.domain.evolution import (
    EVOLUTION_POLICY_VERSION,
    Dimension,
    EvidenceRole,
    EvolutionEvidence,
    ProposedDelta,
    TargetType,
    canonical_hash,
    evidence_watermark,
    oracle_deltas,
    validate_delta,
)
from app.infrastructure.database import evolution_models as er
from app.infrastructure.database import memory_models as mr
from app.infrastructure.database import models as r

ORACLE_ID = "gray-harbor-oracle"


class BaselineRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    generation: int
    structured_state: dict[str, object]
    persona_summary: str
    content_hash: str


class IdentityRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    version: int
    offsets: dict[str, float]
    confidence: float
    persona_summary: str
    evidence_horizon: datetime
    content_hash: str


class RelationshipRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    target_type: str
    target_id: str
    version: int
    dimensions: dict[str, float]
    uncertainty: float
    interpretation: str
    evidence_horizon: datetime
    content_hash: str


class ChangeRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    job_id: str
    snapshot_kind: str
    snapshot_id: str
    dimension: str
    proposed_magnitude: float
    applied_magnitude: float
    accepted: bool
    reason: str
    rationale: str
    evidence_memory_ids: list[str]
    created_at: datetime


class EvolutionStateRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    baseline: BaselineRead
    identity: IdentityRead
    relationships: list[RelationshipRead]
    changes: list[ChangeRead]
    context_watermark: str


class ReflectionRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    job_id: str
    status: str
    accepted_dimensions: int
    rejected_dimensions: int
    idempotent_replay: bool


BASELINE_DEFAULTS: dict[str, dict[str, object]] = {
    "char-lin-zhixia": {
        "traits": {"compassion": 0.8, "caution": 0.35},
        "values": {"care": 100, "duty": 90},
        "protected_values": ["care"],
        "desires": ["treat preventable illness"],
        "fears": ["avoidable loss"],
        "taboos": ["denying urgent care for convenience"],
        "summary": "Lin is compassionate, duty-led, and willing to accept bounded personal risk.",
    },
    "char-zhou-qiming": {
        "traits": {"caution": 0.6, "confidence": 0.65},
        "values": {"duty": 100, "order": 85},
        "protected_values": ["duty"],
        "desires": ["keep evacuation orderly"],
        "fears": ["crowd panic"],
        "taboos": ["abandoning an assigned post"],
        "summary": "Zhou values duty and order, testing uncertain reports before acting.",
    },
    "char-chen-mo": {
        "traits": {"caution": 0.75, "confidence": 0.5},
        "values": {"survival": 100, "community": 65},
        "protected_values": ["survival"],
        "desires": ["preserve scarce supplies"],
        "fears": ["waste and dependency"],
        "taboos": ["reckless resource promises"],
        "summary": (
            "Chen is resource-conscious and deliberate while retaining community obligations."
        ),
    },
}


class EvolutionApplicationService:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    async def initialize(self, owner_id: str) -> None:
        defaults = BASELINE_DEFAULTS[owner_id]
        structured = {key: value for key, value in defaults.items() if key != "summary"}
        baseline_hash = canonical_hash(
            [owner_id, json.dumps(structured, sort_keys=True, separators=(",", ":"))]
        )
        baseline_id = f"identity-baseline-{owner_id}-g1"
        snapshot_id = f"identity-{owner_id}-v1"
        async with self.sessions.begin() as session:
            character = await session.get(r.CharacterRecord, owner_id)
            if character is None or character.world_id != WORLD_ID:
                raise ValueError("OWNER_NOT_FOUND")
            await session.execute(
                insert(er.identity_baselines)
                .values(
                    id=baseline_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    agent_id=owner_id,
                    generation=1,
                    schema_version="1.0",
                    structured_state=structured,
                    persona_summary=str(defaults["summary"]),
                    content_hash=baseline_hash,
                )
                .on_conflict_do_nothing(
                    index_elements=["world_id", "owner_id", "agent_id", "generation"]
                )
            )
            world = await session.get(r.WorldRecord, WORLD_ID)
            assert world is not None
            snapshot_hash = canonical_hash([baseline_hash, "1", "{}"])
            await session.execute(
                insert(er.identity_snapshots)
                .values(
                    id=snapshot_id,
                    baseline_id=baseline_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    agent_id=owner_id,
                    version=1,
                    offsets={},
                    confidence=0.5,
                    persona_summary=str(defaults["summary"]),
                    evidence_horizon=world.current_time,
                    policy_version=EVOLUTION_POLICY_VERSION,
                    lifecycle="active",
                    content_hash=snapshot_hash,
                )
                .on_conflict_do_nothing(index_elements=["baseline_id", "version"])
            )
            await self._ensure_relationship(
                session, owner_id, TargetType.ORACLE, ORACLE_ID, world.current_time
            )

    async def reflect(self, owner_id: str) -> ReflectionRead:
        await self.initialize(owner_id)
        async with self.sessions() as session:
            world = await session.get(r.WorldRecord, WORLD_ID)
            assert world is not None
            memories = list(
                (
                    await session.scalars(
                        select(mr.MemoryItemRecord)
                        .where(
                            mr.MemoryItemRecord.world_id == WORLD_ID,
                            mr.MemoryItemRecord.owner_id == owner_id,
                            mr.MemoryItemRecord.occurred_at <= world.current_time,
                            mr.MemoryItemRecord.tombstoned_at.is_(None),
                        )
                        .order_by(mr.MemoryItemRecord.occurred_at, mr.MemoryItemRecord.id)
                        .limit(64)
                    )
                ).all()
            )
        evidence = [self._evidence(item, owner_id) for item in memories]
        watermark = evidence_watermark(evidence)
        logical_key = canonical_hash([WORLD_ID, owner_id, watermark, EVOLUTION_POLICY_VERSION])
        job_id = f"reflection-{logical_key[:32]}"
        async with self.sessions.begin() as session:
            result = await session.execute(
                insert(er.reflection_jobs)
                .values(
                    id=job_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    agent_id=owner_id,
                    logical_key=logical_key,
                    evidence_watermark=watermark,
                    policy_version=EVOLUTION_POLICY_VERSION,
                    status="claimed",
                    attempts=1,
                    claim_owner="deterministic-fallback",
                    claim_token=1,
                )
                .on_conflict_do_nothing(index_elements=["logical_key"])
                .returning(er.reflection_jobs.c.id)
            )
            created = result.scalar_one_or_none() is not None
        if not created:
            return await self._reflection_read(job_id, True)

        proposals = self._proposals(memories)
        for target_type, target_id, proposal in proposals:
            await self._commit_proposal(
                job_id, owner_id, target_type, target_id, proposal, evidence, watermark
            )
        async with self.sessions.begin() as session:
            await session.execute(
                update(er.reflection_jobs)
                .where(er.reflection_jobs.c.id == job_id, er.reflection_jobs.c.claim_token == 1)
                .values(status="completed", lease_expires_at=None)
            )
        return await self._reflection_read(job_id, False)

    async def state(self, owner_id: str) -> EvolutionStateRead:
        await self.initialize(owner_id)
        async with self.sessions() as session:
            baseline = (
                (
                    await session.execute(
                        select(er.identity_baselines)
                        .where(er.identity_baselines.c.owner_id == owner_id)
                        .order_by(er.identity_baselines.c.generation.desc())
                        .limit(1)
                    )
                )
                .mappings()
                .one()
            )
            identity = (
                (
                    await session.execute(
                        select(er.identity_snapshots)
                        .where(
                            er.identity_snapshots.c.owner_id == owner_id,
                            er.identity_snapshots.c.lifecycle == "active",
                        )
                        .order_by(er.identity_snapshots.c.version.desc())
                        .limit(1)
                    )
                )
                .mappings()
                .one()
            )
            relationships = list(
                (
                    await session.execute(
                        select(er.relationship_snapshots)
                        .where(
                            er.relationship_snapshots.c.owner_id == owner_id,
                            er.relationship_snapshots.c.active.is_(True),
                        )
                        .order_by(
                            er.relationship_snapshots.c.target_type,
                            er.relationship_snapshots.c.target_id,
                        )
                    )
                ).mappings()
            )
            deltas = list(
                (
                    await session.execute(
                        select(er.evolution_deltas)
                        .where(er.evolution_deltas.c.owner_id == owner_id)
                        .order_by(er.evolution_deltas.c.created_at, er.evolution_deltas.c.id)
                        .limit(100)
                    )
                ).mappings()
            )
            links = list(
                (
                    await session.execute(
                        select(
                            er.evolution_evidence_links.c.delta_id,
                            er.evolution_evidence_links.c.memory_id,
                        )
                        .join(
                            er.evolution_deltas,
                            er.evolution_deltas.c.id == er.evolution_evidence_links.c.delta_id,
                        )
                        .where(er.evolution_deltas.c.owner_id == owner_id)
                    )
                ).all()
            )
        linked: dict[str, list[str]] = {}
        for delta_id, memory_id in links:
            linked.setdefault(str(delta_id), []).append(str(memory_id))
        relationship_reads = [self._relationship_read(item) for item in relationships]
        context = self.context_watermark_rows(identity, relationships)
        return EvolutionStateRead(
            baseline=BaselineRead(
                id=str(baseline["id"]),
                generation=int(baseline["generation"]),
                structured_state=dict(baseline["structured_state"]),
                persona_summary=str(baseline["persona_summary"]),
                content_hash=str(baseline["content_hash"]),
            ),
            identity=self._identity_read(identity),
            relationships=relationship_reads,
            changes=[
                ChangeRead(
                    id=str(item["id"]),
                    job_id=str(item["job_id"]),
                    snapshot_kind=str(item["snapshot_kind"]),
                    snapshot_id=str(item["snapshot_id"]),
                    dimension=str(item["dimension"]),
                    proposed_magnitude=float(item["proposed_magnitude"]),
                    applied_magnitude=float(item["applied_magnitude"]),
                    accepted=bool(item["accepted"]),
                    reason=str(item["reason"]),
                    rationale=str(item["rationale"]),
                    evidence_memory_ids=sorted(linked.get(str(item["id"]), [])),
                    created_at=item["created_at"],
                )
                for item in deltas
            ],
            context_watermark=context,
        )

    async def context(self, owner_id: str) -> tuple[dict[str, object], str]:
        state = await self.state(owner_id)
        payload = {
            "baseline_id": state.baseline.id,
            "baseline_generation": state.baseline.generation,
            "identity": state.identity.model_dump(mode="json"),
            "relationships": [item.model_dump(mode="json") for item in state.relationships],
        }
        return payload, state.context_watermark

    async def _commit_proposal(
        self,
        job_id: str,
        owner_id: str,
        target_type: TargetType | None,
        target_id: str | None,
        proposal: ProposedDelta,
        evidence: list[EvolutionEvidence],
        watermark: str,
    ) -> None:
        relationship = target_type is not None
        async with self.sessions.begin() as session:
            job = (
                (
                    await session.execute(
                        select(er.reflection_jobs)
                        .where(er.reflection_jobs.c.id == job_id)
                        .with_for_update()
                    )
                )
                .mappings()
                .one()
            )
            if int(job["claim_token"]) != 1 or str(job["status"]) != "claimed":
                return
            world = await session.get(r.WorldRecord, WORLD_ID)
            assert world is not None
            if relationship:
                assert target_type is not None and target_id is not None
                target_type_value = target_type.value
                await self._ensure_relationship(
                    session, owner_id, target_type, target_id, world.current_time
                )
                current = (
                    (
                        await session.execute(
                            select(er.relationship_snapshots)
                            .where(
                                er.relationship_snapshots.c.owner_id == owner_id,
                                er.relationship_snapshots.c.target_type == target_type_value,
                                er.relationship_snapshots.c.target_id == target_id,
                                er.relationship_snapshots.c.active.is_(True),
                            )
                            .with_for_update()
                        )
                    )
                    .mappings()
                    .one()
                )
                values = dict(current["dimensions"])
            else:
                current = (
                    (
                        await session.execute(
                            select(er.identity_snapshots)
                            .where(
                                er.identity_snapshots.c.owner_id == owner_id,
                                er.identity_snapshots.c.lifecycle == "active",
                            )
                            .with_for_update()
                        )
                    )
                    .mappings()
                    .one()
                )
                values = dict(current["offsets"])
            selected = [item for item in evidence if item.id in proposal.evidence_ids]
            decision = validate_delta(
                proposal,
                evidence=evidence,
                world_id=WORLD_ID,
                owner_id=owner_id,
                agent_id=owner_id,
                cutoff=world.current_time,
                expected_watermark=watermark,
                current_value=float(values.get(proposal.dimension.value, 0.0)),
                relationship=relationship,
            )
            snapshot_id = str(current["id"])
            if decision.accepted:
                values[proposal.dimension.value] = round(
                    float(values.get(proposal.dimension.value, 0.0)) + decision.applied_magnitude,
                    6,
                )
                version = int(current["version"]) + 1
                if relationship:
                    await session.execute(
                        update(er.relationship_snapshots)
                        .where(er.relationship_snapshots.c.id == current["id"])
                        .values(active=False)
                    )
                    snapshot_id = f"relationship-{owner_id}-{target_id}-v{version}"
                    digest = canonical_hash(
                        [
                            str(current["content_hash"]),
                            str(version),
                            json.dumps(values, sort_keys=True),
                        ]
                    )
                    await session.execute(
                        insert(er.relationship_snapshots).values(
                            id=snapshot_id,
                            world_id=WORLD_ID,
                            owner_id=owner_id,
                            subject_agent_id=owner_id,
                            target_type=target_type_value,
                            target_id=target_id,
                            version=version,
                            dimensions=values,
                            uncertainty=max(0.0, float(current["uncertainty"]) - 0.03),
                            interpretation=proposal.rationale,
                            evidence_horizon=world.current_time,
                            policy_version=EVOLUTION_POLICY_VERSION,
                            previous_snapshot_id=current["id"],
                            content_hash=digest,
                            active=True,
                        )
                    )
                else:
                    await session.execute(
                        update(er.identity_snapshots)
                        .where(er.identity_snapshots.c.id == current["id"])
                        .values(lifecycle="superseded")
                    )
                    snapshot_id = f"identity-{owner_id}-v{version}"
                    digest = canonical_hash(
                        [
                            str(current["content_hash"]),
                            str(version),
                            json.dumps(values, sort_keys=True),
                        ]
                    )
                    await session.execute(
                        insert(er.identity_snapshots).values(
                            id=snapshot_id,
                            baseline_id=current["baseline_id"],
                            world_id=WORLD_ID,
                            owner_id=owner_id,
                            agent_id=owner_id,
                            version=version,
                            offsets=values,
                            confidence=min(1.0, float(current["confidence"]) + 0.05),
                            persona_summary=proposal.rationale,
                            evidence_horizon=world.current_time,
                            policy_version=EVOLUTION_POLICY_VERSION,
                            previous_snapshot_id=current["id"],
                            lifecycle="active",
                            content_hash=digest,
                        )
                    )
            delta_key = f"{job_id}:{target_id}:{proposal.dimension.value}"
            delta_id = f"delta-{sha256(delta_key.encode()).hexdigest()[:32]}"
            await session.execute(
                insert(er.evolution_deltas)
                .values(
                    id=delta_id,
                    job_id=job_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    agent_id=owner_id,
                    snapshot_kind="relationship" if relationship else "identity",
                    snapshot_id=snapshot_id,
                    dimension=proposal.dimension.value,
                    proposed_magnitude=proposal.magnitude,
                    applied_magnitude=decision.applied_magnitude,
                    accepted=decision.accepted,
                    reason=decision.reason,
                    rationale=proposal.rationale,
                )
                .on_conflict_do_nothing(
                    index_elements=["job_id", "snapshot_kind", "snapshot_id", "dimension"]
                )
            )
            for item in selected:
                await session.execute(
                    insert(er.evolution_evidence_links)
                    .values(
                        id=f"evidence-link-{sha256(f'{delta_id}:{item.source_id}'.encode()).hexdigest()[:32]}",
                        delta_id=delta_id,
                        memory_id=item.source_id,
                        world_id=WORLD_ID,
                        owner_id=owner_id,
                        occurred_at=item.occurred_at,
                        visible_from=item.visible_from,
                        evidence_role=item.role.value,
                        independent_key=item.independent_key,
                    )
                    .on_conflict_do_nothing(index_elements=["delta_id", "memory_id"])
                )

    @staticmethod
    def _evidence(memory: mr.MemoryItemRecord, owner_id: str) -> EvolutionEvidence:
        contract = memory.metadata_payload.get("contract")
        involved = contract.get("involved_entity_ids", []) if isinstance(contract, dict) else []
        role = (
            EvidenceRole.ORACLE_EVENT
            if memory.memory_type == "oracle"
            else (EvidenceRole.DIRECT_INTERACTION if involved else EvidenceRole.REPEATED_PATTERN)
        )
        return EvolutionEvidence(
            id=f"evidence-{memory.id}",
            world_id=memory.world_id,
            owner_id=memory.owner_id,
            agent_id=owner_id,
            source_type="memory",
            source_id=memory.id,
            occurred_at=memory.occurred_at,
            visible_from=memory.occurred_at,
            role=role,
            independent_key=f"{memory.logical_key}:{','.join(map(str, involved))}",
            summary=memory.summary[:600],
            schema_version="1.0",
        )

    @staticmethod
    def _proposals(
        memories: list[mr.MemoryItemRecord],
    ) -> list[tuple[TargetType | None, str | None, ProposedDelta]]:
        result: list[tuple[TargetType | None, str | None, ProposedDelta]] = []
        special_agents = set(BASELINE_DEFAULTS)
        latest_by_target: dict[str, mr.MemoryItemRecord] = {}
        for memory in memories:
            contract = memory.metadata_payload.get("contract")
            involved = contract.get("involved_entity_ids", []) if isinstance(contract, dict) else []
            for target in involved:
                target_id = str(target)
                if target_id in special_agents and target_id != memory.owner_id:
                    latest_by_target[target_id] = memory
        for target_id, memory in sorted(latest_by_target.items()):
            result.append(
                (
                    TargetType.AGENT,
                    target_id,
                    ProposedDelta(
                        dimension=Dimension.FAMILIARITY,
                        magnitude=0.03,
                        confidence=0.6,
                        evidence_ids=[f"evidence-{memory.id}"],
                        rationale=(
                            "A direct known interaction supports a small directional "
                            "increase in familiarity."
                        ),
                    ),
                )
            )
        consequential = [
            item
            for item in memories
            if any(
                word in item.summary.casefold()
                for word in (
                    "plan",
                    "resource",
                    "ration",
                    "shipment",
                    "medicine",
                    "failed",
                    "abandon",
                )
            )
        ]
        if len({item.logical_key for item in consequential}) >= 2:
            chosen = consequential[-2:]
            result.append(
                (
                    None,
                    None,
                    ProposedDelta(
                        dimension=Dimension.CAUTION,
                        magnitude=0.04,
                        confidence=0.7,
                        evidence_ids=[f"evidence-{item.id}" for item in chosen],
                        rationale=(
                            "Repeated independent resource consequences support "
                            "a small increase in caution."
                        ),
                    ),
                )
            )
        for memory in [item for item in memories if item.memory_type == "oracle"][-1:]:
            text = memory.summary.casefold()
            deltas = oracle_deltas(
                replied="silence" not in text and "timeout" not in text,
                urgent="urgent" in text or "medicine" in text,
                advice_quality="poor" if "poor" in text or "conflict" in text else "unknown",
                outcome="good" if "success" in text or "accepted" in text else "unknown",
                choice="rejected" if "reject" in text else "partial",
                value_conflict="conflict" in text,
            )
            for dimension, magnitude in deltas.items():
                result.append(
                    (
                        TargetType.ORACLE,
                        ORACLE_ID,
                        ProposedDelta(
                            dimension=dimension,
                            magnitude=magnitude,
                            confidence=0.65,
                            evidence_ids=[f"evidence-{memory.id}"],
                            rationale=(
                                "Oracle assessment separates reply, advice "
                                "quality, choice, and outcome."
                            ),
                        ),
                    )
                )
        return result

    @staticmethod
    async def _ensure_relationship(
        session: AsyncSession,
        owner_id: str,
        target_type: TargetType,
        target_id: str,
        horizon: datetime,
    ) -> None:
        identifier = f"relationship-{owner_id}-{target_id}-v1"
        digest = canonical_hash([owner_id, target_type.value, target_id, "1", "{}"])
        await session.execute(
            insert(er.relationship_snapshots)
            .values(
                id=identifier,
                world_id=WORLD_ID,
                owner_id=owner_id,
                subject_agent_id=owner_id,
                target_type=target_type.value,
                target_id=target_id,
                version=1,
                dimensions={},
                uncertainty=1.0,
                interpretation="No durable conclusion yet.",
                evidence_horizon=horizon,
                policy_version=EVOLUTION_POLICY_VERSION,
                content_hash=digest,
                active=True,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "world_id",
                    "owner_id",
                    "subject_agent_id",
                    "target_type",
                    "target_id",
                    "version",
                ]
            )
        )

    async def _reflection_read(self, job_id: str, replay: bool) -> ReflectionRead:
        async with self.sessions() as session:
            job = (
                (
                    await session.execute(
                        select(er.reflection_jobs).where(er.reflection_jobs.c.id == job_id)
                    )
                )
                .mappings()
                .one()
            )
            rows = list(
                (
                    await session.execute(
                        select(er.evolution_deltas.c.accepted).where(
                            er.evolution_deltas.c.job_id == job_id
                        )
                    )
                ).scalars()
            )
        return ReflectionRead(
            job_id=job_id,
            status=str(job["status"]),
            accepted_dimensions=sum(bool(item) for item in rows),
            rejected_dimensions=sum(not bool(item) for item in rows),
            idempotent_replay=replay,
        )

    @staticmethod
    def _identity_read(row: RowMapping) -> IdentityRead:
        item = row
        return IdentityRead(
            id=str(item["id"]),
            version=int(item["version"]),
            offsets={str(k): float(v) for k, v in dict(item["offsets"]).items()},
            confidence=float(item["confidence"]),
            persona_summary=str(item["persona_summary"]),
            evidence_horizon=item["evidence_horizon"],
            content_hash=str(item["content_hash"]),
        )

    @staticmethod
    def _relationship_read(item: RowMapping) -> RelationshipRead:
        return RelationshipRead(
            id=str(item["id"]),
            target_type=str(item["target_type"]),
            target_id=str(item["target_id"]),
            version=int(item["version"]),
            dimensions={str(k): float(v) for k, v in dict(item["dimensions"]).items()},
            uncertainty=float(item["uncertainty"]),
            interpretation=str(item["interpretation"]),
            evidence_horizon=item["evidence_horizon"],
            content_hash=str(item["content_hash"]),
        )

    @staticmethod
    def context_watermark_rows(
        identity: RowMapping,
        relationships: Sequence[RowMapping],
    ) -> str:
        return canonical_hash(
            [
                EVOLUTION_POLICY_VERSION,
                f"identity:{identity['id']}:{identity['version']}:{identity['content_hash']}",
                *(
                    f"relationship:{item['target_type']}:{item['target_id']}:{item['version']}:{item['content_hash']}"
                    for item in relationships
                ),
            ]
        )
