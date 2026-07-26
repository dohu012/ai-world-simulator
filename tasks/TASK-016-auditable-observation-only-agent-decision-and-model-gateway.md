# TASK-016: Auditable Observation-Only Agent Decision and Model Gateway Vertical Slice

**Status:** Planned  
**Planning date:** 2026-07-26  
**Depends on:** TASK-001 through TASK-015  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf` (41 pages)

## 1. Planning Basis

The product plan defines an AI-world simulator in which Agents make autonomous decisions from limited local knowledge, while deterministic application code owns permissions, world state, action results, and causal propagation. The first technical milestone requires a fixed world with three distinct Agents, differentiated information propagation, optional Oracle interaction, independent Agent decisions, authoritative world adjudication, and an observer-visible thought/action/dialogue trajectory.

TASK-015 completed the prerequisite authoritative mutation path: a current Agent can submit concurrency-safe `wait` and `move` intents through Validator, World Engine, atomic PostgreSQL persistence, runtime Observation propagation, and replay. The largest remaining gap in the core product loop is therefore not another hand-authored action. It is a safe, auditable bridge from an Agent's Observation-only input to one of those existing authoritative actions.

This task plans that bridge as a deliberately constrained vertical slice. It does not attempt general autonomous scheduling, unrestricted tool use, long-term memory, or a broad action catalogue.

## 2. Why This Is the Next Critical Task

| Candidate | Why not next |
| --- | --- |
| More action types | Expands mechanics but still does not validate autonomous AI characters. |
| Oracle automation | Depends on reliable decision classification and model-call auditability. |
| Scheduler / Temporal / Celery | Automates a loop that has not yet been proven safe or useful. |
| Long-term memory / vector retrieval | Adds retrieval complexity before the minimal local-knowledge decision loop exists. |
| World creator / editor | Improves content authoring, not the product's central autonomy claim. |
| Observation-only Agent decision | Connects the completed perception and authority paths and directly tests the product thesis. |

TASK-016 must prove, end to end, that an Agent can:

1. receive only its permitted Observations and its own state;
2. propose a strictly constrained decision through a provider-neutral Model Gateway;
3. have the server validate and translate that proposal into an existing `wait` or `move` ActionIntent;
4. let the existing Validator and World Engine accept or reject the action;
5. expose a complete, privacy-safe causal replay from input through model call to world result.

## 3. One-Sentence Acceptance Target

From the Gray Harbor demo UI or API, trigger one decision for Chen and obtain either a safely rejected, fully audited model attempt or exactly one idempotent `wait`/`move` action whose Observation watermark, prompt version, structured output, model metadata, ActionResult, event, resulting state version, and recipient Observations can be replayed without exposing any other Agent's private data or hidden global truth.

## 4. Required Preliminary Open-Source Research

Implementation must not begin with a library choice already assumed. First add a dated decision note comparing current releases and official documentation. Record version/date, license, maintenance activity, dependency weight, security/privacy implications, capability gaps, and a minimal spike result.

### 4.1 Provider and transport strategy

Compare:

- official OpenAI Python SDK and Responses structured outputs;
- official Anthropic SDK and strict tool/JSON-schema output;
- direct `httpx` adapters;
- LiteLLM proxy/library;
- a deterministic in-process fake provider.

Evaluate async cancellation, timeout behavior, strict structured output, refusal/incomplete responses, request IDs, token usage, retries, fallbacks, pinned model identifiers, logging defaults, retention controls, and dependency footprint.

### 4.2 Structured decision enforcement

Compare:

- provider-native strict JSON Schema;
- forced strict tool calls used only as an output envelope;
- local Pydantic validation;
- PydanticAI structured output;
- Instructor or an equivalent maintained helper.

Test unsupported JSON Schema features, truncation, refusal, extra fields, invalid enum values, repair/retry behavior, and whether validation can remain provider-neutral.

### 4.3 Orchestration boundary

Compare a small explicit Application service with PydanticAI and LangGraph/LangChain. Determine whether a framework introduces automatic tool execution, hidden state, checkpoints, persistence, retry behavior, or abstractions that duplicate the future scheduler. The default expectation is a small internal Gateway and explicit orchestration, but the research must justify the conclusion.

### 4.4 Observability and evaluation

Compare:

- authoritative PostgreSQL audit tables;
- OpenTelemetry GenAI semantic conventions;
- Langfuse and Arize Phoenix for optional diagnostics;
- pytest fixtures versus Promptfoo/DeepEval-style opt-in live evaluations.

PostgreSQL must remain the authoritative replay source. Any telemetry integration must be optional, privacy-filtered, non-authoritative, and tolerant of evolving GenAI conventions. Live-provider evaluation must be opt-in, budget-capped, and excluded from normal CI.

### 4.5 Required research output

Create an ADR or decision note that includes:

- a capability matrix and rejected alternatives;
- a minimal adapter spike with mocked responses;
- the selected real-provider adapter and deterministic fake;
- the no-new-library option;
- migration and removal costs;
- secret, prompt, and telemetry handling;
- exact reasons a full Agent framework is or is not adopted.

If the selected approach materially changes ADR-006 or the authority boundaries, update the ADR before production code.

## 5. Scope and Demo Scenario

The primary demo uses Chen in Gray Harbor:

- Input contains Chen's own persisted state and only persisted Observations currently permitted to Chen.
- Server-derived affordances contain `wait` and valid adjacent `move` destinations only.
- The model may choose exactly one offered affordance.
- A deterministic fake is the default for tests and local repeatability.
- One real provider adapter is supported only when explicitly configured.
- Fixtures cover valid move, valid wait, malformed output, refusal, timeout, transient failure, invented destination, stale state after inference, and attempted hidden-fact leakage.

The task is complete only when both successful and unsuccessful attempts are causally inspectable.

## 6. Target Architecture

```text
POST /demo/worlds/gray-harbor/me/decisions
  -> AgentDecisionApplicationService
     -> current-agent input / Observation query
     -> server-derived affordance builder
     -> versioned prompt builder
     -> ModelGateway port
        -> deterministic fake OR one selected provider adapter
     -> strict decision validator + allowlist check
     -> server-derived wait/move ActionIntent
     -> existing GrayHarborActionService
        -> Validator -> World Engine -> Repository
     -> decision/action/replay projection
