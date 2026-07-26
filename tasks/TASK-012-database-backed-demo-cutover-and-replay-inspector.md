# TASK-012: Database-Backed Demo Cutover and Replay Inspector

## Background

TASK-004 through TASK-010 established the observer, agent-perspective, current-agent,
and Observation-only input boundaries using fixed service fixtures. TASK-011 added
PostgreSQL domain tables, an idempotent Gray Harbor seed, repository mapping, and
database-backed `/persistent` and `/replay` proof routes.

The product still has two competing runtime read paths:

- the main dashboard and agent previews use fixture-backed endpoints;
- persistence and replay are available only through parallel debug endpoints.

This means the UI can appear healthy without proving that seeded world state,
information isolation, and causal replay work together. Before implementing a real
Observation Builder, World Engine, scheduler, or LLM agent, the fixed demo must use
the persistent read path as its normal path.

## Goal

Make seeded PostgreSQL data the single runtime source for all existing Gray Harbor
demo reads, and add a compact observer-only replay inspector that makes event,
observation, Oracle, action, result, source, and correlation links visible.

The task is a read-path cutover. It does not create or mutate simulation state.

## Dependencies

- TASK-005 through TASK-011
- ADR-002 Information Isolation
- ADR-004 Module Boundaries
- ADR-005 Repository Rules
- ADR-007 Concurrency

## Core Outcome

```text
Gray Harbor application seed
  -> PostgreSQL domain tables
  -> repository
  -> application read service
  -> existing demo APIs
  -> observer / agent preview / agent input / replay inspector
```

After TASK-012, removing or corrupting the database seed must be observable through
the existing demo UI; the main experience must no longer silently succeed from a
hard-coded service fixture.

## Required Preliminary Review

## Implementation Notes

- `demo_world.py` retains the fixed literals and legacy composition helpers as seed definitions; runtime routes no longer call `get_gray_harbor_demo_world()` or the fixture perspective/input helpers.
- FastAPI resolves `get_db_session()` once per request and closes that request-owned `AsyncSession` after the application read service returns.
- `GrayHarborReadService` is the composition boundary: observer reads may include every seeded record, while agent perspective and input reads are scoped by repository ownership fields before presentation.
- `/persistent` remains a temporary observer compatibility alias and delegates to the same application service as the primary route; its agent sub-route was removed because the primary scoped route is now persistent.
- TanStack Query keeps `retry: false`, so an unavailable or unseeded database produces one explicit typed error instead of repeated requests or fixture fallback.
- Replay Inspector is a compact observer/debug audit projection. It sorts and links existing records but deliberately has no playback, time travel, animation, scrubbing, aggregate rebuild, or mutation controls.
- Chen's Oracle-response-to-Observation projection is isolated in application code and marked temporary until TASK-013.

Before implementation, add short Implementation Notes to this task covering:

- which parts of `demo_world.py` are seed definitions versus runtime read logic;
- how FastAPI dependencies will provide one `AsyncSession` per request;
- how the application service will preserve observer and agent information boundaries;
- whether `/persistent` remains as a temporary alias or is removed;
- how TanStack Query retry behavior should handle an unseeded database;
- how the replay inspector avoids becoming a full replay player.

No new external library is expected. If a library is proposed, document why the
existing FastAPI, SQLAlchemy, Pydantic, and TanStack Query stack is insufficient.

## Backend Scope

### Application read service

Add an application-layer Gray Harbor read service that owns composition of:

- observer read model;
- selected-agent perspective;
- current-agent perspective;
- current-agent Observation-only input;
- replay/debug read model.

API routes call this service. Routes must not issue SQL, assemble visibility filters,
or map ORM records directly.

### Existing API cutover

The following existing endpoints must read seeded PostgreSQL data:

- `GET /demo/worlds/gray-harbor`
- `GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective`
- `GET /demo/worlds/gray-harbor/me/perspective`
- `GET /demo/worlds/gray-harbor/me/input`
- `GET /demo/worlds/gray-harbor/replay`

Preserve current response shapes and demo access behavior unless a documented defect
requires a narrow correction.

### Fixture separation

- Runtime routes must not call `get_gray_harbor_demo_world()`.
- Fixed literals may remain as seed source data, but should be clearly separated from
  runtime read services, preferably under a seed-data module.
- The application must not auto-seed during API startup.
- An unseeded database must return a stable typed API error rather than falling back
  to fixture data.
- `/persistent` may remain as a documented compatibility alias during TASK-012, but it
  must use the same application service as the primary endpoint.

### Information isolation

- Observer reads may include all fixed demo records.
- Agent perspective reads include only the selected/current agent's character,
  profile, observations, beliefs, Oracle records, and actions.
- Agent input contains only world summary, current character, profile, and allowed
  `Observation` records.
- Lin must never receive Chen's Oracle request/response, action intent/result, belief,
  or Oracle-derived observation.
- Chen's fixed Oracle advice may continue to be projected as an Observation for this
  task, but the projection must be isolated in application code and explicitly marked
  as temporary pending TASK-013.

### Replay read model

Replay must expose enough data to inspect:

- objective event order;
- event visibility;
- `source_event_id`;
- `source_action_id`;
- `correlation_id`;
- observations linked to each event;
- Chen's Oracle request -> response -> intent -> result -> emitted event chain;
- records that have no causal link, without crashing or fabricating one.

