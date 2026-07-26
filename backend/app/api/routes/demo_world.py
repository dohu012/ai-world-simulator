"""Database-backed Gray Harbor demo routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.demo_access import require_demo_agent_id
from app.api.dependencies import (
    get_gray_harbor_action_service,
    get_gray_harbor_read_service,
)
from app.api.errors import ApiError
from app.application.action_lifecycle import (
    ActionTransactionUnavailableError,
    DemoActionLifecycleReadModel,
    DemoActionSubmission,
    GrayHarborActionService,
)
from app.application.gray_harbor import (
    GrayHarborAgentNotFoundError,
    GrayHarborNotSeededError,
    GrayHarborReadService,
)
from app.services.demo_world import (
    DemoAgentInputReadModel,
    DemoAgentPerspectiveReadModel,
    DemoWorldReadModel,
)

router = APIRouter(prefix="/demo/worlds", tags=["demo-world"])


def _world_not_seeded() -> ApiError:
    return ApiError(
        status_code=404,
        code="DEMO_WORLD_NOT_SEEDED",
        message="Gray Harbor has not been seeded.",
        details={"world_id": "world-gray-harbor-lockdown"},
    )


@router.get("/gray-harbor", response_model=DemoWorldReadModel)
async def read_gray_harbor_demo_world(
    service: Annotated[GrayHarborReadService, Depends(get_gray_harbor_read_service)],
) -> DemoWorldReadModel:
    try:
        return await service.observer()
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None


@router.get(
    "/gray-harbor/me/perspective",
    response_model=DemoAgentPerspectiveReadModel,
)
async def read_gray_harbor_current_agent_perspective(
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
    service: Annotated[GrayHarborReadService, Depends(get_gray_harbor_read_service)],
) -> DemoAgentPerspectiveReadModel:
    try:
        return await service.agent_perspective(agent_id)
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None
    except GrayHarborAgentNotFoundError:
        raise ApiError(
            status_code=403,
            code="DEMO_AGENT_FORBIDDEN",
            message="Demo agent is not allowed to use this endpoint.",
            details={"agent_id": agent_id},
        ) from None


@router.get("/gray-harbor/me/input", response_model=DemoAgentInputReadModel)
async def read_gray_harbor_current_agent_input(
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
    service: Annotated[GrayHarborReadService, Depends(get_gray_harbor_read_service)],
) -> DemoAgentInputReadModel:
    try:
        return await service.agent_input(agent_id)
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None
    except GrayHarborAgentNotFoundError:
        raise ApiError(
            status_code=403,
            code="DEMO_AGENT_FORBIDDEN",
            message="Demo agent is not allowed to use this endpoint.",
            details={"agent_id": agent_id},
        ) from None


@router.get(
    "/gray-harbor/agents/{agent_id}/perspective",
    response_model=DemoAgentPerspectiveReadModel,
)
async def read_gray_harbor_agent_perspective(
    agent_id: str,
    service: Annotated[GrayHarborReadService, Depends(get_gray_harbor_read_service)],
) -> DemoAgentPerspectiveReadModel:
    try:
        return await service.agent_perspective(agent_id)
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None
    except GrayHarborAgentNotFoundError:
        raise ApiError(
            status_code=404,
            code="DEMO_AGENT_NOT_FOUND",
            message="Demo agent was not found.",
            details={"agent_id": agent_id},
        ) from None


@router.post(
    "/gray-harbor/me/actions",
    response_model=DemoActionLifecycleReadModel,
)
async def submit_gray_harbor_current_agent_action(
    submission: DemoActionSubmission,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
    service: Annotated[GrayHarborActionService, Depends(get_gray_harbor_action_service)],
) -> DemoActionLifecycleReadModel:
    """Validate and adjudicate one idempotent demo action."""
    try:
        return await service.submit(agent_id, submission)
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None
    except GrayHarborAgentNotFoundError:
        raise ApiError(
            status_code=403,
            code="DEMO_AGENT_FORBIDDEN",
            message="Demo agent is not allowed to act in this world.",
            details={"agent_id": agent_id},
        ) from None
    except ActionTransactionUnavailableError:
        raise ApiError(
            status_code=503,
            code="ACTION_TRANSACTION_UNAVAILABLE",
            message="The action transaction could not be completed safely; retry later.",
            details={"world_id": "world-gray-harbor-lockdown"},
        ) from None
