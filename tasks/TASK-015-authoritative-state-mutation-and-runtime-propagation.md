# TASK-015: Authoritative State Mutation and Runtime Event Propagation

## Status

Planned.

## Implementation Research Notes

Dated 2026-07-26. Official sources reviewed: [SQLAlchemy ORM versioning](https://docs.sqlalchemy.org/en/21/orm/versioning.html), [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html), [PostgreSQL advisory locks](https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS), and the [`eventsourcing` project](https://github.com/pyeventsourcing/eventsourcing).

- SQLAlchemy `version_id_col` adds the previous version to ORM `UPDATE`/`DELETE` predicates and raises `StaleDataError` when `Session.flush()` matches no row. It does not protect bulk updates. Generated/server-side versions add mapping and synchronization concerns. This slice already has indexed integer versions mirrored in JSONB and explicitly checks client versions while holding the world lock, so automatic counters would duplicate the chosen per-world serialization rule. The repository flush remains the invariant boundary.
- PostgreSQL row locks live until transaction end, block conflicting writers/lockers but not ordinary reads, and wait unless bounded by `lock_timeout`. `SELECT ... FOR UPDATE` on the existing world row is a visible, queryable serialization boundary. Lock order is always world, then character/topology reads, then writes and append records.
- Transaction advisory locks release on transaction end/rollback and work with pooled connections when the transaction-scoped form is used, but require a collision-safe key derivation and every writer to honor an application convention. A durable world row already exists, so advisory locks add convention and observability cost without solving a missing capability.
- `eventsourcing` supplies aggregates, stored aggregate events, snapshots, projections, and optimistic concurrency. Adopting it would replace the current-state-table plus append-audit design rather than complement it and would require migration, dual-write/rollback, and operational ownership. No insufficiency in SQLAlchemy/PostgreSQL was found.
- Decision: no new dependency; use the world row as the per-world lock, enforce submitted character/world versions, increment both exactly once, keep JSONB/indexed versions equal, and retain `WorldEvent` as audit history rather than rebuild authority. Locations remain an internal persistence/application value model because existing public contracts need only `Character.location_id`. Same-key/different-body retries retain TASK-014 compatibility and return the first lifecycle.

## Implementation Evidence (2026-07-26)

- Migration `20260726_0003` adds four idempotently seeded locations and explicit directed edges. Chen Mo starts at `north-market-store`; `north-market-street` is adjacent and contains an explicit witness; `north-gate` is non-adjacent from the store.
- Strict move validation implements all required stable domain rejection codes. The engine returns exactly three state changes, one movement event, and a typed mutation plan.
- Repository persistence updates objective rows/payloads and flushes intent, result, event, and deterministic runtime Observations before one commit. Same-key replay returns the persisted lifecycle; different keys with stale versions are rejected after world serialization.
- Runtime movement projection delivers mixed/internal information to the actor and indirect visible information to destination witnesses; request reason text is not copied into witness event/Observation content.
- Final backend gates: 103 passed with `RUN_INFRA_TESTS=1`, including 9 PostgreSQL/Redis tests; Ruff and mypy pass. Frontend: 33 tests pass, typecheck and production build pass.


### Final concurrency and smoke evidence (2026-07-26)

- Different-key concurrent moves with the same expected versions produce exactly one success and one auditable version conflict; persisted indexed/JSONB character and world versions are both `2`.
- Same-key concurrent move produces one intent/result lifecycle, with one response marked `idempotent_replay: true`.
- An injected hook after flush and before commit proves objective state, intent, event, and Observation counts all roll back.
- A second transaction contending on the locked world row with a 100ms timeout raises an operational error; the API maps it to HTTP 503 `ACTION_TRANSACTION_UNAVAILABLE` and creates no fictional rejection.
- Accepted smoke: intent `intent-demo-b7f3265a0d8f1591dbc8`, result `result-demo-b7f3265a0d8f1591dbc8`, event `event-demo-b7f3265a0d8f1591dbc8`; location `north-market-store -> north-market-street`, character `1 -> 2`, world `1 -> 2`.
- Stale smoke: intent `intent-demo-e40b1bd8f778002c522a`, result `result-demo-e40b1bd8f778002c522a`, rejected with `CHARACTER_VERSION_CONFLICT`, no event.
- Same-key retry returned the accepted lifecycle IDs unchanged with `idempotent_replay: true`.
## Status

Implemented. Live PostgreSQL migration, idempotent seed, concurrency/rollback/lock-timeout tests, and accepted/stale/retry HTTP smoke all pass.
## Background

TASK-011 through TASK-014 established PostgreSQL-backed reads, replay, deterministic owner-scoped Observations, and an idempotent action lifecycle. The only accepted action is currently parameterless `wait`; it creates an auditable result and private event but changes no character, resource, fact, world version, or world time.

The project plan requires Agents to see only Observations, submit only ActionIntents, and let the World Engine alone decide results. It names movement as deterministic code adjudication and defines the first milestone as isolated information leading to an independent decision, world adjudication, and a visible character trajectory. Before adding model-driven decisions, Oracle automation, or background scheduling, the product needs one useful action whose objective consequences are transactionally safe.

## Why This Is the Next Critical Task

| Candidate | Readiness | Risk if done next | Decision |
| --- | --- | --- | --- |
| Model Gateway and Agent decision loop | Low | The Agent would have only `wait` or unsupported actions, so model behavior could not cause a meaningful consequence. | Defer |
| World clock and scheduler | Medium | It automates a world before state mutation and distributed retry semantics are proven. | Defer |
| Oracle request/timeout workflow | Medium | It still ends in a decision without a useful executable action. | Defer |
| General spatial/event-sourcing platform | Low | Too broad for the fixed-world milestone. | Reject |
| Authoritative state-changing action plus runtime propagation | High | Fits existing contracts and closes the largest causal-loop gap. | **TASK-015** |

TASK-015 must prove more than a second action type:

```text
persisted isolated Observation
  -> current-agent move ActionIntent
  -> state-aware validation
  -> authoritative World Engine mutation plan
  -> per-world serialized transaction + optimistic versions
  -> Character location/version and World version update
  -> ActionResult with explicit StateChanges
  -> movement WorldEvent
  -> runtime Observation Builder projection
  -> persisted per-agent Observations
  -> observer, agent input, and replay
```

## Goal

Implement a production-shaped Gray Harbor movement vertical slice in which a current demo agent can attempt to move to an adjacent location. The system must atomically validate expected state, let only the World Engine decide the transition, update persisted objective state, append the correlated result/event, build allowed runtime Observations, and expose the complete chain through existing reads.

One-sentence acceptance:

> A Gray Harbor character can move through an explicitly defined location graph, and one request produces one concurrency-safe objective state change and one causally complete, information-isolated replay chain.

## Dependencies

- TASK-002, TASK-011, TASK-012, TASK-013, TASK-014
- ADR-001 World State Authority
- ADR-002 Information Isolation
- ADR-003 Action Lifecycle
- ADR-004 Module Boundaries
- ADR-005 Repository Rules
- ADR-007 Concurrency
- ADR-008 Development Principles

## Required Preliminary Open-Source Research

Implementation must begin by adding a dated `## Implementation Research Notes` section to this task. Use current official documentation and compare:

1. **SQLAlchemy ORM version counters**
   - `version_id_col`, generated versions, `StaleDataError`, and its `Session.flush()` scope.
   - Fit with the current indexed columns plus JSONB payload mapping.
2. **PostgreSQL row locks**
   - `SELECT ... FOR UPDATE` / `FOR NO KEY UPDATE`, lock lifetime, waiting, timeout, and deterministic lock order.
   - Whether locking the existing `worlds` row is a clear per-world serialization boundary.
3. **PostgreSQL transaction advisory locks**
   - `pg_advisory_xact_lock`, rollback/release behavior, safe key derivation, connection pooling, and observability.
   - Compare with a normal world-row lock; do not choose advisory locks merely because they exist.
4. **Python `eventsourcing` library**
   - Aggregates, event store, snapshots, projections, and optimistic concurrency.
   - Whether adopting it would replace rather than complement the existing current-state tables and audit events.
5. **No-new-library option**
   - State whether SQLAlchemy + PostgreSQL already satisfy the task.
   - A proposed dependency requires migration cost, rollback plan, maintenance rationale, and proof the current stack is insufficient.

Official starting points:

- SQLAlchemy ORM Versioning: https://docs.sqlalchemy.org/en/21/orm/versioning.html
- PostgreSQL Explicit Locking: https://www.postgresql.org/docs/current/explicit-locking.html
- PostgreSQL Advisory Lock Functions: https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS
- Event Sourcing in Python: https://github.com/pyeventsourcing/eventsourcing

Planning baseline:

- SQLAlchemy version counters constrain an update by primary key and previous version and raise `StaleDataError` on stale state.
- PostgreSQL row locks last for the transaction and block conflicting writers without blocking ordinary readers.
- Advisory locks model application-defined locks but only work when every writer follows the same convention.
- `eventsourcing` is a full aggregate/event-store/projection architecture, not a small concurrency utility.

Expected decision, subject to the required research: add no runtime dependency; lock the existing world row; enforce submitted character/world versions; increment both versions on successful mutation; keep WorldEvent as append-oriented audit history rather than the sole rebuild source. If research overturns this, pause and update the relevant ADR before coding.

## Fixed Demonstration Scenario

Seed a small, explicit Gray Harbor topology—not a map editor:

```text
north-market-store <-> north-market-street <-> emergency-shelter
                              |
                              +----------------> north-gate
```

Exact IDs may follow existing seed vocabulary, but the graph must provide:

- at least four world-owned locations;
- one character at a node with two adjacent choices;
- one valid adjacent move and one unreachable non-adjacent move;
- one destination with an explicit witness character;
- explicit directed/bidirectional edges, never inferred from display order;
- idempotent repeated seeding.

The primary proof should move Chen Mo from the seeded store to an adjacent shared area.

## Existing Interfaces to Preserve

- `POST /demo/worlds/gray-harbor/me/actions`
- all existing observer, perspective, input, and replay GET routes
- `X-Demo-Agent-Id` as demo-only actor identity
- `ActionIntent` expresses an attempt, never success
- `ActionResult.state_changes` is the explicit consequence list
- World Engine alone creates successful transitions and ActionResults
- Observation Builder alone creates Observations
- Repository persists decisions; it never decides validity or consequences
- existing `wait` behavior and idempotency

## Contract and Schema Design

### Location topology

Create the smallest durable topology model that supports deterministic reachability. Decide in Research Notes whether locations need a public domain contract:

- if frontend/agent input needs structured locations, add a strict `Location` contract, export JSON Schema, regenerate TypeScript, update fixtures/docs;
- otherwise use a documented internal domain/application value object and expose only the existing `Character.location_id`.

In either case:

- do not hide adjacency only in opaque character JSON;
- enforce world ownership and unique IDs;
- make edges deterministic, queryable, and seedable;
- prevent cross-world edges;
- omit coordinates, weights, pathfinding, capacity, line of sight, travel time, and editing.

### Move parameters

`ActionType.MOVE` already exists. Parse the JSON transport into a strict internal model:

```json
{
  "target_location_id": "north-market-street",
  "expected_character_version": 1,
  "expected_world_version": 1
}
```

Reject missing, extra, empty, or incorrectly typed fields. Versions are positive integers. The server derives actor, old location, topology, world, time, witnesses, and visibility. The client cannot submit success, witnesses, or old state.

### Version semantics

- Successful move increments `Character.version` once and `World.version` once.
- Indexed version columns and JSONB payload versions must agree.
- Rejection, stale state, retry, or rollback increments neither.
- `updated_at` changes only on successful character mutation.
- Versions are concurrency tokens, not event sequence numbers.

### State changes

A successful result records exactly these authoritative changes:

- `Character.location_id`: old -> target;
- `Character.version`: old -> new;
- `World.version`: old -> new.

Narrative event text is not mutation data.

## Application Transaction Requirements

Application owns one transaction in this order:

```text
derive deterministic intent ID
  -> resolve existing idempotent lifecycle
  -> begin transaction and lock world boundary
  -> re-check lifecycle inside lock
  -> load current world, actor, topology
  -> parse and validate shape/state/versions/reachability
  -> World Engine creates result + mutation plan + event
  -> persist authoritative mutation
  -> Observation Builder creates runtime Observations
  -> persist intent + result + event + Observations
  -> flush invariants and commit once
```

Repository methods must not independently commit. State, versions, intent, result, event, and every runtime Observation are all-or-nothing. Any failure rolls all of them back.

## Validation Requirements

Separate pure parameter validation from state-aware validation. Reject without state mutation when:

- parameters are invalid;
- actor is absent, inactive, or has no location;
- target is absent, cross-world, or equals current location;
- no directed edge exists from current to target;
- expected character or world version is stale.

Stable codes must include:

- `MOVE_PARAMETERS_INVALID`
- `ACTOR_NOT_ACTIVE`
- `ACTOR_LOCATION_UNKNOWN`
- `TARGET_LOCATION_NOT_FOUND`
- `MOVE_SAME_LOCATION`
- `MOVE_NOT_REACHABLE`
- `CHARACTER_VERSION_CONFLICT`
- `WORLD_VERSION_CONFLICT`

Domain rejections are auditable and emit no movement event/Observation. Lock timeout, deadlock, or serialization failure is an operational error—not a fictional rejected action—and must roll back and map to a stable API error.

## World Engine Requirements

Extend `GrayHarborWorldEngine` without creating a generic plugin system. A valid move produces:

- succeeded ActionResult;
- explicit StateChanges;
- a typed mutation plan for persistence;
- one `EventType.MOVEMENT` event;
- participants/witnesses derived from current state;
- deterministic metadata and one intent-rooted correlation chain.

The engine receives a validated state snapshot. It must not query SQL, mutate ORM objects, commit, call Observation Builder/LLM, or trust client-supplied old state, versions, witnesses, or visibility. Existing `wait` remains valid.

## Runtime Observation Propagation

Make TASK-013 Observation Builder usable for action-generated runtime events:

- actor receives an internal/mixed movement Observation;
- explicit destination witnesses receive only the allowed visible projection;
- non-witnesses receive nothing;
- recipients derive from server state, never request fields;
- IDs derive deterministically from event + recipient;
- retries produce no duplicates;
- source event, time, location, and correlation remain replayable;
- witness input never leaks actor-private reason text or unrelated state.

Do not add range, line of sight, social graphs, channel routing, or general diffusion.

## Idempotency and Concurrency

### Same idempotency key

The first completed request defines the lifecycle. Repeating it returns the exact persisted lifecycle with `idempotent_replay: true`, without revalidation, version changes, event append, or Observation rebuild. Research Notes must decide and test whether a different body with the same key returns the original lifecycle for TASK-014 compatibility or raises `IDEMPOTENCY_KEY_REUSED`.

### Different keys, same expected versions

For concurrent moves by one actor from the same versions:

- exactly one succeeds;
- the loser becomes an auditable version conflict or a documented retryable conflict if that is required by the transaction design;
- loser emits no movement event/Observation;
- versions increment exactly once.

### Different actors, same world

Serialize per world according to ADR-007 for deterministic correctness. Do not optimize to per-character concurrency in this task.

### Lock discipline

Use one documented lock order, never hold locks across external calls, configure/document bounded lock timeout, distinguish operational failures from domain rejections, and prove concurrency without arbitrary sleeps.

## Persistence Requirements

- one new Alembic migration; never edit applied migrations;
- idempotent topology seed;
- transactional repository load/mutation/Observation operations;
- Pydantic remains the JSONB mapping boundary;
- indexed/payload version consistency checks;
- uniqueness/indexes for adjacency and event/Observation idempotency;
- no event-store replacement or aggregate rebuild.

## API and Read Model Requirements

Keep the existing POST envelope and accept `move` with the typed parameter shape. A successful response returns intent, result, movement event, and replay flag. Stable typed errors distinguish malformed transport, unseeded world, unknown actor, stale state, and operational transaction failure. Routes contain no SQL, topology rules, version arithmetic, or witness inference.

Observer reads show persisted location and versions. Actor perspective/input show its new location and runtime Observation. Witnesses see only their own projection; non-witnesses see none. Extend Replay Inspector only enough to show expected versions, rejection code, location/version StateChanges, movement event, recipient count, and full correlation. Do not add playback, time travel, animation, aggregate rebuild, or a general action composer.

## Allowed Changes

- backend API, application, domain (only if justified), repositories, Gray Harbor seed, World Engine, database models
- one Alembic migration and backend tests/fixtures/schema exports
- generated frontend types if a public contract changes
- demo-world frontend/read types and relevant docs/ADRs

## Forbidden Changes

- no Model Gateway, LLM, prompt assembly, or autonomous Agent
- no memory, embeddings, vector DB, or belief loop
- no scheduler, Temporal, Celery, worker, Redis queue, offline clock
- no Oracle automation or player response write flow
- no inventory, trade, combat, persuasion, random adjudication, resources, or speech
- no general pathfinding, geometry, line of sight, map editor, or world creator
- no full event sourcing, CQRS platform, snapshots, or event-store migration
- no direct SQL/business rules in routes, repository decisions, or frontend authority
- no production auth expansion or unrelated dependency upgrades

## Required Implementation Sequence

1. Write dated official-source Research Notes and decide lock/version/library strategy.
2. Add failing tests for shape, reachability, stale versions, StateChanges, and recipients.
3. Add migration and idempotent topology seed.
4. Add transactional repository primitives without intermediate commits.
5. Extend Validator and World Engine using state value objects.
6. Implement the single Application-owned transaction.
7. Extend API/read models and Replay Inspector.
8. Add PostgreSQL concurrency and rollback tests.
9. Run full backend/frontend gates.
10. Update task evidence, ADR-007, status, contracts, and known limits.

## Backend Test Requirements

At minimum cover:

- strict move parsing; adjacent/bidirectional/directed moves; missing/inactive actor; unknown/cross-world/same/unreachable target; stale character/world versions;
- exact StateChanges; server-derived witnesses/old state; existing wait regression;
- actor/witness/non-witness projections, deterministic IDs, and no reason leakage;
- migration from current head and idempotent seed;
- indexed columns and JSONB mutate together;
- injected pre-commit failure leaves state and lifecycle counts unchanged;
- same-key sequential/concurrent retry creates one lifecycle;
- different-key concurrent stale moves yield one mutation;
- no duplicate event/Observation; per-world serialization; stable lock failure mapping;
- observer, perspective, input, and replay show one committed chain;
- architecture imports preserve API/Application/Engine/Repository boundaries.

Coordinate concurrency tests with barriers/events or test hooks, not timing sleeps.

## Frontend Test Requirements

At minimum cover observer location after persisted move; Replay Inspector StateChanges/version conflicts/recipient count; actor runtime movement input; non-witness isolation; wait-chain regression; loading/error/empty states; same-origin `/api`; existing observer, perspective, input, replay, and health behavior.

## Verification Commands

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

Also migrate/seed and smoke-test one accepted move, one stale-version move, and one same-key retry against live PostgreSQL. Record returned IDs and version transitions.

## Acceptance Criteria

- persisted idempotent explicit topology exists;
- move accepts only the documented typed shape;
- valid adjacent move changes location and increments character/world versions once;
- only World Engine decides the transition;
- mutation plus intent/result/event/runtime Observations commit atomically;
- rejection/rollback changes no objective state;
- retries never duplicate mutation or causal records;
- concurrent stale requests cannot both succeed;
- recipients derive server-side and only allowed agents receive Observations;
- observer, input, and replay read the same PostgreSQL chain;
- wait and isolation remain compatible;
- all infrastructure tests, lint, type checks, frontend tests, and build pass;
- no deferred LLM/scheduler/memory/Oracle/full-event-sourcing scope enters the task.

## Documentation Updates

- this task's Research Notes, evidence, and final status
- `tasks/TASK_STATUS.md`
- `docs/current-status.md`
- `docs/known-issues.md`
- `docs/domain-contracts.md` if a public contract changes
- `decisions/ADR-007-concurrency.md` with chosen lock/retry semantics
- architecture handbook/new ADR only if an established boundary changes

## Follow-On Direction

After TASK-015, prefer TASK-016 as a constrained Agent decision slice:

```text
Observation-only input
  -> provider-neutral Model Gateway
  -> strict structured decision
  -> allowlisted wait/move ActionIntent
  -> existing Validator and World Engine
  -> replayed prompt/version/cost/action/result evidence
```

TASK-015 must not pre-implement it.

## Final Summary Format

- official-source research and decision;
- topology/migration;
- validation/mutation behavior;
- atomicity/idempotency/concurrency evidence;
- Observation isolation evidence;
- API/replay changes;
- commands and smoke scenarios;
- remaining limits and docs/ADR updates.




