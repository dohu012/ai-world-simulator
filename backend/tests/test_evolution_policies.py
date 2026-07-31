from datetime import UTC, datetime, timedelta

from app.domain.evolution import (
    Dimension,
    EvidenceRole,
    EvolutionEvidence,
    ProposedDelta,
    evidence_watermark,
    oracle_deltas,
    validate_delta,
)

NOW = datetime(2026, 7, 28, tzinfo=UTC)


def evidence(identifier: str, *, owner: str = "chen", independent: str | None = None):
    return EvolutionEvidence(
        id=identifier,
        world_id="gray-harbor",
        owner_id=owner,
        agent_id=owner,
        source_type="memory",
        source_id=f"memory-{identifier}",
        occurred_at=NOW,
        visible_from=NOW,
        role=EvidenceRole.REPEATED_PATTERN,
        independent_key=independent or identifier,
        summary="Bounded fictional evidence.",
        schema_version="1.0",
    )


def test_identity_requires_independent_evidence_and_caps_change():
    items = [evidence("a"), evidence("b")]
    proposal = ProposedDelta(
        dimension=Dimension.CAUTION,
        magnitude=0.08,
        confidence=0.8,
        evidence_ids=["a", "b"],
        rationale="Two independent resource failures support a small change.",
    )
    accepted = validate_delta(
        proposal,
        evidence=items,
        world_id="gray-harbor",
        owner_id="chen",
        agent_id="chen",
        cutoff=NOW,
        expected_watermark=evidence_watermark(items),
        relationship=False,
    )
    assert accepted.accepted
    assert (
        validate_delta(
            proposal.model_copy(update={"magnitude": 0.081}),
            evidence=items,
            world_id="gray-harbor",
            owner_id="chen",
            agent_id="chen",
            cutoff=NOW,
            expected_watermark=evidence_watermark(items),
            relationship=False,
        ).reason
        == "EVENT_CAP"
    )


def test_owner_future_duplicate_and_stale_evidence_are_rejected():
    items = [evidence("a"), evidence("b", owner="lin")]
    proposal = ProposedDelta(
        dimension=Dimension.TRUST,
        magnitude=0.1,
        confidence=0.7,
        evidence_ids=["a", "b"],
        rationale="Untrusted proposal cannot cross owners.",
    )
    assert (
        validate_delta(
            proposal,
            evidence=items,
            world_id="gray-harbor",
            owner_id="chen",
            agent_id="chen",
            cutoff=NOW,
            expected_watermark=evidence_watermark(items),
            relationship=True,
        ).reason
        == "OWNER_MISMATCH"
    )
    future = evidence("future").model_copy(
        update={
            "occurred_at": NOW + timedelta(days=1),
            "visible_from": NOW + timedelta(days=1),
        }
    )
    assert (
        validate_delta(
            proposal.model_copy(update={"evidence_ids": ["future"]}),
            evidence=[future],
            world_id="gray-harbor",
            owner_id="chen",
            agent_id="chen",
            cutoff=NOW,
            expected_watermark=evidence_watermark([future]),
            relationship=True,
        ).reason
        == "FUTURE_EVIDENCE"
    )
    assert (
        validate_delta(
            proposal.model_copy(update={"evidence_ids": ["a"]}),
            evidence=[items[0]],
            world_id="gray-harbor",
            owner_id="chen",
            agent_id="chen",
            cutoff=NOW,
            expected_watermark="0" * 64,
            relationship=True,
        ).reason
        == "STALE_WATERMARK"
    )


def test_oracle_semantics_are_non_mechanical():
    assert (
        oracle_deltas(
            replied=False,
            urgent=False,
            advice_quality="unknown",
            outcome="unknown",
            choice="rejected",
            value_conflict=False,
        )
        == {}
    )
    lucky = oracle_deltas(
        replied=True,
        urgent=True,
        advice_quality="poor",
        outcome="good",
        choice="followed",
        value_conflict=False,
    )
    assert lucky[Dimension.TRUST] < 0
    assert lucky[Dimension.GRATITUDE] > 0
    conflict = oracle_deltas(
        replied=True,
        urgent=True,
        advice_quality="sound",
        outcome="good",
        choice="rejected",
        value_conflict=True,
    )
    assert conflict[Dimension.RESPECT] > 0
    assert conflict[Dimension.RESENTMENT] > 0
