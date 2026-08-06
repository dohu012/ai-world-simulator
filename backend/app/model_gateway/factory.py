"""Settings-driven model gateway selection."""

from app.core.config import Settings
from app.model_gateway.adapters import (
    DisabledModelGateway,
    OpenAIResponsesGateway,
    ScriptedModelGateway,
)
from app.model_gateway.contracts import ModelGateway


def build_model_gateway(settings: Settings) -> ModelGateway:
    """Resolve the configured provider; anything unconfigured degrades to disabled."""
    if settings.model_provider == "fake":
        return ScriptedModelGateway()
    if settings.model_provider == "openai" and settings.model_api_key:
        return OpenAIResponsesGateway(
            api_key=settings.model_api_key,
            base_url=settings.model_base_url,
            model=settings.model_id,
        )
    return DisabledModelGateway()