Replay remains an observer/debug read. It is not an event-sourced aggregate rebuild.

## Frontend Scope

Keep the existing observer dashboard and agent panels visually recognizable.

Add one compact `Replay Inspector` panel that:

- reads `GET /demo/worlds/gray-harbor/replay`;
- renders objective events in deterministic order;
- shows source/correlation identifiers in a readable compact form;
- shows related observation counts and action/Oracle chain membership;
- supports loading, error, empty, and success states;
- clearly labels itself observer/debug-only;
- does not implement play, pause, time travel, animation, scrubbing, or mutation.

The frontend must continue to use the same-origin `/api` transport introduced during
TASK-011 stabilization. Do not reintroduce browser calls to `localhost:8000`.

## Allowed Changes

- `backend/app/api/`
- `backend/app/application/` (new module/package allowed)
- `backend/app/repositories/`
- `backend/app/services/demo_world.py`
- a new backend seed-data module
- `backend/tests/`
- `frontend/src/features/demo-world/`
- `frontend/src/lib/api-client.ts` only if required for typed error handling
- `frontend/src/types/api.ts`
- relevant task and documentation files

Database schema changes are allowed only if a concrete missing read index or constraint
is demonstrated. Any migration must remain small and be justified in this task.

## Forbidden Changes

- No real World Engine.
- No real Observation Builder or general visibility-rule engine.
- No Action Validator.
- No real world-time advancement.
- No agent execution or decision loop.
- No LLM, Model Gateway, embeddings, memory, Temporal, Celery, or scheduler.
- No player Oracle submission/write workflow.
- No authentication system or production authorization.
- No free-world creator or multi-world UI.
- No frontend database knowledge.
- No fixture fallback when the database is unavailable or unseeded.
- No rewriting public Pydantic domain contracts merely to simplify persistence mapping.

## Backend Test Requirements

At minimum cover:

- migration and seed integration still pass;
- seed remains idempotent;
- primary observer endpoint reads through the application service/repository;
- primary observer response remains compatible with the current frontend shape;
- all events are returned in deterministic objective order;
- selected-agent and current-agent routes are DB-backed;
- current-agent input is DB-backed and Observation-only;
- Chen receives the expected Oracle-derived Observation;
- Lin cannot receive any Chen-private records;
- replay links Chen's Oracle/action/result/event chain;
- replay reports observation counts/source links correctly;
- unknown agent returns the existing stable error;
- unseeded world returns a stable typed error and never fixture data;
- database outage does not change `/health` and preserves designed readiness 503 behavior;
- routes contain no direct SQL and do not call the fixture getter.

Run the infrastructure-gated suite with `RUN_INFRA_TESTS=1`.

## Frontend Test Requirements

At minimum cover:

- existing observer dashboard tests continue to pass;
- selected-agent perspective tests continue to pass;
- current-agent preview and input-feed tests continue to pass;
- Replay Inspector loading, error, empty, and success states;
- deterministic event ordering;
- visible source/correlation information;
- related observation counts;
- Chen causal chain rendering;
- no raw Chen-private data appears in Lin-facing panels;
- all browser requests use same-origin `/api` paths;
- no regression to health dashboard behavior.

Run:

```powershell
cd backend
$env:RUN_INFRA_TESTS="1"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check app tests migrations
.\.venv\Scripts\mypy.exe app

cd ..\frontend
npm run test
npm run typecheck
npm run build
```

## Acceptance Criteria

- The normal Gray Harbor observer page is rendered from seeded PostgreSQL data.
- All existing agent-facing demo reads are DB-backed and retain their isolation.
- Stopping PostgreSQL or removing the seed produces an explicit error; no fixture
  fallback hides the failure.
- The observer can inspect objective event order and Chen's complete causal chain in
  the Replay Inspector.
- Existing UI and API response shapes remain compatible.
- No simulation, agent, LLM, scheduler, or mutation behavior is introduced.

One-sentence acceptance:

> Gray Harbor's existing observer and agent experience now proves the persistent
> world end to end, while the observer can inspect its causal history without any
> runtime dependency on hard-coded fixture reads.

## Documentation Updates

- `tasks/TASK-012-database-backed-demo-cutover-and-replay-inspector.md`
- `tasks/TASK_STATUS.md`
- `docs/current-status.md`
- `docs/known-issues.md`
- `docs/domain-contracts.md`
- `docs/architecture-handbook.md` only if an authority boundary changes
- add/update an ADR only if the established dependency direction changes

## Follow-On Direction

TASK-013 should be a deterministic Observation Builder and visibility propagation
vertical slice:

```text
WorldEvent / WorldFact
  -> visibility and channel rules
  -> per-agent Observation
  -> persisted isolated input
```

TASK-013 should begin only after TASK-012 proves that all consumers use the persistent
read path. Action validation/World Engine should follow Observation Builder, and model
integration should follow a deterministic non-LLM action lifecycle.

## Final Summary Format

- What changed.
- Which runtime fixture dependencies were removed.
- API compatibility results.
- Information-isolation evidence.
- Replay-chain evidence.
- Tests/checks run, including infrastructure tests.
- Remaining limitations.
- Documentation updated.

## Status

Done.
