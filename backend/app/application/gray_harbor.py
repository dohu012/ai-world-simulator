"""Database-backed Gray Harbor read use cases."""

from app.repositories.worlds import WorldReplayReadModel, WorldRepository
from app.services.demo_world import (
    DemoAgentInputReadModel,
    DemoAgentPerspectiveReadModel,
    DemoWorldReadModel,
)

WORLD_ID = "world-gray-harbor-lockdown"


class GrayHarborNotSeededError(Exception):
    """The fixed application seed is absent."""


class GrayHarborAgentNotFoundError(Exception):
    """The requested agent is absent from the fixed application seed."""


class GrayHarborReadService:
    """Compose all Gray Harbor read models without fixture fallback."""

    def __init__(self, repository: WorldRepository) -> None:
        self.repository = repository

    async def observer(self) -> DemoWorldReadModel:
        result = await self.repository.get_observer_world(WORLD_ID)
        if result is None:
            raise GrayHarborNotSeededError
        return result

    async def agent_perspective(self, agent_id: str) -> DemoAgentPerspectiveReadModel:
        result = await self.repository.get_agent_perspective(WORLD_ID, agent_id)
        if result is not None:
            return result
        if await self.repository.get_observer_world(WORLD_ID) is None:
            raise GrayHarborNotSeededError
        raise GrayHarborAgentNotFoundError(agent_id)

    async def agent_input(self, agent_id: str) -> DemoAgentInputReadModel:
        perspective = await self.agent_perspective(agent_id)
        observations = list(perspective.observations)
        return DemoAgentInputReadModel(
            world=perspective.world,
            character=perspective.character,
            agentProfile=perspective.agentProfile,
            observations=observations,
        )

    async def replay(self) -> WorldReplayReadModel:
        result = await self.repository.get_replay(WORLD_ID)
        if result is None:
            raise GrayHarborNotSeededError
        return result
