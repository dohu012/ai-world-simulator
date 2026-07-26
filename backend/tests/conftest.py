from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_world_repository
from app.application.observation_builder import ObservationBuilder
from app.core.config import Settings
from app.main import create_app
from app.repositories.worlds import ReplayChain, WorldReplayReadModel
from app.services.demo_world import (
    get_gray_harbor_agent_perspective,
    get_gray_harbor_demo_world,
)


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Use a repository double; route behavior must still cross the app service."""
    settings = Settings(
        database_url="postgresql+asyncpg://simulator:simulator@localhost:5432/simulator",
        redis_url="redis://localhost:6379/0",
    )
    app = create_app(settings)
    demo = get_gray_harbor_demo_world()
    builder = ObservationBuilder()
    persisted_observations = builder.build_for_events(
        demo.events,
        demo.characters,
        additional_recipients={"event-day3-guards": ["char-chen-mo"]},
        observation_id_overrides={
            ("event-day1-fever", "char-lin-zhixia"): "obs-lin-fever",
            ("event-day2-north-gate-plan", "char-zhou-qiming"): "obs-zhou-plan",
            ("event-day3-guards", "char-chen-mo"): "obs-chen-rumor",
        },
    )
    persisted_observations.append(
        builder.build_for_oracle(demo.oracleRequests[0], demo.oracleResponses[0])
    )
    demo = demo.model_copy(update={"observations": persisted_observations})
    repository = AsyncMock()
    repository.get_action_lifecycle.return_value = None
    repository.get_observer_world.return_value = demo

    def perspective_for(_world_id: str, agent_id: str):
        perspective = get_gray_harbor_agent_perspective(agent_id)
        if perspective is None:
            return None
        return perspective.model_copy(
            update={
                "observations": [
                    item for item in persisted_observations if item.agent_id == agent_id
                ]
            }
        )

    repository.get_agent_perspective.side_effect = perspective_for
    repository.get_replay.return_value = WorldReplayReadModel(
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
    app.dependency_overrides[get_world_repository] = lambda: repository
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