```

Hard boundaries:

- Provider SDK imports exist only inside Model Gateway adapters.
- The Gateway cannot access repositories, sessions, world entities, or mutate state.
- No database transaction or world lock remains open during an external model request.
- A model output is a proposal, never an action result or state mutation.
- Current state and versions are revalidated by the existing authoritative action path.
- Redis, telemetry, or provider logs cannot become the replay authority.

## 7. Observation-Only Decision Input

Define an internal, serializable `AgentDecisionInput` containing only:

- world ID, world time, and observed world/state version;
- the current Agent's identity, stable profile/persona fields, and own mutable state;
- deterministically ordered persisted Observations owned by that Agent;
- an Observation watermark and included Observation IDs;
- server-derived action affordances;
- prompt version, output-schema version, and input-contract version.

Explicitly exclude:

- global facts or an objective truth table;
- all characters or all world events;
- other Agents' private observations, memories, beliefs, goals, or Oracle exchanges;
- unpropagated and future events;
- observer/admin projections;
- ORM entities and repository handles.

Affordances must be concrete and server owned. For this slice they are:

- `wait` with no model-controlled authoritative fields;
- `move` with only currently adjacent destination IDs and expected state versions.

The model cannot invent actor IDs, idempotency keys, source locations, character versions, world versions, witnesses, recipients, success flags, events, or results.

If the current Observation schema cannot support this contract without weakening isolation, document and update ADR-002 before changing it.

## 8. Strict Structured Decision Contract

Define a versioned Pydantic/domain contract that includes:

- echoed input watermark;
- `observations_considered`, restricted to supplied Observation IDs;
- bounded candidate actions with short rationale summaries;
- exactly one selected action matching an offered affordance;
- `major_decision`;
- `seek_oracle`, fixed to `false` in TASK-016;
- a bounded `private_thought_summary` intended for product display.

Validation rules:

- reject unknown or extra fields;
- reject unknown Observation IDs and mismatched watermarks;
- reject actions or destinations outside the offered affordances;
- accept only `wait` or `move`;
- reject model-proposed success, result, event, version, state mutation, witnesses, or recipients;
- do not request, store, or expose hidden chain-of-thought;
- enforce length and collection limits before persistence and UI rendering;
- derive the final ActionIntent entirely on the server.

Provider-native schema enforcement is defense in depth; local validation is always mandatory.

## 9. Prompt Versioning and Privacy

Seed an immutable `gray-harbor-agent-decision-v1` prompt version. Persist:

- logical version and content hash;
- output-schema version and schema hash;
- selected model configuration;
- effective system/developer/user message representation after redaction.

Prompt composition must be deterministic:

1. decision protocol and authority rules;
2. known world rules, not hidden world truth;
3. Agent persona and own state;
4. owned Observations in deterministic order;
5. server-derived affordances;
6. strict output contract.

Prompt text is not an authorization boundary. Snapshot and leakage tests must prove that decoy secrets, other Agents' private records, raw Oracle lifecycle data, observer-only state, and unrelated events are absent. Prompt injection inside an Observation must not widen the action allowlist.

## 10. Model Gateway Contract

Define an async provider-neutral port similar to:

```python
generate_structured(request: ModelRequest[T]) -> ModelResponse[T]
```

The request includes messages, strict output schema, task name, model tier/configuration, timeout, maximum output size, and correlation metadata. The response distinguishes:

- validated structured output;
- provider refusal;
- incomplete/truncated output;
- typed provider or transport failure.

It also returns provider/model identifiers, provider request ID where available, finish reason, token/usage data, latency, and attempt information.

Required adapters:

- deterministic scripted fake supporting success, invalid output, refusal, timeout, rate limit, transient unavailable, and incomplete output;
- one real provider adapter chosen by the research;
- disabled mode that starts safely without credentials.

Retry policy:

- bounded attempts;
- retry only classified transient failures;
- at most one explicitly recorded structured-output repair if research justifies it;
- never retry after a locally valid response;
- never duplicate action submission;
- record fallback/provider switching;
- cancellation produces no action.

## 11. Durable Decision Claim and Idempotency

External model calls cannot hold a database lock. Implement a durable lifecycle such as:

```text
requested -> claimed -> model_completed|model_failed
          -> validated|rejected
          -> action_submitted -> completed
