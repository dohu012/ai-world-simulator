# Architecture Handbook

This is the highest-level architecture contract for the AI world observation and intervention simulator. Future tasks must follow this document unless a new ADR explicitly changes it.

## System Architecture

```text
Frontend
  |
  v
API
  |
  v
Application
  |
  v
World Engine
  |
  v
Repositories
  |
  v
Infrastructure
```

- Frontend presents state, collects user input, and calls public API contracts. It must not infer hidden world state, enforce domain authority, or call model providers directly.
- API owns HTTP parsing, response schemas, auth boundaries when added, and error mapping. It must not implement world rules or write persistence directly.
- Application owns use-case orchestration, transaction scope, and module coordination. It must not hide domain rules inside FastAPI routes.
- World Engine is the only module allowed to transform authoritative world state and create `ActionResult`.
- Repositories persist and retrieve data. They must not decide outcomes, validate actions, call LLMs, or own business policy.
- Infrastructure owns PostgreSQL, Redis, Alembic, configuration, logging, and external technical adapters. It must not own domain vocabulary.

## Module Responsibilities

| Module | Responsible for | Not responsible for | Allowed dependencies | Forbidden dependencies |
| --- | --- | --- | --- | --- |
| Frontend | UI state, API calls, user workflows | World rules, hidden state, LLM calls | API types, generated domain types | Database, backend internals, model SDKs |
| API | HTTP boundary, request/response mapping, errors | Domain decisions, SQL, prompt logic | Application services, API schemas | Repositories for business writes, Model Gateway |
| Application | Use cases, transactions, orchestration | Raw HTTP handling, low-level SQL, UI state | Domain, validators, World Engine, Repositories, Model Gateway | Frontend, framework shortcuts |
| World Engine | Authoritative world mutation and `ActionResult` creation | LLM calls, prompt building, HTTP responses | Domain contracts, validated intents | API, Frontend, model SDKs |
| Observation Builder | Creating per-agent `Observation` from allowed facts/events | Full world dumps, action validation, mutation | Domain read models, visibility rules, repositories through Application | Model Gateway as authority, direct API |
| Action Validator | Validating `ActionIntent` legality, capability, timing, visibility | State mutation, narrative generation, persistence | Domain contracts, policy rules, repositories through Application | LLM SDKs, Frontend |
| Repositories | Persistence and retrieval | Business rules, authorization, model calls | Infrastructure sessions, persistence models, domain mapping | API routes, Model Gateway, prompts |
| Model Gateway | Provider-neutral model invocation | Database writes, permission checks, world mutation | Provider adapters, prompt builders, config | Repositories, SQLAlchemy models, World Engine mutation APIs |
| Memory | Agent memory summaries and retrieval policy | Complete world state, authoritative outcomes | Domain memory contracts, repositories, Model Gateway for summarization | API routes, direct DB writes outside repositories |
| Infrastructure | DB, Redis, config, logging, process adapters | Domain decisions, prompts, product rules | External libraries | Domain depending back on infrastructure |
| Scheduler | Triggering time-based work | Inventing outcomes, bypassing validation | Application use cases, job repositories | Direct mutation without World Engine |

## Data Flow

```text
WorldEvent
  |
  v
Observation
  |
  v
Agent
  |
  v
ActionIntent
  |
  v
ActionValidator
  |
  v
WorldEngine
  |
  v
ActionResult
  |
  v
WorldEvent
```

- `WorldEvent` is an objective event. It may be appended, not silently rewritten.
- `Observation` is a filtered per-agent input. It may redact, summarize, or select information. It must never include a full database snapshot, all facts, other agents' private memories, or undisclosed secrets.
- Agent reasoning may produce `ActionIntent`. It must not produce `ActionResult` or write state.
- `ActionIntent` expresses an attempted action and parameters. It must not claim success.
- `ActionValidator` may accept, reject, or normalize intent. It must not mutate world state.
- `WorldEngine` applies validated intent and world rules. It is the only owner of `ActionResult`.
- `ActionResult` records consequences and emitted events. New `WorldEvent` entries come from this result path.

## Objective And Subjective State

- `WorldFact` is objective state accepted by the world.
- `AgentBelief` is subjective cognition and may be wrong, stale, or incomplete.
- `OracleResponse` is player-provided information, never a command. It must be converted into an allowed `Observation` before an Agent can use it.
- Correlation IDs connect objects; boundary objects must not embed each other in ways that bypass validation.

## Module Boundaries

- May modify world state: World Engine only, through Application use cases.
- May access the database: Repositories and infrastructure setup only.
- May call LLMs: Model Gateway only.
- May build observations: Observation Builder only.
- May validate actions: Action Validator only.
- May define public domain contracts: `backend/app/domain` only; schemas and generated TS are derived outputs.

## Dependency Rules

- Domain must not depend on FastAPI, SQLAlchemy, Alembic, Redis, HTTP clients, LLM SDKs, environment variables, or frontend code.
- API routes must not issue SQL or implement world rules.
- Repositories must not call Model Gateway, prompts, API routes, or World Engine decision methods.
- Model Gateway must not import repositories, SQLAlchemy models, Redis clients for state mutation, or World Engine.
- World Engine must not call provider SDKs, build prompts, or parse HTTP requests.
- Prompt text must never enforce permission, authorization, validation, or world-state authority.

## Development Principles

- Only World Engine can modify world state.
- LLM output can suggest or describe, but can never directly modify the database.
- Agent can produce `ActionIntent`, never `ActionResult`.
- Observation can reveal only the information slice allowed by visibility rules.
- Repository can persist facts, never decide what facts should happen.
- Prompt can express style and reasoning context, never access control.
- Any implementation violating these principles is an architecture error, even if tests pass.

## Ownership

- Observation Builder uniquely owns `Observation` construction.
- Action Validator uniquely owns `ActionIntent` validation.
- World Engine uniquely owns world-state transformation and `ActionResult` creation.
- Model Gateway uniquely owns model-provider invocation.
- Repositories uniquely own persistence operations.
- Application uniquely owns use-case orchestration.
- Domain uniquely owns public contract definitions.

## Changing This Handbook

Update this file when a task changes authority, lifecycle, information isolation, ownership, dependency direction, public contract source, LLM authority, or persistence rules. Such changes also require a new or updated ADR in `decisions/`.
