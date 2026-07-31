import pytest

from app.application.seven_day_scenario import build_scenario


def test_full_seven_day_scenario_meets_core_fixture_counts() -> None:
    result = build_scenario(7)
    assert result.current_day == 7
    assert len(result.residents) == 30
    assert sum(resident["tier"] == "L3" for resident in result.residents) == 3
    assert len(result.events) == 7
    assert len({action.action_type for action in result.actions}) >= 5
    assert any(action.status == "rejected" for action in result.actions)
    assert any(plan.status == "completed" for plan in result.plans)
    assert any(plan.status == "abandoned" for plan in result.plans)
    assert len(result.outcomes) == 4
    assert result.model_calls == 0


def test_scenario_is_deterministic_and_resources_never_negative() -> None:
    first = build_scenario(7)
    assert first == build_scenario(7)
    for day in range(8):
        assert all(amount >= 0 for amount in build_scenario(day).resources.values())


def test_future_events_and_outcomes_are_not_exposed() -> None:
    day_four = build_scenario(4)
    assert len(day_four.events) == 4
    assert day_four.outcomes == []
    assert all(action.day <= 4 for action in day_four.actions)


def test_invalid_day_is_rejected() -> None:
    with pytest.raises(ValueError, match="between zero and seven"):
        build_scenario(8)
