"""TASK-019 reset, advance, observer, and owner-scoped APIs."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict

from app.api.demo_access import require_demo_agent_id
from app.application.seven_day_scenario import (
    SevenDayScenarioRead,
    SevenDayScenarioService,
)
from app.domain.enums import ActionType

router = APIRouter(prefix="/demo/worlds/gray-harbor", tags=["seven-day-scenario"])


class ScenarioAffordance(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    action_type: ActionType
    available_day: int


def service(request: Request) -> SevenDayScenarioService:
    return SevenDayScenarioService(request.app.state.database.session_factory)


@router.get("/scenario", response_model=SevenDayScenarioRead)
async def scenario(request: Request) -> SevenDayScenarioRead:
    return await service(request).read()


@router.post("/scenario/reset", response_model=SevenDayScenarioRead)
async def reset(request: Request) -> SevenDayScenarioRead:
    return await service(request).reset()


@router.get("/me/scenario", response_model=SevenDayScenarioRead)
async def own_scenario(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> SevenDayScenarioRead:
    state = await service(request).read()
    return state.model_copy(
        update={
            "residents": [resident for resident in state.residents if resident["id"] == agent_id],
            "plans": [plan for plan in state.plans if plan.owner_id == agent_id],
            "actions": [action for action in state.actions if action.actor_id == agent_id],
            "outcomes": [],
        }
    )


@router.get("/me/scenario/affordances", response_model=list[ScenarioAffordance])
async def own_affordances(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> list[ScenarioAffordance]:
    state = await service(request).read()
    offered = {
        "char-lin-zhixia": (
            ("gh-v1:consume-medicine", ActionType.CONSUME_RESOURCE, 1),
            ("gh-v1:acquire-hidden-cache", ActionType.ACQUIRE_RESOURCE, 4),
            ("gh-v1:complete-triage", ActionType.HELP_CHARACTER, 6),
        ),
        "char-zhou-qiming": (
            ("gh-v1:queue-checkpoint", ActionType.QUEUE_FOR_SERVICE, 3),
            ("gh-v1:route-clinic", ActionType.ATTEMPT_ROUTE, 6),
            ("gh-v1:allocate-rescue-seats", ActionType.QUEUE_FOR_SERVICE, 7),
        ),
        "char-chen-mo": (
            ("gh-v1:transfer-food", ActionType.TRANSFER_RESOURCE, 2),
            ("gh-v1:help-luo", ActionType.HELP_CHARACTER, 5),
            ("gh-v1:abandon-store-plan", ActionType.ABANDON_PLAN, 6),
        ),
    }
    return [
        ScenarioAffordance(id=identifier, action_type=action_type, available_day=day)
        for identifier, action_type, day in offered[agent_id]
        if day == state.current_day
    ]
