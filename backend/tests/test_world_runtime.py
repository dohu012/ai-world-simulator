from datetime import UTC, datetime, timedelta

import pytest

from app.application.world_runtime import (
    AdvanceLimitExceeded,
    DeadlineWinner,
    MajorDecisionAssessment,
    OracleDeadline,
    OraclePolicyContext,
    RuntimeGenerationConflict,
    RuntimePaused,
    RuntimeStatus,
    ScheduledItem,
    WorldClock,
    bounded_due,
    deadline_winner,
    evaluate_oracle,
    order_scheduled,
    should_wake,
)

NOW = datetime(2026, 7, 27, tzinfo=UTC)


def item(identity: str, priority: int = 100) -> ScheduledItem:
    return ScheduledItem(id=identity, due_world_time=NOW, priority=priority, created_at=NOW)


def test_equal_time_has_stable_total_order_and_bound() -> None:
    assert [x.id for x in order_scheduled([item("b"), item("a"), item("c", 1)])] == ["c", "a", "b"]
    with pytest.raises(AdvanceLimitExceeded):
        bounded_due([item("a"), item("b")], NOW, 1)


def test_world_clock_is_monotonic_paused_and_fenced() -> None:
    clock = WorldClock(
        world_id="w", current_world_time=NOW, status=RuntimeStatus.RUNNING, generation=3
    )
    assert clock.advance(
        timedelta(minutes=5), expected_generation=3
    ).current_world_time == NOW + timedelta(minutes=5)
    with pytest.raises(RuntimeGenerationConflict):
        clock.advance(timedelta(), expected_generation=2)
    with pytest.raises(RuntimePaused):
        clock.model_copy(update={"status": RuntimeStatus.PAUSED}).advance(
            timedelta(), expected_generation=3
        )


def test_reply_timeout_precedence_is_deterministic() -> None:
    deadline = OracleDeadline(
        world_deadline=NOW + timedelta(minutes=10), real_deadline=NOW + timedelta(hours=1)
    )
    assert (
        deadline_winner(
            world_now=NOW, real_now=NOW, deadline=deadline, reply_at=NOW + timedelta(minutes=9)
        )
        is DeadlineWinner.REPLY
    )
    assert (
        deadline_winner(world_now=NOW + timedelta(minutes=10), real_now=NOW, deadline=deadline)
        is DeadlineWinner.WORLD_TIMEOUT
    )
    assert deadline_winner(world_now=NOW, real_now=NOW, deadline=deadline) is DeadlineWinner.WAITING


def test_oracle_is_server_policy_and_wake_is_owner_scoped() -> None:
    assessment = MajorDecisionAssessment(
        major_decision=True,
        seek_oracle=True,
        risk="high",
        reversible=False,
        rationale_summary="Irreversible family risk.",
    )
    context = OraclePolicyContext(
        oracle_enabled=True,
        contact_available=True,
        cooldown_clear=True,
        budget_available=True,
        existing_open_window=False,
    )
    assert evaluate_oracle(assessment, context).eligible
    assert not evaluate_oracle(
        assessment, context.model_copy(update={"existing_open_window": True})
    ).eligible
    assert should_wake("chen", "chen", "oracle_reply")
    assert not should_wake("chen", "lin", "oracle_reply")