```

Requirements:

- derive a stable decision ID from world, Agent, and client idempotency key;
- enforce one decision/action link per key with database constraints;
- same-key concurrent requests return the completed chain or `DECISION_IN_PROGRESS`;
- use a bounded lease/claim with explicit recovery semantics;
- test lease expiry/takeover atomically without timing sleeps;
- persist each model attempt before/after the call without holding world locks;
- after a crash following model completion, resume without calling the model again;
- after a crash following action submission, resolve the existing action lifecycle rather than resubmitting;
- after inference, submit through the current authoritative action path with current validation;
- stale state produces an auditable action rejection and does not silently re-prompt.

“First completed response wins” or another concurrency rule must be documented precisely and enforced in PostgreSQL.

## 12. Persistence and Audit

Add one reversible migration for appropriately normalized tables, expected to cover:

- immutable prompt versions;
- Agent decision requests/runs;
- model calls and individual attempts;
- the decision-to-action causal link.

Persist at minimum:

- world, Agent, decision, and idempotency identifiers;
- lifecycle status, claim owner, lease timestamps, and recovery metadata;
- input watermark and included Observation IDs;
- input, prompt, and schema version/hash;
- redacted/canonical prompt payload or a privacy-safe replay representation;
- provider, pinned model, provider request ID, timestamps, latency, finish reason;
- attempt number and typed failure;
- provider-reported token usage;
- cost only when calculated from versioned server-owned pricing data, otherwise `null`;
- validated structured decision;
- linked ActionIntent/ActionResult/event IDs and resulting versions.

Do not persist credentials, authorization headers, provider-hidden reasoning, unrestricted raw chain-of-thought, or unredacted unrelated private data. JSONB payloads must be round-tripped through strict Pydantic/domain models. Add useful indexes and database constraints, not just application checks.

## 13. Application Workflow

Implement this explicit sequence:

1. Authenticate/resolve the fixed demo current Agent.
2. Normalize the client idempotency key and derive decision ID.
3. Return a completed replay when the same key already completed.
4. Atomically claim or recover the decision lifecycle.
5. Load the current Agent input through the existing isolation boundary.
6. Derive affordances and the Observation watermark on the server.
7. Resolve immutable prompt/schema versions and build the deterministic request.
8. Persist the attempt boundary and close the transaction.
9. Call the Gateway without a database/world lock.
10. Persist provider outcome and locally validate structured output.
11. Derive a deterministic action key and server-owned ActionIntent.
12. Submit through the existing action Application service.
13. Link the authoritative result and finalize the decision.
14. Return the privacy-safe causal projection.

No step may bypass TASK-014/TASK-015 validation, engine, idempotency, transaction, Observation propagation, or replay behavior.

## 14. Failure Semantics

Define stable codes including:

- `MODEL_PROVIDER_DISABLED`
- `MODEL_TIMEOUT`
- `MODEL_RATE_LIMITED`
- `MODEL_PROVIDER_UNAVAILABLE`
- `MODEL_REFUSED`
- `MODEL_OUTPUT_INCOMPLETE`
- `MODEL_OUTPUT_INVALID`
- `DECISION_OUTPUT_NOT_ALLOWED`
- `DECISION_IN_PROGRESS`
- `DECISION_CLAIM_CONFLICT`

Continue using existing version/precondition rejection codes for authoritative action failures.

Model failures must be audited but create no ActionIntent, ActionResult, world event, state mutation, or new runtime Observation. Action rejection remains an authoritative ActionResult, not a model failure. Do not silently convert failure into `wait`. Return JSON error bodies consistently so the frontend never attempts to parse plain-text 500 responses.

## 15. API Contract

Add:

```http
POST /demo/worlds/gray-harbor/me/decisions
X-Demo-Agent-Id: chen
Content-Type: application/json

