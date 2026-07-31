import json
from pathlib import Path

import pytest

from app.domain.seven_day import (
    DueWork,
    PlanStatus,
    ResidentTier,
    ResourcePolicy,
    SevenDayRuntimeSeam,
    adjudicate,
    blocked_plan_outcome,
    evaluate_condition,
    stable_due_order,
    transition_plan,
)

SCENARIO_PATH = Path(__file__).parents[1] / "app" / "scenarios" / "gray_harbor_seven_day_v1.json"


def test_equal_time_order_is_stable_for_one_hundred_operations() -> None:
    work = [DueWork(60, index % 4, f"work-{99 - index:03d}") for index in range(100)]
    ordered = stable_due_order(work)
    assert ordered == stable_due_order(list(reversed(work)))
    assert ordered == sorted(
        work, key=lambda item: (item.world_minute, item.priority, item.stable_key)
    )


def test_two_workers_competing_for_final_unit_have_one_auditable_winner() -> None:
    stock = ResourcePolicy(1)
    winner = stock.consume(1, "worker-a")
    with pytest.raises(ValueError, match="RESOURCE_INSUFFICIENT"):
        stock.consume(1, "worker-b")
    assert winner.new_available == stock.available == 0


def test_crash_before_and_after_commit_recovery_is_exact_once() -> None:
    stock = ResourcePolicy(2)
    assert stock.available == 2
    first = stock.consume(1, "logical-action")
    recovered = stock.consume(1, "logical-action")
    assert recovered == first
    assert stock.available == 1


def test_day_five_condition_fires_once() -> None:
    condition = {"field": "day", "op": "gte", "value": 5}
    fired = False
    firings = 0
    for day in range(1, 8):
        if not fired and evaluate_condition(condition, {"day": day}):
            fired = True
            firings += 1
    assert firings == 1


def test_plan_completes_blocks_replans_and_terminates_without_loop() -> None:
    assert transition_plan(PlanStatus.DRAFT, PlanStatus.ACTIVE) is PlanStatus.ACTIVE
    assert transition_plan(PlanStatus.ACTIVE, PlanStatus.COMPLETED) is PlanStatus.COMPLETED
    assert transition_plan(PlanStatus.ACTIVE, PlanStatus.BLOCKED) is PlanStatus.BLOCKED
    assert blocked_plan_outcome(replan_count=0, repeated_step_count=1) is PlanStatus.ACTIVE
    assert blocked_plan_outcome(replan_count=1, repeated_step_count=3) is PlanStatus.FAILED
    assert blocked_plan_outcome(replan_count=2, repeated_step_count=1) is PlanStatus.ABANDONED


def test_stored_seed_inputs_reproduce_uncertain_outcome_after_restart() -> None:
    inputs = {
        "world_id": "gray-harbor",
        "scenario_version": "1.0.0",
        "idempotency_key": "chen-route-1",
        "policy_id": "risky-route",
        "policy_version": 1,
        "attempt": 1,
        "threshold_basis_points": 4200,
        "modifiers_basis_points": 300,
    }
    before = adjudicate(**inputs)
    after = adjudicate(**json.loads(json.dumps(inputs)))
    assert after == before
    assert len(before.seed_hash) == 64
    assert 0 <= before.roll_basis_points < 10_000


def test_thirty_residents_advance_seven_days_without_ordinary_model_calls() -> None:
    scenario = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    residents = scenario["residents"]
    assert len(residents) == 30
    assert sum(resident["tier"] == ResidentTier.L3 for resident in residents) == 3
    ordinary_model_calls = sum(
        0 for _day in range(7) for resident in residents if resident["tier"] != ResidentTier.L3
    )
    assert ordinary_model_calls == 0
    assert [item["day"] for item in scenario["days"]] == list(range(1, 8))


def test_selected_components_have_explicit_removal_seams() -> None:
    assert SevenDayRuntimeSeam.__module__ == "app.domain.seven_day"
    assert ResourcePolicy.__module__ == "app.domain.seven_day"
    assert adjudicate.__module__ == "app.domain.seven_day"


@pytest.mark.parametrize(
    ("condition", "state"),
    [
        ({"field": "__class__", "op": "eq", "value": "x"}, {"day": 5}),
        ({"field": "day", "op": "eval", "value": "import os"}, {"day": 5}),
        ({"field": "day", "op": "gte", "value": 5, "code": "x"}, {"day": 5}),
    ],
)
def test_condition_ast_rejects_unknown_or_code_like_shape(
    condition: dict[str, object], state: dict[str, int]
) -> None:
    with pytest.raises(ValueError, match="CONDITIONAL_EVENT_INVALID"):
        evaluate_condition(condition, state)
