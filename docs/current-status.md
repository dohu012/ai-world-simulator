# 当前状态

当前阶段：TASK-014 已完成；TASK-015 已规划。

已完成内容：

- TASK-001：工程骨架、FastAPI 后端、Next.js 前端、PostgreSQL/Redis 本地基础设施、Alembic、健康检查、测试与基础文档。
- TASK-002：World、Character、AgentProfile、WorldFact、AgentBelief、Observation、ActionIntent、ActionResult、WorldEvent、OracleRequest、OracleResponse 的最小领域契约；JSON Schema 稳定导出；TypeScript 类型生成；示例数据和边界校验测试。
- TASK-003：Architecture Handbook、Development Handbook、AI Collaboration Guide、ADR、Task 系统与长期协作规范。
- TASK-004：固定世界观察台前端切片。首页展示灰港封锁区静态 demo，明确区分客观世界事件、角色 Observation、主观 Belief、玩家启示、ActionIntent 与 ActionResult；健康检查功能保留为页面下方开发状态区。

尚未完成内容：

- 数据库领域模型、Repository、业务 Service、世界裁定、感知过滤、Agent 决策、Oracle 投递流程及业务 API。
- World Engine、Observation Builder、Action Validator、Model Gateway、Memory、Scheduler 的业务实现。
- 生产部署、备份、TLS、可观测性和高可用方案。

TASK-005 建议方向：

- 实现 Fixed World Demo Read API，由后端提供固定世界 demo 数据，前端从只读 API 读取，但仍不实现真实数据库、World Engine 或 LLM。
## TASK-005 Update

TASK-005 is complete. The Gray Harbor fixed observer demo is now served by the backend read-only API `GET /demo/worlds/gray-harbor`, and the frontend observer uses `apiGet` with TanStack Query to render the same objective/subjective UI sections from the API response.

The current product state is still a fixed demo slice. This confirms the first business read boundary from backend read model to API response to frontend query, but it is not a real running world simulation.

## TASK-006 Update

TASK-006 is complete. The backend now exposes `GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective` for one fixed demo character's local perspective, while the full observer endpoint remains unchanged.

The frontend observer still uses `GET /demo/worlds/gray-harbor` for the objective dashboard timeline and character selector, but the selected character's first-person Observation, Belief, Oracle, and action lifecycle panels now read from the agent-scoped perspective query. This is fixture/API-level isolation only; it is still not a real runtime Observation Builder, memory permission system, prompt isolation layer, or world simulation.

## TASK-007 Update

TASK-007 is complete. The backend now exposes demo-only current-agent perspective reads at `GET /demo/worlds/gray-harbor/me/perspective`, with the caller identity fixed by `X-Demo-Agent-Id` instead of a URL path parameter.

This boundary is intentionally narrow: it accepts only the three Gray Harbor special agents and reuses the TASK-006 agent-scoped read model. `GET /demo/worlds/gray-harbor` remains the observer-only full payload, and `GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective` remains available as an observer/dev demo endpoint.

## TASK-008 Update

TASK-008 is complete. The frontend now includes a lightweight `Agent Preview` harness that calls `GET /demo/worlds/gray-harbor/me/perspective` through the fixed demo header path introduced in TASK-007.

The main observer dashboard remains unchanged. The preview is a small agent-facing test surface for the current-agent data flow, and its tests verify loading, error, successful rendering, header usage, and no fallback to observer payload private records.

## TASK-009 Update

TASK-009 is complete. The backend now exposes `GET /demo/worlds/gray-harbor/me/input`, a fixed demo current-agent input feed that uses `X-Demo-Agent-Id` and returns only the world summary, current character, current profile, and allowed `Observation` records.

Chen Mo's fixed Oracle advice is projected into an `Observation` with `observation_type: "oracle"`, demonstrating the ADR-002 direction that player-provided information should become allowed local input before agent reasoning. This is still a hand-authored demo projection, not a real Observation Builder or agent runtime.

## TASK-010 Update

TASK-010 is complete. The frontend now includes an `Agent Input Feed` harness that calls `GET /demo/worlds/gray-harbor/me/input` and renders the Observation-only current-agent input stream.

The panel sits below the current-agent perspective preview. It keeps the observer dashboard unchanged and shows Chen's Oracle advice only as an `oracle` Observation, not as raw Oracle/action lifecycle records for agent input.

## TASK-011 Update

Gray Harbor now has PostgreSQL persistence models, an application-level idempotent seed, repository mapping through the canonical Pydantic contracts, and database-backed `/persistent` and `/replay` demo reads. Existing fixture routes remain temporarily available during migration.


## Next Planned Task: TASK-012

