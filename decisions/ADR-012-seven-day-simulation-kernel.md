# ADR-012: Dependency-free seven-day simulation kernel

- Status: Accepted
- Date: 2026-07-28
- Scope: TASK-019

## Decision

Extend the existing PostgreSQL-backed `WorldRuntimePort` with typed Python policies,
explicit finite-state plans, normalized resource balances plus an append-only
ledger, SHA-256-derived deterministic adjudication, and deterministic schedule
templates for non-L3 residents. PostgreSQL remains the only replay and recovery
authority. No production dependency is added.

The Plan Coordinator may select and advance typed steps, but every consequential
step must submit a server-derived `ActionIntent` through Action Validator and World
Engine. Conditions use a restricted data AST. Models never choose resource
identifiers, quantities, probabilities, rolls, or outcomes.

## Research snapshot

Versions and maintenance state were checked on 2026-07-28 from official
documentation and project repositories. Python compatibility means Python 3.12 or
newer unless noted.

| Area | Candidates checked | Decision and removal seam |
| --- | --- | --- |
| Scheduling | current runtime; SimPy 4.1.1 (MIT); Mesa 3.3.1 (Apache-2); salabim 26.0.0 (MIT); PostgreSQL 18 scheduled rows; Temporal Python SDK 1.18 (MIT) | Keep the current runtime. It already supplies persisted virtual time, transaction fencing, pause/restart, stable claims, and replay linkage. In-memory simulators lose transaction ownership; Temporal adds another operational authority. Seam: `WorldRuntimePort` and typed due-work handlers. |
| Plans/rules | typed Python FSM; transitions 0.9.3 (MIT); python-statemachine 2.5.0 (MIT); durable_rules 2.0.28 (MIT); business-rules 1.1.1 (MIT, inactive); JSONLogic implementations; GOAP/behavior trees | Typed policies selected for static validation, explicit serialization, bounded transitions, and explainable failures. Generic executable rules increase arbitrary-code and versioning risk. Seam: pure `transition_plan` and condition evaluator functions. |
| Resources | normalized balances/ledger; event-sourced ledger; double-entry concepts; JSONB snapshots; SQL constraints/triggers; inventory packages | Normalized accounts plus append-only ledger selected. Account rows make locking and non-negative constraints direct; ledger rows provide audit and compensation. JSONB-only balances and third-party inventory systems weaken database constraints. Seam: resource repository interface and immutable ledger DTOs. |
| Adjudication | thresholds; Python `random.Random`; NumPy `Generator`/PCG64; randomgen; PostgreSQL `random()`; commit-reveal | SHA-256-derived integer rolls selected. It has no global RNG state, platform ordering dependency, or extra package. Stored inputs, digest, roll, threshold, modifiers, and result reproduce after restart. Commit-reveal is unnecessary for a private fixed demo. Seam: versioned `adjudicate` policy. |
| Population | deterministic templates; Mesa AgentSet; ECS; batch SQL transitions; LLM residents | Deterministic templates and bounded batch work selected. Only Lin, Zhou, and Chen are L3; ordinary L0/L1/L2 fixture work makes zero model calls. Seam: `ResidentTier` plus schedule template handlers. |
| Evaluation | pytest/replay scoring; DeepEval; Promptfoo; Langfuse; Phoenix; OpenTelemetry | Deterministic pytest and persisted observer-safe counters selected. Optional live/evaluation tools would add services, content-capture privacy risk, or non-CI determinism. Counters retain a future OpenTelemetry export seam. |

Primary sources:

- https://simpy.readthedocs.io/
- https://mesa.readthedocs.io/
- https://www.salabim.org/manual/
- https://docs.temporal.io/develop/python
- https://github.com/pytransitions/transitions
- https://python-statemachine.readthedocs.io/
- https://www.postgresql.org/docs/18/explicit-locking.html
- https://docs.python.org/3/library/hashlib.html
- https://numpy.org/doc/stable/reference/random/generator.html
- https://opentelemetry.io/docs/specs/semconv/

All selected production behavior uses the Python standard library, Pydantic,
SQLAlchemy, and PostgreSQL already present. Removal means deleting the isolated
TASK-019 policy/scenario modules and downgrading its migration to
`20260727_0007`; no external service or package data must be migrated.

## Executable evidence

`backend/tests/test_seven_day_spikes.py` proves stable equal-time ordering, final
unit exclusion, exact-once recovery, one-shot conditions, bounded plan termination,
restart-stable adjudication, 30-resident zero-LLM ordinary simulation, and explicit
removal seams. These spikes exercise production pure-policy code rather than
throwaway implementations. PostgreSQL race/restart coverage follows with normalized
persistence before resource actions are exposed.

## Failure and privacy semantics

All policy failures return stable codes and make no mutation. A persisted
idempotency key returns the first committed effect. Unknown condition
fields/operators and code-like shapes are rejected. Agent-facing reads expose only
owned, local, or explicitly offered resource summaries and owner plans; raw ledger,
hidden caches, future rescue lists, private diagnoses, and adjudication seeds remain
observer/server data.

