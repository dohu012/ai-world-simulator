from httpx import AsyncClient


async def test_current_agent_wait_action_completes_lifecycle(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/demo/worlds/gray-harbor/me/actions",
        headers={"X-Demo-Agent-Id": "char-lin-zhixia"},
        json={
            "idempotency_key": "api-lin-wait-1",
            "action_type": "wait",
            "parameters": {},
            "reason_summary": "Wait for verified information.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["intent"]["actor_id"] == "char-lin-zhixia"
    assert body["result"]["status"] == "succeeded"
    assert body["event"]["visibility"] == "private"
    assert body["event"]["source_action_id"] == body["intent"]["id"]
    assert body["idempotent_replay"] is False


async def test_current_agent_unsupported_action_is_auditable_rejection(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/demo/worlds/gray-harbor/me/actions",
        headers={"X-Demo-Agent-Id": "char-lin-zhixia"},
        json={
            "idempotency_key": "api-lin-move-1",
            "action_type": "move",
            "parameters": {"target": "north-gate"},
            "reason_summary": "Move toward the gate.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"] == "rejected"
    assert body["result"]["failure_code"] == "MOVE_PARAMETERS_INVALID"
    assert body["event"] is None


async def test_current_agent_action_requires_demo_identity(client: AsyncClient) -> None:
    response = await client.post(
        "/demo/worlds/gray-harbor/me/actions",
        json={
            "idempotency_key": "missing-agent",
            "action_type": "wait",
            "parameters": {},
            "reason_summary": "Wait.",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "DEMO_AGENT_ID_REQUIRED"


async def test_move_lock_failure_maps_to_stable_operational_error() -> None:
    from unittest.mock import AsyncMock

    from httpx import ASGITransport

    from app.api.dependencies import get_world_repository
    from app.core.config import Settings
    from app.main import create_app
    from app.repositories.worlds import WorldTransactionError
    from app.services.demo_world import get_gray_harbor_demo_world

    repository = AsyncMock()
    repository.get_action_lifecycle.return_value = None
    repository.get_observer_world.return_value = get_gray_harbor_demo_world()
    repository.lock_move_state.side_effect = WorldTransactionError("lock timeout")
    app = create_app(
        Settings(
            database_url="postgresql+asyncpg://simulator:simulator@localhost:5432/simulator",
            redis_url="redis://localhost:6379/0",
        )
    )
    app.dependency_overrides[get_world_repository] = lambda: repository
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as local_client:
        response = await local_client.post(
            "/demo/worlds/gray-harbor/me/actions",
            headers={"X-Demo-Agent-Id": "char-chen-mo"},
            json={
                "idempotency_key": "lock-timeout-api",
                "action_type": "move",
                "parameters": {
                    "target_location_id": "north-market-street",
                    "expected_character_version": 1,
                    "expected_world_version": 1,
                },
                "reason_summary": "Move if transaction is available.",
            },
        )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ACTION_TRANSACTION_UNAVAILABLE"
