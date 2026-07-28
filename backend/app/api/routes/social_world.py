"""Observer and owner-scoped Task 18 social-world APIs."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.demo_access import require_demo_agent_id
from app.api.errors import ApiError
from app.application.social_runtime import (
    BeliefRevisionRead,
    ConversationRead,
    PropagationItemRead,
    SocialRuntimeService,
)

router = APIRouter(prefix="/demo/worlds/gray-harbor", tags=["social-world"])


def service(request: Request) -> SocialRuntimeService:
    return SocialRuntimeService(request.app.state.database.session_factory)


@router.get("/propagation", response_model=list[PropagationItemRead])
async def propagation(request: Request) -> list[PropagationItemRead]:
    runtime = service(request)
    await runtime.seed_scenario()
    await runtime.deliver_due()
    return await runtime.propagation()


@router.get("/beliefs/history", response_model=list[BeliefRevisionRead])
async def observer_beliefs(request: Request) -> list[BeliefRevisionRead]:
    return await service(request).beliefs()


@router.get("/me/beliefs/history", response_model=list[BeliefRevisionRead])
async def own_beliefs(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> list[BeliefRevisionRead]:
    return await service(request).beliefs(agent_id)


@router.get("/me/messages", response_model=list[PropagationItemRead])
async def own_messages(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> list[PropagationItemRead]:
    return [item for item in await service(request).propagation() if item.recipient_id == agent_id]


@router.get("/conversations", response_model=list[ConversationRead])
async def conversations(request: Request) -> list[ConversationRead]:
    return await service(request).conversations()


@router.post("/me/conversations/correction", response_model=ConversationRead)
async def open_correction(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> ConversationRead:
    if agent_id != "char-chen-mo":
        raise ApiError(
            status_code=403,
            code="MESSAGE_RECIPIENT_NOT_ALLOWED",
            message="Only Chen can open the fixed correction dialogue.",
            details={"agent_id": agent_id},
        )
    return await service(request).open_correction_dialogue()
