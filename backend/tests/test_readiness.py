from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class FakeSession:
    async def __aenter__(self) -> "FakeSession":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    async def execute(self, _query: object) -> None:
        return None


class FakeRedis:
    async def ping(self) -> bool:
        return True


def test_readiness_when_dependencies_are_available() -> None:
    app = create_app(Settings())

    @asynccontextmanager
    async def fake_lifespan(_app: object) -> AsyncIterator[None]:
        app.state.database = SimpleNamespace(session_factory=FakeSession)
        app.state.redis = FakeRedis()
        yield

    app.router.lifespan_context = fake_lifespan
    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {"database": "ok", "redis": "ok"},
    }
