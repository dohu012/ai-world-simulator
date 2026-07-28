from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.domain.communication import (
    BeliefProjection,
    BeliefStatus,
    ClaimStance,
    ConversationBudget,
    MessageClaim,
    Transmission,
    revise_belief,
    stable_route_order,
)


def claim(value: str, source: str, stance: ClaimStance = ClaimStance.HEARD) -> MessageClaim:
    return MessageClaim(
        proposition_key="gray_harbor.north_gate.closure_time",
        stance=stance,
        value=value,
        attribution="fixture",
        causal_source_key=source,
    )


def test_equal_time_transmissions_have_stable_total_order() -> None:
    now = datetime(2026, 7, 27, tzinfo=UTC)

    def transmission(identifier: str, priority: int) -> Transmission:
        return Transmission(
            id=identifier,
            delivery_key=identifier,
            world_id="world",
            message_id=f"message-{identifier}",
            channel_id="channel",
            sender_id=None,
            recipient_id="agent",
            sent_world_time=now,
            arrival_world_time=now + timedelta(minutes=5),
            priority=priority,
        )

    ordered = stable_route_order(
        [transmission("b", 20), transmission("c", 10), transmission("a", 20)]
    )
    assert [item.id for item in ordered] == ["c", "a", "b"]


def test_conflicting_evidence_preserves_history_projection() -> None:
    first = revise_belief(None, claim("all gates 11:30", "courier"), reliability=0.52)
    conflicted = revise_belief(first, claim("north gate 12:00", "bulletin"), reliability=0.94)
    assert conflicted.status is BeliefStatus.CONFLICTED
    assert conflicted.value == "all gates 11:30"
    assert conflicted.reason_code == "CONFLICTING_EVIDENCE"
    assert conflicted.causal_source_keys == ["courier", "bulletin"]


def test_higher_reliability_correction_revises_projection() -> None:
    rumor = revise_belief(None, claim("all gates 11:30", "courier"), reliability=0.52)
    corrected = revise_belief(
        rumor,
        claim("north gate 12:00", "official", ClaimStance.CORRECTED),
        reliability=0.94,
    )
    assert corrected.value == "north gate 12:00"
    assert corrected.status is BeliefStatus.ACTIVE
    assert corrected.reason_code == "HIGHER_RELIABILITY_CORRECTION"


def test_same_causal_source_is_not_independent_corroboration() -> None:
    prior = BeliefProjection(
        proposition_key="gray_harbor.north_gate.closure_time",
        value="north gate 12:00",
        confidence=0.8,
        status=BeliefStatus.ACTIVE,
        reason_code="INITIAL_EVIDENCE",
        causal_source_keys=["shared-order"],
    )
    duplicate = revise_belief(prior, claim("north gate 12:00", "shared-order"), reliability=0.99)
    assert duplicate.confidence == 0.8
    assert duplicate.reason_code == "BELIEF_EVIDENCE_DUPLICATE"


def test_conversation_budget_is_strictly_bounded() -> None:
    assert ConversationBudget(max_turns=3, used_turns=3).used_turns == 3
    with pytest.raises(ValidationError):
        ConversationBudget(max_turns=3, used_turns=4)
