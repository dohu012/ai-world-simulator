"""FastAPI infrastructure dependencies."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.action_lifecycle import GrayHarborActionService
from app.application.agent_decision import AgentDecisionApplicationService
from app.application.gray_harbor import GrayHarborReadService
from app.application.runtime_service import PostgresWorldRuntimeAdapter
from app.core.config import Settings
from app.model_gateway.factory import build_model_gateway
from app.repositories.worlds import WorldRepository


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.database.session_factory() as session:
        yield session


def get_world_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorldRepository:
    return WorldRepository(session)


def get_agent_decision_service(request: Request) -> AgentDecisionApplicationService:
    settings: Settings = request.app.state.settings
    return AgentDecisionApplicationService(
        request.app.state.database.session_factory,
        build_model_gateway(settings),
        max_attempts=settings.model_max_attempts,
        timeout_seconds=settings.model_timeout_seconds,
        max_output_tokens=settings.model_max_output_tokens,
    )


def get_world_runtime_service(request: Request) -> PostgresWorldRuntimeAdapter:
    settings: Settings = request.app.state.settings
    return PostgresWorldRuntimeAdapter(
        request.app.state.database.session_factory,
        enabled=settings.world_runtime_enabled,
        gateway=build_model_gateway(settings),
        model_max_attempts=settings.model_max_attempts,
        model_timeout_seconds=settings.model_timeout_seconds,
        model_max_output_tokens=settings.model_max_output_tokens,
    )


def get_gray_harbor_read_service(
    repository: Annotated[WorldRepository, Depends(get_world_repository)],
) -> GrayHarborReadService:
    return GrayHarborReadService(repository)


def get_gray_harbor_action_service(
    repository: Annotated[WorldRepository, Depends(get_world_repository)],
) -> GrayHarborActionService:
    return GrayHarborActionService(repository)
