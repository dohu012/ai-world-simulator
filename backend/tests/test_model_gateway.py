import json

import pytest
from pydantic import ValidationError

from app.model_gateway.adapters import DisabledModelGateway, ScriptedModelGateway
from app.model_gateway.contracts import AgentDecisionProposal, ModelRequest


def request() -> ModelRequest:
    return ModelRequest(
        task="test",
        prompt=json.dumps(
            {
                "affordances": [{"id": "wait", "action": "wait"}],
                "observation_ids": ["obs-1"],
                "observation_watermark": "a" * 64,
            }
        ),
        output_schema=AgentDecisionProposal.model_json_schema(),
        timeout_seconds=1.0,
        max_output_tokens=100,
        correlation_id="decision-test",
    )


async def test_fake_captures_request_and_returns_strict_offered_proposal() -> None:
    gateway = ScriptedModelGateway()
    outcome = await gateway.complete(request())
    proposal = AgentDecisionProposal.model_validate(outcome.output)
    assert proposal.action == "wait"
    assert proposal.observation_ids == ["obs-1"]
    assert gateway.requests[0].correlation_id == "decision-test"


async def test_disabled_gateway_is_typed_and_creates_no_fallback() -> None:
    outcome = await DisabledModelGateway().complete(request())
    assert outcome.failure_code == "MODEL_PROVIDER_DISABLED"
    assert outcome.output is None


@pytest.mark.parametrize(
    "extra", [{"seek_oracle": True}, {"action": "combat"}, {"observation_watermark": "short"}]
)
def test_proposal_rejects_extra_unsupported_and_wrong_watermark(extra: dict[str, object]) -> None:
    value = {
        "action": "wait",
        "affordance_id": "wait",
        "rationale_summary": "Wait safely.",
        "observation_ids": ["obs-1"],
        "observation_watermark": "a" * 64,
    }
    value.update(extra)
    with pytest.raises(ValidationError):
        AgentDecisionProposal.model_validate(value)


class FakeHTTPResponse:
    def __init__(self, payload: dict[str, object], status: int = 200) -> None:
        import io

        self.status = status
        self.headers = {"x-request-id": "req-test"}
        self._body = io.BytesIO(json.dumps(payload).encode())

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, amount: int = -1) -> bytes:
        return self._body.read(amount)


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"status": "incomplete", "output_text": None}, "MODEL_OUTPUT_INCOMPLETE"),
        ({"status": "completed", "output": [{"content": [{"type": "refusal"}]}]}, "MODEL_REFUSED"),
    ],
)
async def test_openai_adapter_maps_incomplete_and_refusal(monkeypatch, payload, expected) -> None:
    from app.model_gateway import adapters

    monkeypatch.setattr(
        adapters.urllib_request, "urlopen", lambda *_args, **_kwargs: FakeHTTPResponse(payload)
    )
    gateway = adapters.OpenAIResponsesGateway(
        api_key="secret", base_url="https://example.test", model="test-model"
    )
    outcome = await gateway.complete(request())
    assert outcome.failure_code == expected


async def test_openai_adapter_maps_rate_limit(monkeypatch) -> None:
    from urllib import error

    from app.model_gateway import adapters

    def limited(*_args, **_kwargs):
        raise error.HTTPError(
            "https://example.test", 429, "limited", {"x-request-id": "req-rate"}, None
        )

    monkeypatch.setattr(adapters.urllib_request, "urlopen", limited)
    outcome = await adapters.OpenAIResponsesGateway(
        api_key="secret", base_url="https://example.test", model="test-model"
    ).complete(request())
    assert outcome.failure_code == "MODEL_RATE_LIMITED"


async def test_openai_adapter_maps_timeout(monkeypatch) -> None:
    from app.model_gateway import adapters

    async def timeout(*_args, **_kwargs):
        raise TimeoutError

    monkeypatch.setattr(adapters.asyncio, "to_thread", timeout)
    outcome = await adapters.OpenAIResponsesGateway(
        api_key="secret", base_url="https://example.test", model="test-model"
    ).complete(request())
    assert outcome.failure_code == "MODEL_TIMEOUT"


@pytest.mark.parametrize(
    "raised",
    [
        __import__("ssl").SSLEOFError("EOF occurred in violation of protocol"),
        __import__("urllib.error", fromlist=["error"]).URLError("connection refused"),
        ValueError("not json"),
    ],
)
async def test_openai_adapter_maps_network_and_body_failures(monkeypatch, raised) -> None:
    from app.model_gateway import adapters

    def broken(*_args, **_kwargs):
        raise raised

    monkeypatch.setattr(adapters.urllib_request, "urlopen", broken)
    outcome = await adapters.OpenAIResponsesGateway(
        api_key="secret", base_url="https://example.test", model="test-model"
    ).complete(request())
    assert outcome.failure_code == "MODEL_PROVIDER_UNAVAILABLE"


async def test_openai_adapter_parses_nested_output_text_from_raw_rest_shape(monkeypatch) -> None:
    from app.model_gateway import adapters

    proposal = {
        "action": "wait",
        "affordance_id": "wait",
        "rationale_summary": "Wait safely.",
        "observation_ids": ["obs-1"],
        "observation_watermark": "a" * 64,
    }
    payload = {
        "id": "resp-1",
        "object": "response",
        "model": "test-model",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(proposal)}],
            }
        ],
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }
    monkeypatch.setattr(
        adapters.urllib_request, "urlopen", lambda *_args, **_kwargs: FakeHTTPResponse(payload)
    )
    outcome = await adapters.OpenAIResponsesGateway(
        api_key="secret", base_url="https://example.test", model="test-model"
    ).complete(request())
    assert outcome.failure_code is None
    assert outcome.output == proposal
    assert outcome.input_tokens == 10
