"""Deterministic and OpenAI Responses API gateway adapters."""

import asyncio
import json
from collections import deque
from time import monotonic
from urllib import error
from urllib import request as urllib_request

from app.model_gateway.contracts import ModelOutcome, ModelRequest


class DisabledModelGateway:
    async def complete(self, request: ModelRequest) -> ModelOutcome:
        return ModelOutcome(
            provider="disabled",
            model="disabled",
            failure_code="MODEL_PROVIDER_DISABLED",
            latency_ms=0,
        )


class ScriptedModelGateway:
    def __init__(self, outcomes: list[ModelOutcome] | None = None) -> None:
        self.outcomes = deque(outcomes or [])
        self.requests: list[ModelRequest] = []

    async def complete(self, request: ModelRequest) -> ModelOutcome:
        self.requests.append(request)
        if self.outcomes:
            return self.outcomes.popleft()
        payload = json.loads(request.prompt)
        affordance = payload["affordances"][0]
        return ModelOutcome(
            provider="fake",
            model="deterministic-v1",
            finish_reason="completed",
            output={
                "action": affordance["action"],
                "affordance_id": affordance["id"],
                "rationale_summary": "Selected one server-offered safe action.",
                "observation_ids": payload["observation_ids"],
                "observation_watermark": payload["observation_watermark"],
            },
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
        )


class OpenAIResponsesGateway:
    def __init__(self, *, api_key: str, base_url: str, model: str) -> None:
        self.api_key, self.base_url, self.model = api_key, base_url.rstrip("/"), model

    async def complete(self, request: ModelRequest) -> ModelOutcome:
        started = monotonic()
        # text.format enforces the schema server-side on openai.com, but relay
        # endpoints commonly ignore it — restate the schema in instructions so the
        # model still emits conforming JSON when enforcement is absent.
        schema_directive = (
            "Output a single JSON object conforming to this JSON Schema, with all "
            "required fields and no markdown fences:\n"
            + json.dumps(request.output_schema, sort_keys=True, separators=(",", ":"))
        )
        instructions = (
            f"{request.instructions}\n\n{schema_directive}"
            if request.instructions is not None
            else schema_directive
        )
        body = {
            "model": self.model,
            "input": request.prompt,
            "instructions": instructions,
            "max_output_tokens": request.max_output_tokens,
            "store": False,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "agent_decision",
                    "strict": True,
                    "schema": request.output_schema,
                }
            },
        }

        def send() -> tuple[int, dict[str, object], str | None]:
            req = urllib_request.Request(
                f"{self.base_url}/v1/responses",
                data=json.dumps(body).encode(),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Client-Request-Id": request.correlation_id,
                },
                method="POST",
            )
            try:
                with urllib_request.urlopen(req, timeout=request.timeout_seconds) as response:
                    return (
                        response.status,
                        json.load(response),
                        response.headers.get("x-request-id"),
                    )
            except error.HTTPError as exc:
                return exc.code, {}, exc.headers.get("x-request-id")
            except OSError:
                # DNS, TLS, and connection-reset failures never reach HTTP status handling;
                # map them to a synthetic 599 so they surface as MODEL_PROVIDER_UNAVAILABLE.
                return 599, {}, None
            except ValueError:
                # Non-JSON body (proxy error pages, truncated responses).
                return 599, {}, None

        try:
            status, data, request_id = await asyncio.wait_for(
                asyncio.to_thread(send), timeout=request.timeout_seconds + 0.5
            )
        except TimeoutError:
            return ModelOutcome(
                provider="openai",
                model=self.model,
                failure_code="MODEL_TIMEOUT",
                latency_ms=int((monotonic() - started) * 1000),
            )
        failure = (
            "MODEL_RATE_LIMITED"
            if status == 429
            else "MODEL_PROVIDER_UNAVAILABLE"
            if status >= 400
            else None
        )
        if data.get("status") == "incomplete":
            failure = "MODEL_OUTPUT_INCOMPLETE"
        output_items = data.get("output")
        output_text = data.get("output_text")
        if isinstance(output_items, list):
            fragments: list[str] = []
            for item in output_items:
                if not isinstance(item, dict):
                    continue
                content_items = item.get("content")
                if not isinstance(content_items, list):
                    continue
                for content in content_items:
                    if not isinstance(content, dict):
                        continue
                    if content.get("type") == "refusal":
                        failure = "MODEL_REFUSED"
                    elif content.get("type") == "output_text":
                        fragments.append(str(content.get("text", "")))
            # Raw REST responses carry text only inside output[].content[]; the
            # top-level output_text convenience field is not part of the wire format.
            if not isinstance(output_text, str) and fragments:
                output_text = "".join(fragments)
        output = None
        if isinstance(output_text, str):
            # Some relays skip server-side json_schema enforcement and return the
            # model's raw text, which is often wrapped in markdown code fences.
            text = output_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else ""
                text = text.rsplit("```", 1)[0]
            try:
                output = json.loads(text)
            except json.JSONDecodeError:
                failure = "MODEL_OUTPUT_INVALID"
        if status < 400 and failure is None and output is None:
            failure = "MODEL_OUTPUT_INVALID"
        usage_value = data.get("usage")
        usage: dict[str, object] = usage_value if isinstance(usage_value, dict) else {}
        response_id = data.get("id")
        return ModelOutcome.model_validate(
            {
                "provider": "openai",
                "model": str(data.get("model", self.model)),
                "provider_request_id": request_id or (str(response_id) if response_id else None),
                "finish_reason": str(data.get("status")),
                "output": output,
                "failure_code": failure,
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "latency_ms": int((monotonic() - started) * 1000),
            }
        )
