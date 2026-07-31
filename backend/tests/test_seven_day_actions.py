from datetime import UTC, datetime

import pytest

from app.application.action_validator import ActionValidator, ScenarioActionState
from app.domain.enums import ActionStatus, ActionType
from app.domain.schemas import ActionIntent
from app.world_engine.gray_harbor import GrayHarborWorldEngine, ScenarioMutationPlan


def intent(action_type: ActionType, affordance_id: str, actor_id: str) -> ActionIntent:
    return ActionIntent(
        id=f"intent-{action_type.value}",
        world_id="world-gray-harbor-lockdown",
        actor_id=actor_id,
        action_type=action_type,
        parameters={"affordance_id": affordance_id},
        reason_summary="Execute the offered scenario action.",
        submitted_at=datetime(2026, 7, 28, tzinfo=UTC),
        expected_duration=1,
        correlation_id=f"corr-{action_type.value}",
        schema_version="1.0",
    )


@pytest.mark.parametrize(
    ("action_type", "affordance", "actor_id"),
    [
        (ActionType.CONSUME_RESOURCE, "gh-v1:consume-medicine", "char-lin-zhixia"),
        (ActionType.TRANSFER_RESOURCE, "gh-v1:transfer-food", "char-chen-mo"),
        (ActionType.QUEUE_FOR_SERVICE, "gh-v1:queue-checkpoint", "char-zhou-qiming"),
        (ActionType.HELP_CHARACTER, "gh-v1:help-luo", "char-chen-mo"),
        (ActionType.ATTEMPT_ROUTE, "gh-v1:route-clinic", "char-zhou-qiming"),
        (ActionType.ABANDON_PLAN, "gh-v1:abandon-store-plan", "char-chen-mo"),
        (
            ActionType.QUEUE_FOR_SERVICE,
            "gh-v1:allocate-rescue-seats",
            "char-zhou-qiming",
        ),
        (ActionType.HELP_CHARACTER, "gh-v1:complete-triage", "char-lin-zhixia"),
    ],
)
def test_server_offered_actions_traverse_validator_and_world_engine(
    action_type: ActionType, affordance: str, actor_id: str
) -> None:
    action = intent(action_type, affordance, actor_id)
    validation = ActionValidator().validate(
        action,
        scenario_state=ScenarioActionState(available=10, required=1, plan_status="active"),
    )
    assert validation.accepted
    adjudication = GrayHarborWorldEngine().adjudicate(action, validation)
    assert adjudication.result.status is ActionStatus.SUCCEEDED
    assert adjudication.event is not None
    assert adjudication.event.source_action_id == action.id
    assert adjudication.event.metadata["affordance_id"] == affordance
    if affordance in {
        "gh-v1:consume-medicine",
        "gh-v1:transfer-food",
        "gh-v1:help-luo",
        "gh-v1:abandon-store-plan",
        "gh-v1:allocate-rescue-seats",
        "gh-v1:complete-triage",
    }:
        assert isinstance(adjudication.mutation, ScenarioMutationPlan)


def test_forged_affordance_is_rejected_without_event_or_mutation() -> None:
    action = intent(ActionType.TRANSFER_RESOURCE, "gh-v1:route-clinic", "char-chen-mo")
    validation = ActionValidator().validate(action, scenario_state=ScenarioActionState())
    assert validation.failure_code == "ACTION_TARGET_NOT_ALLOWED"
    adjudication = GrayHarborWorldEngine().adjudicate(action, validation)
    assert adjudication.result.status is ActionStatus.REJECTED
    assert adjudication.event is None
    assert adjudication.mutation is None


def test_depleted_resource_is_rejected_by_validator_before_world_engine() -> None:
    action = intent(ActionType.TRANSFER_RESOURCE, "gh-v1:transfer-food", "char-chen-mo")
    validation = ActionValidator().validate(
        action, scenario_state=ScenarioActionState(available=3, required=4)
    )
    assert validation.failure_code == "RESOURCE_INSUFFICIENT"
    assert GrayHarborWorldEngine().adjudicate(action, validation).mutation is None
