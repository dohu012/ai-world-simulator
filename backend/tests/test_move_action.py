from unittest.mock import AsyncMock

import pytest

from app.application.action_lifecycle import DemoActionSubmission, GrayHarborActionService
from app.application.action_validator import ActionValidator, MoveState
from app.domain.enums import ActionType, CharacterStatus
from app.domain.schemas import ActionIntent
from app.services.demo_world import get_gray_harbor_demo_world


def move_state(*, character_version: int = 1, world_version: int = 1) -> MoveState:
    demo = get_gray_harbor_demo_world()
    actor = next(item for item in demo.characters if item.id == "char-chen-mo").model_copy(
        update={"version": character_version, "status": CharacterStatus.ACTIVE}
    )
    return MoveState(
        world=demo.world.model_copy(update={"version": world_version}),
        actor=actor,
        location_ids=frozenset(
            {"north-market-store", "north-market-street", "emergency-shelter", "north-gate"}
        ),
        directed_edges=frozenset({("north-market-store", "north-market-street")}),
        destination_witness_ids=("char-market-witness",),
    )


def intent(parameters: dict[str, object]) -> ActionIntent:
    demo = get_gray_harbor_demo_world()
    return ActionIntent(
        id="intent-move-test",
        world_id=demo.world.id,
        actor_id="char-chen-mo",
        action_type=ActionType.MOVE,
        parameters=parameters,
        reason_summary="private reason",
        submitted_at=demo.world.current_time,
        expected_duration=0.0,
        correlation_id="corr-move-test",
        schema_version="1.0",
    )


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"target_location_id": "north-market-street", "expected_character_version": 1},
        {
            "target_location_id": "north-market-street",
            "expected_character_version": True,
            "expected_world_version": 1,
        },
        {
            "target_location_id": "north-market-street",
            "expected_character_version": 1,
            "expected_world_version": 1,
            "witnesses": [],
        },
    ],
)
def test_move_parameters_are_strict(parameters: dict[str, object]) -> None:
    result = ActionValidator().validate(intent(parameters), move_state())
    assert result.failure_code == "MOVE_PARAMETERS_INVALID"


@pytest.mark.parametrize(
    ("parameters", "code"),
    [
        (
            {
                "target_location_id": "north-market-store",
                "expected_character_version": 1,
                "expected_world_version": 1,
            },
            "MOVE_SAME_LOCATION",
        ),
        (
            {
                "target_location_id": "north-gate",
                "expected_character_version": 1,
                "expected_world_version": 1,
            },
            "MOVE_NOT_REACHABLE",
        ),
        (
            {
                "target_location_id": "missing",
                "expected_character_version": 1,
                "expected_world_version": 1,
            },
            "TARGET_LOCATION_NOT_FOUND",
        ),
        (
            {
                "target_location_id": "north-market-street",
                "expected_character_version": 2,
                "expected_world_version": 1,
            },
            "CHARACTER_VERSION_CONFLICT",
        ),
        (
            {
                "target_location_id": "north-market-street",
                "expected_character_version": 1,
                "expected_world_version": 2,
            },
            "WORLD_VERSION_CONFLICT",
        ),
    ],
)
def test_move_state_rejections(parameters: dict[str, object], code: str) -> None:
    assert ActionValidator().validate(intent(parameters), move_state()).failure_code == code


async def test_valid_move_builds_exact_mutation_event_and_isolated_observations() -> None:
    demo = get_gray_harbor_demo_world()
    repository = AsyncMock()
    repository.get_action_lifecycle.return_value = None
    repository.get_observer_world.return_value = demo
    repository.lock_move_state.return_value = move_state()
    repository.destination_witness_ids.return_value = ("char-market-witness",)
    response = await GrayHarborActionService(repository).submit(
        "char-chen-mo",
        DemoActionSubmission(
            idempotency_key="chen-move-street",
            action_type=ActionType.MOVE,
            parameters={
                "target_location_id": "north-market-street",
                "expected_character_version": 1,
                "expected_world_version": 1,
            },
            reason_summary="private reason must not leak",
        ),
    )
    assert response.result.status == "succeeded"
    assert [
        (x.entity_type, x.field, x.old_value, x.new_value) for x in response.result.state_changes
    ] == [
        ("character", "location_id", "north-market-store", "north-market-street"),
        ("character", "version", 1, 2),
        ("world", "version", 1, 2),
    ]
    assert response.event is not None and response.event.event_type == "movement"
    assert "private reason" not in response.event.description
    args = repository.persist_action_lifecycle.await_args.args
    observations = args[3]
    mutation = args[4]
    assert mutation.character.location_id == "north-market-street"
    assert mutation.character.version == 2 and mutation.world.version == 2
    assert {item.agent_id for item in observations} == {"char-chen-mo"}
