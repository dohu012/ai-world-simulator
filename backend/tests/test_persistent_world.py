from pathlib import Path
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_world_repository
from app.main import create_app
from app.repositories.worlds import ReplayChain, WorldReplayReadModel
from app.services.demo_world import (
    DemoAgentPerspectiveReadModel,
    DemoWorldSummaryReadModel,
    get_gray_harbor_demo_world,
)


async def _client(repository: AsyncMock) -> AsyncClient:
    app = create_app()
    app.dependency_overrides[get_world_repository] = lambda: repository
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_primary_and_compatibility_observer_endpoints_use_repository() -> None:
    repository = AsyncMock()
    repository.get_observer_world.return_value = get_gray_harbor_demo_world()
    async with await _client(repository) as client:
        primary = await client.get("/demo/worlds/gray-harbor")
        compatibility = await client.get("/demo/worlds/gray-harbor/persistent")
    assert primary.status_code == compatibility.status_code == 200
    assert primary.json() == compatibility.json()
    assert repository.get_observer_world.await_count == 2


async def test_replay_endpoint_exposes_ordered_events_and_chen_chain() -> None:
    demo = get_gray_harbor_demo_world()
    replay = WorldReplayReadModel(
        world_id=demo.world.id,
        events=demo.events,
        observations=demo.observations,
        oracle_requests=demo.oracleRequests,
        oracle_responses=demo.oracleResponses,
        action_intents=demo.actionIntents,
        action_results=demo.actionResults,
        chains=[
            ReplayChain(
                correlation_id="corr-chen-oracle-decision",
                oracle_request_ids=["oracle-request-chen-north-gate"],
                oracle_response_ids=["oracle-response-chen-north-gate"],
                action_intent_ids=["intent-chen-contact-courier"],
                action_result_ids=["result-chen-contact-courier"],
                event_ids=["event-chen-action-result"],
            )
        ],
    )
    repository = AsyncMock()
    repository.get_replay.return_value = replay
    async with await _client(repository) as client:
        body = (await client.get("/demo/worlds/gray-harbor/replay")).json()
    assert [x["occurred_at"] for x in body["events"]] == sorted(
        x["occurred_at"] for x in body["events"]
    )
    assert body["chains"][0] == {
        "correlation_id": "corr-chen-oracle-decision",
        "oracle_request_ids": ["oracle-request-chen-north-gate"],
        "oracle_response_ids": ["oracle-response-chen-north-gate"],
        "action_intent_ids": ["intent-chen-contact-courier"],
        "action_result_ids": ["result-chen-contact-courier"],
        "event_ids": ["event-chen-action-result"],
        "decision_ids": [],
    }


async def test_primary_lin_perspective_excludes_chen_private_records() -> None:
    demo = get_gray_harbor_demo_world()
    lin = next(x for x in demo.characters if x.id == "char-lin-zhixia")
    profile = next(x for x in demo.agentProfiles if x.character_id == lin.id)
    perspective = DemoAgentPerspectiveReadModel(
        world=DemoWorldSummaryReadModel(
            id=demo.world.id,
            name=demo.world.name,
            current_time=demo.world.current_time.isoformat(),
            schema_version=demo.world.schema_version,
            version=demo.world.version,
        ),
        character=lin,
        agentProfile=profile,
        observations=[x for x in demo.observations if x.agent_id == lin.id],
        beliefs=[x for x in demo.beliefs if x.agent_id == lin.id],
        oracleRequests=[],
        oracleResponses=[],
        actionIntents=[],
        actionResults=[],
    )
    repository = AsyncMock()
    repository.get_agent_perspective.return_value = perspective
    async with await _client(repository) as client:
        response = await client.get("/demo/worlds/gray-harbor/agents/char-lin-zhixia/perspective")
    body = response.json()
    assert response.status_code == 200
    assert body["oracleRequests"] == []
    assert body["actionResults"] == []
    assert all(x["agent_id"] == lin.id for x in body["observations"])


async def test_unseeded_world_returns_typed_error_without_fixture_fallback() -> None:
    repository = AsyncMock()
    repository.get_observer_world.return_value = None
    repository.get_agent_perspective.return_value = None
    repository.get_replay.return_value = None
    async with await _client(repository) as client:
        responses = [
            await client.get("/demo/worlds/gray-harbor"),
            await client.get(
                "/demo/worlds/gray-harbor/me/input",
                headers={"X-Demo-Agent-Id": "char-chen-mo"},
            ),
            await client.get("/demo/worlds/gray-harbor/replay"),
        ]
    assert {response.status_code for response in responses} == {404}
    assert {response.json()["error"]["code"] for response in responses} == {"DEMO_WORLD_NOT_SEEDED"}


def test_runtime_routes_do_not_call_fixture_or_issue_sql() -> None:
    routes = Path("app/api/routes/demo_world.py").read_text(encoding="utf-8")
    persistent = Path("app/api/routes/persistent_world.py").read_text(encoding="utf-8")
    route_source = routes + persistent
    assert "get_gray_harbor_demo_world" not in route_source
    assert "sqlalchemy" not in route_source
    assert "select(" not in route_source