TASK-012 will cut the existing Gray Harbor observer, agent perspective, current-agent,
and agent-input APIs over to the PostgreSQL repository path and add a compact
observer-only Replay Inspector. This closes the remaining runtime fixture dependency
before TASK-013 introduces a deterministic Observation Builder and visibility
propagation vertical slice.

## TASK-012 Update

All normal Gray Harbor observer, selected-agent, current-agent, Observation-only input, and replay reads now flow from PostgreSQL through WorldRepository and GrayHarborReadService. The observer UI includes a compact read-only Replay Inspector for deterministic event order, visibility, source/action/correlation identifiers, linked observation counts, and Oracle/action chain membership. No runtime route falls back to the fixed seed fixture.

## Next Planned Task: TASK-013

Implement the deterministic Observation Builder and visibility propagation slice; Chen's temporary application-layer Oracle projection remains until that boundary exists.

## TASK-013 Update

Observation Builder is now the unique application boundary for Gray Harbor event and Oracle information delivered to agents. The seed deterministically persists nine owner-scoped Observations: public events reach all agents, secret/private events reach participants, restricted events may include explicit indirect auditory recipients, and Oracle advice becomes a persisted `oracle` Observation. Agent input no longer creates Oracle data at read time.

The next vertical slice should introduce a minimal authoritative action validation and adjudication lifecycle, while continuing to keep agents limited to Observation input and Action output.

## TASK-014 Update

Gray Harbor now proves one complete authoritative action lifecycle. A current demo agent may submit an idempotent `wait` attempt; Application creates the intent, pure validation accepts or rejects it, the minimal Gray Harbor World Engine creates the result and optional private event, and Repository commits the lifecycle atomically. Replay exposes the resulting correlation chain, while agent perspectives remain owner-filtered.

The next slice should add one meaningful state-changing action with explicit preconditions and optimistic world-version checks, without adding model-driven agent execution yet.

## Next Planned Task: TASK-015

TASK-015 will implement the first meaningful authoritative world mutation: a current demo agent can move across a small persisted Gray Harbor location graph using explicit character/world versions. Application will serialize mutations per world, World Engine alone will produce the transition, and character/world state, ActionResult, movement event, and runtime-built Observations will commit in one transaction.

Before implementation, TASK-015 requires a documented official-source comparison of SQLAlchemy version counters, PostgreSQL row/advisory locks, and the Python `eventsourcing` library. The expected direction is to retain the current SQLAlchemy/PostgreSQL architecture, lock the existing world row, and avoid full event sourcing. Model-driven Agent decisions, Oracle automation, and scheduler work remain deferred until the system has a useful concurrency-safe action space.

## TASK-015 Update

Gray Harbor now supports an authoritative `move` ActionIntent across a persisted explicit location graph. Application serializes moves on the world row, validates submitted character/world versions, and commits the character/world mutation, ActionResult, movement event, and owner-scoped runtime Observations together. Observer, agent input, and replay read the same persisted causal chain. Model-driven decisions and scheduling remain deferred.

## TASK-015 Final Verification

TASK-015 concurrency and rollback closure is complete. The full backend suite passes 103 tests with infrastructure enabled, including different-key stale competition, same-key concurrency, pre-commit rollback, and bounded world-lock timeout. Real HTTP smoke confirms the accepted move 1→2 transition, auditable stale rejection, and exact same-key replay. Frontend passes 33 tests, typecheck, and a clean production build.

## Next Planned Task: TASK-016

TASK-016 will add the first auditable model-driven Agent decision vertical slice. Chen will decide once from only his own state and persisted Observations, through a provider-neutral Model Gateway and a strict server-owned `wait`/`move` affordance contract. The selected proposal will still traverse the existing Validator, World Engine, PostgreSQL transaction, Observation propagation, and causal replay path; the model will never author results or mutate world state.

Before implementation, TASK-016 requires a dated official-source and open-source comparison covering provider SDKs versus LiteLLM/direct HTTP, native structured output versus PydanticAI/Instructor/local validation, explicit orchestration versus Agent frameworks, PostgreSQL audit versus optional OpenTelemetry/Langfuse/Phoenix telemetry, and deterministic pytest fixtures versus opt-in live evaluation tools. The expected direction is a small internal Gateway with a deterministic fake and one real adapter, but implementation must justify the choice in an ADR.

The task also requires durable model-call claims and crash recovery without holding database/world locks during inference, strict privacy/leakage tests, typed JSON failures, bounded and audited retries, usage/cost metadata, and a replay chain from Observation watermark through model attempts and decision to authoritative action result, event, state version, and recipient Observations. Scheduling, Oracle automation, long-term vector memory, unrestricted tools, and broad new actions remain out of scope until this slice produces evidence for TASK-017.

## TASK-016 Update

