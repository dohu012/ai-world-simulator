"""Gray Harbor persistence compatibility and observer replay routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_gray_harbor_read_service
from app.api.errors import ApiError
from app.application.gray_harbor import GrayHarborNotSeededError, GrayHarborReadService
from app.repositories.worlds import WorldReplayReadModel
from app.services.demo_world import DemoWorldReadModel

router = APIRouter(prefix="/demo/worlds/gray-harbor", tags=["demo-world"])


def _world_not_seeded() -> ApiError:
    return ApiError(
        status_code=404,
        code="DEMO_WORLD_NOT_SEEDED",
        message="Gray Harbor has not been seeded.",
        details={"world_id": "world-gray-harbor-lockdown"},
    )


@router.get("/persistent", response_model=DemoWorldReadModel)
async def read_persisted_world(
    service: Annotated[GrayHarborReadService, Depends(get_gray_harbor_read_service)],
) -> DemoWorldReadModel:
    """Compatibility alias for the primary observer read."""
    try:
        return await service.observer()
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None


@router.get("/replay", response_model=WorldReplayReadModel)
async def read_world_replay(
    service: Annotated[GrayHarborReadService, Depends(get_gray_harbor_read_service)],
) -> WorldReplayReadModel:
    try:
        return await service.replay()
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None
