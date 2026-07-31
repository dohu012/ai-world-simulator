"""Owner-scoped identity, directional relationship, and reflection APIs."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.demo_access import require_demo_agent_id
from app.application.evolution_evaluation import (
    EvolutionEvaluationReport,
    run_evolution_evaluation,
)
from app.application.evolution_service import (
    EvolutionApplicationService,
    EvolutionStateRead,
    ReflectionRead,
)

router = APIRouter(prefix="/demo/worlds/gray-harbor", tags=["evolution"])


def service(request: Request) -> EvolutionApplicationService:
    return EvolutionApplicationService(request.app.state.database.session_factory)


@router.get("/me/evolution", response_model=EvolutionStateRead)
async def own_evolution(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> EvolutionStateRead:
    return await service(request).state(agent_id)


@router.post("/me/reflections", response_model=ReflectionRead)
async def reflect(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> ReflectionRead:
    return await service(request).reflect(agent_id)


@router.get("/evolution/evaluation", response_model=EvolutionEvaluationReport)
async def evaluation() -> EvolutionEvaluationReport:
    return run_evolution_evaluation()
