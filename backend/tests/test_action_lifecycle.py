from unittest.mock import AsyncMock

import pytest

from app.application.action_lifecycle import (
    DemoActionSubmission,
    GrayHarborActionService,
)
from app.domain.enums import ActionType
from app.services.demo_world import get_gray_harbor_demo_world


@pytest.fixture
def repository() -> AsyncMock:
    value = AsyncMock()
    value.get_action_lifecycle.return_value = None
    value.get_observer_world.return_value = get_gray_harbor_demo_world()
    return value


async def test_wait_action_succeeds_and_emits_private_event(repository: AsyncMock) -> None:
    response = await GrayHarborActionService(repository).submit(
        "char-lin-zhixia",
        DemoActionSubmission(
            idempotency_key="lin-wait-1",
            action_type=ActionType.WAIT,
            parameters={},
            reason_summary="Wait for more observations.",
        ),
    )
    assert response.result.status == "succeeded"
    assert response.event is not None
    assert response.event.visibility == "private"
    assert response.event.source_action_id == response.intent.id
    repository.persist_action_lifecycle.assert_awaited_once()


async def test_unsupported_action_is_rejected_without_event(
    repository: AsyncMock,
) -> None:
    response = await GrayHarborActionService(repository).submit(
        "char-lin-zhixia",
        DemoActionSubmission(
            idempotency_key="lin-move-1",
            action_type=ActionType.MOVE,
            parameters={"target": "north-gate"},
            reason_summary="Try to move.",
        ),
    )
    assert response.result.status == "rejected"
    assert response.result.failure_code == "MOVE_PARAMETERS_INVALID"
    assert response.event is None


async def test_existing_lifecycle_is_returned_without_second_write(
    repository: AsyncMock,
) -> None:
    service = GrayHarborActionService(repository)
    submission = DemoActionSubmission(
        idempotency_key="same-key",
        action_type=ActionType.WAIT,
        parameters={},
        reason_summary="Wait.",
    )
    first = await service.submit("char-chen-mo", submission)
    repository.get_action_lifecycle.return_value = (
        first.intent,
        first.result,
        first.event,
    )
    second = await service.submit("char-chen-mo", submission)
    assert second.idempotent_replay is True
    assert second.intent.id == first.intent.id
    assert repository.persist_action_lifecycle.await_count == 1
