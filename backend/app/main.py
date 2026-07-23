from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.middleware import request_logging_middleware
from app.infrastructure.database.session import Database
from app.infrastructure.redis.client import create_redis_client


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an application with lifespan-owned infrastructure clients."""
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.database = Database(app_settings.database_url)
        app.state.redis = create_redis_client(app_settings.redis_url)
        yield
        await app.state.redis.aclose()
        await app.state.database.dispose()

    app = FastAPI(title="AI World Simulator API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)
    app.include_router(health_router)
    register_exception_handlers(app)
    return app


app = create_app()
