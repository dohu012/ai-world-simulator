"""Owner-derived and observer-safe TASK-020 memory APIs."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from app.api.demo_access import require_demo_agent_id
from app.application.memory_evaluation import (
    MemoryEvaluationReport,
    run_fixed_evaluation,
)
from app.application.memory_service import (
    ConsolidationRead,
    MemoryApplicationService,
    MemoryRead,
    MemorySyncRead,
    RetrievalRead,
)

router = APIRouter(prefix="/demo/worlds/gray-harbor", tags=["memory"])


class RetrievalQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(default="", max_length=2000)
    cutoff: datetime
    final_k: int = Field(default=6, ge=1, le=12)


class EmbeddingWorkRead(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    completed: int


def service(request: Request) -> MemoryApplicationService:
    return MemoryApplicationService(request.app.state.database.session_factory)


@router.post("/memory/sync", response_model=MemorySyncRead)
async def sync_memory(request: Request) -> MemorySyncRead:
    """Internal fixed-world projection; owners and content remain server-derived."""
    return await service(request).sync_observations()


@router.post("/memory/embedding-work", response_model=EmbeddingWorkRead)
async def process_embedding_work(request: Request) -> EmbeddingWorkRead:
    completed = await service(request).process_embedding_jobs(worker_id="api-memory-worker")
    return EmbeddingWorkRead(completed=completed)


@router.get("/memory/evaluation", response_model=MemoryEvaluationReport)
async def memory_evaluation() -> MemoryEvaluationReport:
    """Run the versioned corpus through production hybrid and fallback policies."""
    return run_fixed_evaluation()


@router.get("/me/memories", response_model=list[MemoryRead])
async def own_memories(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> list[MemoryRead]:
    return await service(request).memories(agent_id)


@router.post("/me/memory-consolidation", response_model=ConsolidationRead)
async def consolidate_own_memory(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> ConsolidationRead:
    return await service(request).consolidate_stage(agent_id)


@router.get("/me/memory-retrieval", response_model=RetrievalRead)
async def own_retrieval(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
    cutoff: Annotated[datetime, Query()],
    query: Annotated[str, Query(max_length=2000)] = "",
    final_k: Annotated[int, Query(ge=1, le=12)] = 6,
) -> RetrievalRead:
    return await service(request).retrieve_for_owner(
        agent_id, query=query, cutoff=cutoff, final_k=final_k
    )


@router.get("/me/memory-retrieval/latest", response_model=RetrievalRead | None)
async def latest_own_retrieval(
    request: Request,
    agent_id: Annotated[str, Depends(require_demo_agent_id)],
) -> RetrievalRead | None:
    return await service(request).latest_retrieval(agent_id)
