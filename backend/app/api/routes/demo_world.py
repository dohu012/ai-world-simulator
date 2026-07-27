"""Database-backed Gray Harbor demo routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.demo_access import require_demo_agent_id
from app.api.dependencies import (
    get_agent_decision_service,
    get_gray_harbor_action_service,
    get_gray_harbor_read_service,
    get_world_runtime_service,
)
from app.api.errors import ApiError
from app.application.action_lifecycle import (
    ActionTransactionUnavailableError,
    DemoActionLifecycleReadModel,
    DemoActionSubmission,
    GrayHarborActionService,
)
from app.application.agent_decision import (
    AgentDecisionApplicationService,
    AgentDecisionReadModel,
    DecisionInProgressError,
    DecisionSubmission,
)
from app.application.gray_harbor import (
    GrayHarborAgentNotFoundError,
    GrayHarborNotSeededError,
    GrayHarborReadService,
)
from app.application.runtime_service import (
    AdvanceCommand,
    NotificationRead,
    OracleReplyCommand,
    OracleWindowClosedError,
    OracleWindowRead,
    PostgresWorldRuntimeAdapter,
    RuntimeDisabledError,
    RuntimeRead,
    RuntimeStateError,
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


@router.post("/gray-harbor/me/decisions", response_model=AgentDecisionReadModel)
async def submit_gray_harbor_current_agent_decision(
    submission: DecisionSubmission,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
    service: Annotated[AgentDecisionApplicationService, Depends(get_agent_decision_service)],
) -> AgentDecisionReadModel:
    try:
        return await service.decide(agent_id, submission)
    except DecisionInProgressError:
        raise ApiError(
            status_code=409,
            code="DECISION_IN_PROGRESS",
            message="This decision is already being processed.",
            details=None,
        ) from None
    except GrayHarborNotSeededError:
        raise _world_not_seeded() from None
    except GrayHarborAgentNotFoundError:
        raise ApiError(
            status_code=403,
            code="DEMO_AGENT_FORBIDDEN",
            message="Demo agent is not allowed to decide.",
            details={"agent_id": agent_id},
        ) from None


def _runtime_error(exc: Exception) -> ApiError:
    if isinstance(exc, RuntimeDisabledError):
        return ApiError(503, "WORLD_RUNTIME_DISABLED", "The durable world runtime is disabled.")
    code = str(exc) if str(exc) else "WORKFLOW_TEMPORARILY_UNAVAILABLE"
    status = 409 if "CONFLICT" in code or "PAUSED" in code else 404
    return ApiError(status, code, "The durable runtime command could not be applied.")


@router.post("/gray-harbor/runtime/start", response_model=RuntimeRead)
async def start_runtime(
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> RuntimeRead:
    try:
        return await service.start()
    except (RuntimeDisabledError, RuntimeStateError) as exc:
        raise _runtime_error(exc) from None


@router.post("/gray-harbor/runtime/pause", response_model=RuntimeRead)
async def pause_runtime(
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> RuntimeRead:
    try:
        return await service.set_status("paused")
    except (RuntimeDisabledError, RuntimeStateError) as exc:
        raise _runtime_error(exc) from None


@router.post("/gray-harbor/runtime/resume", response_model=RuntimeRead)
async def resume_runtime(
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> RuntimeRead:
    try:
        return await service.set_status("running")
    except (RuntimeDisabledError, RuntimeStateError) as exc:
        raise _runtime_error(exc) from None


@router.post("/gray-harbor/runtime/advance", response_model=RuntimeRead)
async def advance_runtime(
    command: AdvanceCommand,
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> RuntimeRead:
    try:
        return await service.advance(command)
    except (RuntimeDisabledError, RuntimeStateError) as exc:
        raise _runtime_error(exc) from None


@router.get("/gray-harbor/runtime", response_model=RuntimeRead)
async def read_runtime(
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> RuntimeRead:
    try:
        return await service.read()
    except RuntimeStateError as exc:
        raise _runtime_error(exc) from None


@router.get("/gray-harbor/oracle-requests", response_model=list[OracleWindowRead])
async def read_oracle_requests(
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> list[OracleWindowRead]:
    return await service.windows()


@router.post("/gray-harbor/oracle-requests/{request_id}/responses", response_model=OracleWindowRead)
async def respond_to_oracle(
    request_id: str,
    command: OracleReplyCommand,
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> OracleWindowRead:
    try:
        return await service.reply(request_id, command)
    except OracleWindowClosedError:
        raise ApiError(
            409, "ORACLE_WINDOW_CLOSED", "The Oracle window is already closed."
        ) from None


@router.get("/gray-harbor/notifications", response_model=list[NotificationRead])
async def read_notifications(
    service: Annotated[PostgresWorldRuntimeAdapter, Depends(get_world_runtime_service)],
) -> list[NotificationRead]:
    return await service.notifications()
