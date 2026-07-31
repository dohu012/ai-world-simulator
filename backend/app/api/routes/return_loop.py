"""Owner-scoped, no-store offline return-loop API."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response

from app.api.demo_access import require_demo_agent_id
from app.application.return_loop_service import ReturnLoopService, ReturnLoopState

router = APIRouter(prefix="/demo/worlds/gray-harbor/me/return-loop", tags=["return-loop"])


def service(request: Request) -> ReturnLoopService:
    return ReturnLoopService(request.app.state.database.session_factory)


def require_csrf(
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    if x_csrf_token != "demo-return-loop":
        raise HTTPException(status_code=403, detail="CSRF validation failed")


@router.get("", response_model=ReturnLoopState)
async def read_return_loop(
    request: Request,
    response: Response,
    owner_id: Annotated[str, Depends(require_demo_agent_id)],
) -> ReturnLoopState:
    response.headers["Cache-Control"] = "no-store"
    return await service(request).state(owner_id)


@router.post(
    "/inbox/{item_id}/{action}",
    status_code=204,
    dependencies=[Depends(require_csrf)],
)
async def mutate_inbox(
    request: Request,
    response: Response,
    item_id: str,
    action: Literal["read", "dismiss", "archive"],
    owner_id: Annotated[str, Depends(require_demo_agent_id)],
) -> None:
    response.headers["Cache-Control"] = "no-store"
    if not await service(request).mark(owner_id, item_id, action):
        raise HTTPException(status_code=404, detail="item unavailable")


@router.post("/events/{event_code}", status_code=204, dependencies=[Depends(require_csrf)])
async def record_minimized_event(
    request: Request,
    response: Response,
    event_code: str,
    owner_id: Annotated[str, Depends(require_demo_agent_id)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> None:
    allowed = {
        "summary_view",
        "causal_link",
        "permission_offer",
        "permission_deny",
        "permission_accept",
        "dismiss",
        "return_intention",
    }
    if event_code not in allowed:
        raise HTTPException(status_code=422, detail="undeclared event")
    if not idempotency_key or len(idempotency_key) > 128:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")
    response.headers["Cache-Control"] = "no-store"
    await service(request).record_event(owner_id, event_code, idempotency_key)
