import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

from app.core.config import Settings
from app.infrastructure.database.session import Database
from app.infrastructure.redis.client import create_redis_client

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INFRA_TESTS") != "1",
    reason="set RUN_INFRA_TESTS=1 with PostgreSQL and Redis running",
)


async def test_database_session_can_be_created() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            assert await session.scalar(text("SELECT 1")) == 1
    finally:
        await database.dispose()


async def test_redis_ping() -> None:
    client = create_redis_client(Settings().redis_url)
    try:
        assert await client.ping() is True
    finally:
        await client.aclose()


def test_alembic_upgrade_head() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).parents[1],
        check=False,
    )
    assert result.returncode == 0
