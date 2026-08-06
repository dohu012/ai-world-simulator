"""Factory selection, instructions passthrough, and runtime gateway injection."""

import json

from app.application.runtime_service import PostgresWorldRuntimeAdapter
from app.core.config import Settings
from app.model_gateway import adapters
from app.model_gateway.adapters import (
    DisabledModelGateway,
    OpenAIResponsesGateway,
    ScriptedModelGateway,
)
from app.model_gateway.contracts import AgentDecisionProposal, ModelRequest
from app.model_gateway.factory import build_model_gateway


def settings_for(provider: str, api_key: str | None = None) -> Settings:
    return Settings(
        model_provider=provider,
        model_api_key=api_key,
        model_base_url="https://example.test",
        model_id="test-model",
    )


def test_factory_returns_scripted_for_fake_provider() -> None:
    assert isinstance(build_model_gateway(settings_for("fake")), ScriptedModelGateway)


def test_factory_returns_openai_with_configured_settings() -> None:
    gateway = build_model_gateway(settings_for("openai", api_key="secret"))
    assert isinstance(gateway, OpenAIResponsesGateway)
    assert gateway.base_url == "https://example.test"
    assert gateway.model == "test-model"


def test_factory_degrades_to_disabled_without_api_key_or_provider() -> None:
    assert isinstance(build_model_gateway(settings_for("openai")), DisabledModelGateway)
    assert isinstance(build_model_gateway(settings_for("disabled")), DisabledModelGateway)


def test_runtime_adapter_defaults_to_scripted_and_keeps_injected_gateway() -> None:
    sessions = object()
    fallback = PostgresWorldRuntimeAdapter(sessions, enabled=True)
    assert isinstance(fallback.gateway, ScriptedModelGateway)
    injected = DisabledModelGateway()
    adapter = PostgresWorldRuntimeAdapter(
        sessions,
        enabled=True,
        gateway=injected,
        model_max_attempts=3,
        model_timeout_seconds=7.0,
        model_max_output_tokens=200,
    )
    assert adapter.gateway is injected
    assert (adapter.model_max_attempts, adapter.model_timeout_seconds) == (3, 7.0)
    assert adapter.model_max_output_tokens == 200


def request_with(instructions: str | None) -> ModelRequest:
    return ModelRequest(
        task="test",
        prompt=json.dumps(
            {
                "affordances": [{"id": "wait", "action": "wait"}],
                "observation_ids": ["obs-1"],
                "observation_watermark": "a" * 64,
            }
        ),
        instructions=instructions,
        output_schema=AgentDecisionProposal.model_json_schema(),
        timeout_seconds=1.0,
        max_output_tokens=100,
        correlation_id="decision-test",
    )


async def test_openai_adapter_sends_instructions_in_body(monkeypatch) -> None:
    captured: list[bytes] = []

    def capture(req, timeout):
        captured.append(req.data)
        raise TimeoutError

    monkeypatch.setattr(adapters.urllib_request, "urlopen", capture)
    gateway = OpenAIResponsesGateway(
        api_key="secret", base_url="https://example.test", model="test-model"
    )
    await gateway.complete(request_with("You are Chen Mo."))
    body = json.loads(captured[0])
    assert body["instructions"].startswith("You are Chen Mo.")
    assert "JSON Schema" in body["instructions"]
    captured.clear()
    await gateway.complete(request_with(None))
    body = json.loads(captured[0])
    assert "You are Chen Mo." not in body["instructions"]
    assert "JSON Schema" in body["instructions"]


async def test_scripted_gateway_ignores_instructions_and_still_parses_prompt() -> None:
    gateway = ScriptedModelGateway()
    outcome = await gateway.complete(request_with("You are Chen Mo."))
    proposal = AgentDecisionProposal.model_validate(outcome.output)
    assert proposal.affordance_id == "wait"
    assert gateway.requests[0].instructions == "You are Chen Mo."