{"idempotency_key": "..."}
```

Provider, model, prompt content, input records, action choices, versions, and actor identity remain server-owned. The response returns:

- decision lifecycle and idempotent replay status;
- input watermark and privacy-safe Observation references;
- prompt/schema versions and hashes;
- provider/model/attempt metadata;
- validated candidates and selected proposal;
- linked authoritative action lifecycle/result;
- causal event/state/Observation references when present.

Never return credentials, raw provider reasoning, unrestricted prompts, or hidden Agent/global data. Preserve all existing demo routes and callers.

## 16. Frontend and Replay Inspector

Add an **Agent Decision** panel to the fixed demo:

- manual “decide once” trigger;
- disabled, loading, in-progress, success, refusal, invalid, timeout, and stale-action states;
- prompt version, provider/model, attempts, latency, token usage, and nullable cost;
- bounded candidate/rationale summaries and selected proposal;
- authoritative result and resulting state changes displayed separately;
- exact same-key replay behavior.

Extend replay to show:

```text
Observation watermark
  -> prompt/schema version
  -> model call attempt(s)
  -> validated Agent decision
  -> ActionIntent
  -> ActionResult
  -> world event/state version
  -> recipient Observations
```

The UI must make “model proposal” versus “engine outcome” unmistakable. It must not provide a provider picker, API-key field, raw prompt editor, scheduler control, or hidden-data view.

## 17. Evaluation and Adversarial Fixtures

Create deterministic fixtures for:

- valid adjacent move;
- valid wait;
- invented/non-adjacent destination;
- unsupported action type;
- malformed JSON or extra fields;
- wrong watermark or unknown Observation ID;
- forbidden `seek_oracle=true`;
- refusal and incomplete response;
- one transient retry followed by success;
- all attempts failing;
- state becoming stale after inference;
- decoy global secret and another Agent's private Observation absent from input/prompt;
- Observation prompt injection attempting to add tools or destinations;
- overlong thought/rationale content;
- crash/recovery boundaries before and after action submission.

Measure at least schema-valid rate, allowlist-valid rate, executable proposal rate, leakage violations, authoritative acceptance/rejection, retry count, latency, usage/cost availability, and causal replay completeness. Deterministic fixtures gate CI; live-model evaluations are manual/opt-in and budget-capped.

## 18. Backend Tests

Add tests for:

- strict input/output models, hashes, and stable schema export;
- deterministic Observation ordering and watermarking;
- prompt snapshots and negative leakage assertions;
- fake adapter capture and all scripted outcomes;
- mocked real-adapter mapping without network access;
- error classification, timeout, cancellation, retry, repair, and fallback policy;
- output allowlist and server-owned ActionIntent derivation;
- accepted wait/move and stale authoritative rejection;
- zero actions/events/Observations on model failure;
- same-key replay, same-key concurrency, different-key concurrency;
- claim conflict, lease recovery, and crash-resume semantics;
- proof no database transaction/world lock spans provider latency;
- migration upgrade/downgrade, constraints, indexes, JSONB round-trip;
- replay isolation and privacy;
- import/boundary tests preventing SDK leakage and Gateway repository access;
- complete regression of TASK-001 through TASK-015.

Concurrency tests must use barriers or explicit hooks, not probabilistic sleeps.

## 19. Frontend Tests

Cover:

- request headers/body, same-origin behavior, and JSON error handling;
- disabled/loading/in-progress/failure/success states;
- candidate and selected proposal rendering;
- proposal/result visual separation;
- provider metadata, token usage, latency, and nullable cost;
- invalid output and stale action rejection;
- idempotent replay and causal chain rendering;
- no raw chain-of-thought, secret, private-record, API-key, or raw prompt leakage;
- regressions for health, observer, perspective, input feed, action controls, and replay.

## 20. Configuration and Operational Safety

Add documented server configuration for:

- provider mode: `disabled`, `fake`, or the selected real provider;
- API key via environment/secret injection only;
- optional base URL;
- pinned model ID;
- timeout, maximum attempts, and maximum output size;
- model tier/task mapping;
- optional versioned pricing table;
- live-evaluation enable flag and budget.

Update `.env.example` with placeholders only. The application must start with no key and report provider-disabled separately from backend/database health. Health/readiness checks must not perform paid model calls. Logs and telemetry must redact credentials and private prompt content by default.

## 21. Allowed Changes

- Model Gateway domain/application ports and selected adapters;
- Agent decision application/domain contracts;
- prompt versioning and seed data;
- repository models and one reversible migration;
- Gray Harbor decision API and replay projection;
- fixed demo frontend panel and replay UI;
- deterministic fixtures, tests, configuration, ADRs, and documentation.

## 22. Explicitly Out of Scope / Forbidden

- Gateway access to repositories or direct world mutation;
- provider SDK imports outside adapters;
- automatic or unrestricted model tool execution;
- model-authored success/result/state/version/event/witness/recipient data;
- direct belief, emotion, goal, memory, or relationship mutation;
- prompt text as permission enforcement;
- storing/exposing unrestricted chain-of-thought;
- a database transaction or world lock across an external model call;
- unrecorded retries, infinite repair loops, or silent fallback-to-wait;
- autonomous scheduling, Temporal, Celery, Redis queues, or background loops;
- Oracle automation;
- vector memory/pgvector;
- speech, trade, combat, or broad new actions;
- world creator/general editor;
- a full Agent framework unless research plus an ADR demonstrates clear necessity;
- unrelated auth, deployment, or UI redesign.

## 23. Required Implementation Sequence

1. Complete and commit the official-source/open-source research note.
2. Confirm/update ADR-006 and any affected isolation/authority ADR.
3. Write failing boundary, privacy, schema, concurrency, and recovery tests.
4. Define provider-neutral request/response/error contracts.
5. Define strict input, affordance, and decision contracts.
6. Add migration, repositories, constraints, and lifecycle transitions.
7. Seed immutable prompt/schema version data.
8. Implement deterministic fake adapter.
9. Implement the selected real adapter with mocked contract tests.
10. Implement Observation-only input and prompt builders.
11. Implement durable decision claims, attempts, and recovery.
12. Integrate selected output with the existing action Application service.
13. Add API and causal replay projection.
14. Add frontend decision and replay views.
15. Run concurrency, rollback, leakage, and regression suites.
16. Perform an optional explicitly authorized live-provider smoke test.
17. Update task/status/current-status/known-issues/architecture/development docs.

## 24. Verification Gates

Backend gates should include the repository's canonical equivalents of:

```powershell
$env:RUN_INFRA_TESTS='1'
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy .
python scripts/export_schemas.py --check
python -m alembic check
```

Frontend gates should include:

```powershell
npm run generate:types
npm test
npm run typecheck
npm run lint
npm run format:check
npm run build
```

The optional live smoke must be disabled by default, require an explicit flag and configured budget, and record decision ID, watermark, Observation IDs, prompt/schema hashes, provider/model/request ID, attempts, latency, token usage, nullable cost, validated decision, action/result/event/version or typed rejection, and idempotent replay. Never record the API key.

## 25. Acceptance Criteria

TASK-016 is complete only when:

- preliminary library research and a decision record are present;
- one deterministic fake and one selected real provider adapter satisfy the same Gateway contract;
- the project starts safely with provider mode disabled and no credentials;
- only the current Agent's own state and permitted Observations reach the prompt;
- prompt and output-schema versions are immutable, hashed, and replayable;
- local strict validation rejects all extra/forbidden/unoffered output;
- the model can propose only a server-offered `wait` or adjacent `move`;
- the server derives and submits the final ActionIntent through the existing authoritative path;
- no external call holds a DB transaction or world lock;
- model failure produces no action, event, mutation, or propagated Observation;
- stale state after inference is rejected authoritatively and remains auditable;
- same-key concurrency cannot produce duplicate model/action lifecycles;
- crash recovery cannot duplicate a model call after a persisted completion or duplicate an action after submission;
- every retry/fallback is bounded and individually audited;
- provider usage is recorded and cost is either reproducible from versioned pricing or explicitly `null`;
- causal replay connects input, prompt version, attempts, decision, action, result, event, state, and recipients;
- observer/current-Agent read models preserve ADR-002 isolation;
- frontend clearly separates proposal from authoritative outcome and handles typed JSON errors;
- deterministic adversarial/leakage fixtures pass;
- migrations upgrade/downgrade cleanly;
- full backend/frontend quality gates and TASK-001–015 regressions pass;
- optional live-provider testing remains opt-in and budget-capped;
- architecture, development, current-status, task-status, and known-issues documentation are synchronized.

## 26. Follow-On Decision

Do not preselect TASK-017. Use TASK-016 evidence:

- prioritize Oracle if major-decision classification and decision audit are reliable;
- prioritize scheduling if single-shot decisions are safe but manual triggering is the main limitation;
- prioritize long-term memory if continuity/retrieval is the measured bottleneck;
- prioritize another authoritative action if proposal executability is constrained mainly by the tiny action space.

## 27. Final Completion Report

The implementation report must include:

- research choice and rejected alternatives;
- exact files/migrations/contracts changed;
- authority and privacy boundary evidence;
- deterministic and optional live evaluation results;
- concurrency/crash-recovery evidence;
- backend/frontend command outputs;
- one accepted decision-to-world replay;
- one model failure with proof of zero mutation;
- one stale-state rejection;
- remaining risks and the evidence-based TASK-017 recommendation.