Gray Harbor now supports one manually triggered, auditable Chen decision from only Chen's own state and persisted Observations. A provider-neutral gateway (disabled/fake/OpenAI direct HTTP) returns a strictly validated wait/move proposal; the server allowlist derives the final ActionIntent and the existing Validator, World Engine and atomic Observation propagation remain authoritative. PostgreSQL records decision claims, immutable prompt/schema hashes and each bounded model attempt without holding a transaction during inference. The frontend separates the model proposal from the authoritative engine outcome. Autonomous scheduling, Oracle automation, vector memory and unrestricted tools remain deferred.

## Next Planned Task: TASK-017

TASK-017 will complete the largest remaining part of the product plan's first technical milestone: a durable event-driven Gray Harbor runtime that advances world time, publishes one scheduled event exactly once, wakes only affected Agents, and carries one major Chen decision through a restart-safe Oracle reply-or-timeout window into a fresh TASK-016 decision and authoritative TASK-015 action. Before implementation it must close TASK-016 recovery/replay gates and publish a dated Temporal/PostgreSQL/Celery/worker comparison with timer, signal, two-worker claim, restart, and virtual-time spikes. Long-term vector memory, broad actions, dialogue, world creation, and production push delivery remain deferred until this offline autonomy loop is proven safe and engaging.

## TASK-017 Implementation Update

TASK-017 now has a PostgreSQL-backed adapter behind the runtime port, a monotonic fenced world clock, bounded stable-order scheduled-event publication, Chen-only wake coalescing, a server-created Oracle window, transactional reply/timeout winner delivery through Observation Builder, notification outbox records, and a re-entrant final TASK-016 decision that still submits through the authoritative Action Service and World Engine. Runtime defaults disabled.

The fixed runtime, Oracle inbox/reply and notification APIs are exposed, and the frontend contains World Runtime Control, Oracle Inbox, and decision-linked causal replay surfaces. Deterministic tests do not sleep. Runtime defaults disabled.

TASK-016 and TASK-017 are complete. Docker PostgreSQL verification covers fenced decision takeover, persisted-completion and post-action crash recovery, stale-after-inference rejection, two-worker schedule publication, restart while awaiting Oracle input, reply/timeout transactional winners, explicit silence, malicious reply text constrained to server affordances, decision-linked replay, and zero duplicate logical work. The final backend suite passes 125 tests; Ruff, format, mypy, schema export, Alembic check, and real 0006/0005 downgrade-to-0004 then upgrade-to-head pass. Frontend passes 33 tests, typecheck, ESLint, format, and production build.

## Next Planned Task: TASK-018

TASK-018 will complete the missing multi-character half of the product plan's first technical milestone. One objective Gray Harbor fact will travel to Lin, Zhou, and Chen through different durable channels, delays, reliability and distortion, producing owner-scoped and potentially conflicting belief histories before a bounded Chen-Zhou exchange can correct or preserve the rumor.

The task includes server-authoritative communication actions, restart-safe message transmissions, append-only belief evidence, selective wakes, three-Agent TASK-016 decisions, privacy-safe causal replay, and observer/Agent frontend surfaces. It explicitly excludes general world creation, long-term vector memory, broad actions, production push, and unbounded dialogue.

Before implementation, TASK-018 requires a dated ADR and executable spikes comparing graph/routing libraries, PostgreSQL versus stream/broker delivery, belief-revision approaches, explicit orchestration versus multi-Agent dialogue frameworks, and deterministic evaluation/observability tools. Library adoption must follow evidence rather than precede it.

## TASK-018 Update

TASK-018 is complete. Gray Harbor now has deterministic direct, bulletin, and distorted courier propagation; owner-scoped append-only evidence and belief revisions; a PostgreSQL-backed bounded Chen-Zhou correction exchange; privacy-safe observer/Agent APIs; and propagation, belief-evolution, and conversation UI. The real PostgreSQL smoke proves restart/two-worker idempotency and exact counts of five delivered transmissions, five Observations, and five evidence rows. No paid model call or new production dependency was used.

## Next Planned Task: TASK-019

TASK-019 will turn the completed information-propagation milestone into a seven-day Gray Harbor internal-playtest slice: exactly 30 tiered residents, durable goals and plans, contested food/medicine/capacity, at least five narrow authoritative action types, hard and conditional events, reproducible uncertain adjudication, and a consequential Day-7 outcome. Before implementation it requires a dated ADR and executable spikes comparing discrete-event simulation, plan/rule engines, resource ledgers, deterministic RNG, tiered population simulation, and behavior evaluation. Long-term vector memory, production notifications, free world creation, and 30 independent LLM Agents remain deferred until this fixed-world fate loop is engaging, explainable, private, restart-safe, and cost-bounded.
