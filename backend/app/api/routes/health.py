from typing import Literal

from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from sqlalchemy import text

from app.api.errors import ApiError

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


class DependencyStatus(BaseModel):
    database: Literal["ok"]
    redis: Literal["ok"]


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    dependencies: DependencyStatus


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Report whether the HTTP process is alive."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness(request: Request) -> ReadinessResponse:
    """Check database and Redis connectivity without modifying data."""
    failures: list[str] = []
    try:
        async with request.app.state.database.session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        failures.append("database")

    try:
        if not await request.app.state.redis.ping():
            failures.append("redis")
    except Exception:
        failures.append("redis")

    if failures:
        raise ApiError(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "DEPENDENCY_UNAVAILABLE",
            "One or more dependencies are unavailable",
            {"unavailable": failures},
        )

    return ReadinessResponse(
        status="ready",
        dependencies=DependencyStatus(database="ok", redis="ok"),
    )
