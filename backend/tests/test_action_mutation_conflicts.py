"""Write-time mutation failures stay auditable rejections, not unhandled errors.

Validation runs against a snapshot taken before the mutation is written. When the
write-time re-check overrules it — a lost optimistic race or an account that ran
dry — the lifecycle must still be persisted as REJECTED so the attempt appears in
the audit trail, instead of escaping as an unhandled 500 with no record at all.
"""

from unittest.mock import AsyncMock

import pytest

from app.application.action_lifecycle import (
    DemoActionSubmission,
    GrayHarborActionService,
)
from app.application.action_validator import ScenarioActionState
from app.domain.enums import ActionStatus, ActionType
from app.repositories.worlds import (
    ActionLifecycleConflictError,
    MutationConflictError,
    MutationRejectedError,
    WorldTransactionError,
)
from app.services.demo_world import get_gray_harbor_demo_world


@pytest.fixture
def repository() -> AsyncMock:
    value = AsyncMock()
    value.get_action_lifecycle.return_value = None
    value.get_observer_world.return_value = get_gray_harbor_demo_world()
    # The affordance passes up-front validation; only the write-time re-check fails.
    value.lock_scenario_action_state.return_value = ScenarioActionState(available=10, required=4)
    return value


def transfer_food() -> DemoActionSubmission:
    return DemoActionSubmission(
        idempotency_key="chen-transfer-1",
        action_type=ActionType.TRANSFER_RESOURCE,
        parameters={"affordance_id": "gh-v1:transfer-food"},
        reason_summary="Transfer food to the Sun household.",
    )


async def test_accepted_scenario_action_still_succeeds(repository: AsyncMock) -> None:
    response = await GrayHarborActionService(repository).submit("char-chen-mo", transfer_food())
    assert response.result.status is ActionStatus.SUCCEEDED
    assert repository.persist_action_lifecycle.await_count == 1


async def test_write_time_resource_exhaustion_persists_a_rejected_result(
    repository: AsyncMock,
) -> None:
    repository.persist_action_lifecycle.side_effect = [
        MutationRejectedError("RESOURCE_INSUFFICIENT", "The offered resource is no longer."),
        None,
    ]
    response = await GrayHarborActionService(repository).submit("char-chen-mo", transfer_food())
    assert response.result.status is ActionStatus.REJECTED
    assert response.result.failure_code == "RESOURCE_INSUFFICIENT"
    assert response.result.state_changes == []
    assert response.event is None
    assert response.idempotent_replay is False
    # Rejected lifecycles carry no mutation: the second call must persist the audit
    # record only, never re-attempt the objective change.
    assert repository.persist_action_lifecycle.await_count == 2
    second = repository.persist_action_lifecycle.await_args_list[1]
    assert second.args[0].id == response.intent.id
    assert second.args[2] is None and second.args[4] is None


async def test_lost_optimistic_race_persists_a_conflict_rejection(repository: AsyncMock) -> None:
    repository.persist_action_lifecycle.side_effect = [
        MutationConflictError("stale version"),
        None,
    ]
    response = await GrayHarborActionService(repository).submit("char-chen-mo", transfer_food())
    assert response.result.status is ActionStatus.REJECTED
    assert response.result.failure_code == "MUTATION_STATE_CONFLICT"
    assert response.event is None


async def test_concurrent_writer_of_same_key_yields_the_persisted_replay(
    repository: AsyncMock,
) -> None:
    service = GrayHarborActionService(repository)
    first = await service.submit("char-chen-mo", transfer_food())
    repository.get_action_lifecycle.return_value = (first.intent, first.result, first.event)
    repository.persist_action_lifecycle.side_effect = [
        MutationConflictError("stale version"),
        ActionLifecycleConflictError(),
    ]
    replay = await service.submit("char-chen-mo", transfer_food())
    assert replay.idempotent_replay is True
    assert replay.result.status is ActionStatus.SUCCEEDED


async def test_infrastructure_failure_while_recording_rejection_still_surfaces(
    repository: AsyncMock,
) -> None:
    from app.application.action_lifecycle import ActionTransactionUnavailableError

    repository.persist_action_lifecycle.side_effect = [
        MutationConflictError("stale version"),
        WorldTransactionError("deadlock"),
    ]
    with pytest.raises(ActionTransactionUnavailableError):
        await GrayHarborActionService(repository).submit("char-chen-mo", transfer_food())
