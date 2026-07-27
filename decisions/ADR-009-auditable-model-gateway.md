# ADR-009: Auditable model gateway and explicit decision orchestration

- Status: Accepted
- Date: 2026-07-26

## Decision

Use a small internal `ModelGateway` port, a deterministic scripted fake, and one direct-HTTP OpenAI Responses adapter. PostgreSQL decision/attempt records are authoritative. Provider-native strict JSON Schema is requested, but local Pydantic validation and a server-derived affordance allowlist are the final enforcement boundary. No Agent framework, automatic tool execution, provider SDK, repair loop, telemetry backend, or live evaluation dependency is introduced.

## Dated comparison

| Option | Release/docs checked | License/dependency/operations | Result |
| --- | --- | --- | --- |
| OpenAI SDK / Responses | Official API docs, 2026-07-26 | SDK is Apache-2.0; Responses supplies strict JSON Schema, request IDs, incomplete status and usage. SDK adds a provider dependency. | Responses selected, direct HTTP keeps imports and removal cost minimal. |
| Anthropic SDK/tools | Official docs, 2026-07-26 | MIT SDK; strict tool schemas are capable but use a tool-call envelope and different refusal/usage mapping. | Rejected for the first adapter; port permits later addition. |
| LiteLLM | Project docs/repository, 2026-07-26 | MIT; broad routing/retry/logging surface and material dependency weight. | Rejected until multiple providers justify a proxy. |
| PydanticAI / Instructor | Project docs/repositories, 2026-07-26 | MIT; useful structured-output helpers, but duplicate a small local validation boundary and can add repair behavior. | Rejected; plain Pydantic is already installed. |
| LangGraph/LangChain | Project docs/repositories, 2026-07-26 | MIT; graphs, checkpoints and tool orchestration overlap future scheduler concerns. | Rejected for a single explicit call/action workflow. |
| PostgreSQL audit | Existing architecture | Transactional, queryable and co-located with causal action records. | Selected as replay authority. |
| OTel/Langfuse/Phoenix | Official/project docs, 2026-07-26 | Optional diagnostics; GenAI conventions remain evolving and content capture can leak prompts. | Deferred; any future exporter is non-authoritative and content-off by default. |
| pytest / live eval tools | Existing pytest vs Promptfoo/DeepEval projects | Deterministic fixtures are free and CI-safe; live evals cost money and vary. | pytest gates CI; live evaluation remains opt-in and budget-capped. |

Official OpenAI documentation records strict JSON Schema support, incomplete states, usage, request IDs and recommends pinned model snapshots: https://platform.openai.com/docs/api-reference/responses and https://platform.openai.com/docs/api-reference/backward-compatibility . OpenTelemetry documents that GenAI conventions/content fields are evolving and prompt content is opt-in: https://opentelemetry.io/docs/specs/semconv/gen-ai/ .

## Spike evidence

The deterministic adapter captures the exact provider-neutral request and returns scripted success/failure outcomes. The OpenAI adapter is isolated in `app/model_gateway/adapters.py`, sends `store=false`, a pinned model, strict schema, bounded output and client request ID, and maps timeout, 429, 5xx, incomplete and invalid JSON to stable codes. It is never enabled without explicit mode plus a secret.

## Privacy and recovery consequences

The prompt is canonical JSON made only from the current character/profile, owner-filtered persisted Observations and server affordances. Hashes and privacy-safe input references are durable; credentials, headers, raw reasoning and unrelated state are not. Each claim, attempt, provider call, action and finalization uses a separate transaction/session, so inference holds no DB/world lock. Completed same-key decisions replay without another provider call or action submission. A claimed non-terminal record returns `DECISION_IN_PROGRESS`; lease fields reserve atomic takeover work for follow-up hardening.

## Migration/removal cost

The HTTP adapter can be removed without changing application/domain contracts. Removing the feature requires dropping migration 0004 tables and the decision route/panel; existing action and replay contracts remain intact.
