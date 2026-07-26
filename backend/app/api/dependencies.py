"""FastAPI infrastructure dependencies."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.action_lifecycle import GrayHarborActionService
from app.application.gray_harbor import GrayHarborReadService
from app.repositories.worlds import WorldRepository


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.database.session_factory() as session:
        yield session


def get_world_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorldRepository:
    return WorldRepository(session)


def get_gray_harbor_read_service(
    repository: Annotated[WorldRepository, Depends(get_world_repository)],
) -> GrayHarborReadService:
    return GrayHarborReadService(repository)


def get_gray_harbor_action_service(
    repository: Annotated[WorldRepository, Depends(get_world_repository)],
) -> GrayHarborActionService:
    return GrayHarborActionService(repository)
