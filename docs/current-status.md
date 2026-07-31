# 当前状态

当前阶段：TASK-019 已完成；TASK-020 已规划。

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

## TASK-019 Foundation Update

TASK-018 baseline is 113 passing and 18 opt-in infrastructure tests skipped in
1.48 seconds. ADR-012 selects the existing PostgreSQL runtime, typed finite-state
policies, normalized balances plus append-only ledgers, SHA-256-derived
adjudication, deterministic resident schedules, and pytest/replay evaluation with
no new production dependency.

The versioned `gray-harbor-seven-day` 1.0.0 fixture freezes exactly 30 residents,
three L3 Agents, initial food/water/medicine and capacities, and the seven daily
scenario events. Production pure policies and executable spikes now cover stable
equal-time ordering, final-unit exclusion, exact-once retry, one-shot Day-5
conditions, bounded plan termination, restart-stable uncertain outcomes, zero-LLM
ordinary residents, and removal seams. TASK-019 remains in progress: normalized
persistence and constraints are the next implementation stage.

## TASK-019 Implementation Update

Migration `20260728_0008` adds normalized resource definitions/accounts/ledger,
goals/plans, conditional events, adjudication traces, and a persisted scenario
checkpoint. Explicit reset and row-locked bounded advance survive API process
restart. Observer and header-derived owner APIs expose the seven-day state without
copying other owners' plans/actions or future outcomes into the owner view.

Six server-offered scenario action types now traverse the existing ActionIntent,
Action Validator, World Engine, ActionResult, WorldEvent, Observation, and replay
path. Affordances bind action type and actor; forged, cross-actor, and hidden-cache
attempts reject with stable codes. The internal-playtest panel supports reset,
single-day advance, resource inspection, plan blockage/completion, typed action
failures, and Day-7 irreversible outcomes.

Migrations `0008` and `0009` now pass downgrade to `20260727_0007`, upgrade to
head, and drift checks on PostgreSQL. Reset persists exactly 30 residents, three L3
Agents, four deterministic schedule templates, initial resources, goals, plans,
and a fenced scenario generation. Only the existing runtime advances days.

Runtime progression automatically submits seven versioned server affordances
through the existing action lifecycle. Resource source accounts and plans are
locked before validation; accepted consumption/transfer/help effects update
versioned accounts and append per-leg ledger records in the same transaction as
ActionResult, event, Observation, and replay. A full seven-day PostgreSQL run,
including a Day-4 service reconstruction, ends with seven persisted actions,
conserved transfers, medicine consumption, Chen's abandoned plan, Day-7 outcomes,
and zero ordinary-resident model calls. Running the scenario integration suite
twice proves reset-generation fencing and same-generation idempotency.

Current gates pass 179 infrastructure-enabled backend tests and 34 frontend tests
plus Ruff, mypy,
schema check, TypeScript, ESLint, Prettier, production build, and Alembic drift.
TASK-019 is complete. Day-5 shipment stop is a persisted one-shot condition that
atomically emits one event and owner-safe Observations. Day-7 rescue seats are a
capacity-10 resource: two concurrent PostgreSQL sessions produce exactly one
successful allocation and one `RESOURCE_INSUFFICIENT` rejection, leaving
available 0 and consumed 10. Persisted final plan states are Lin `completed`,
Zhou `completed`, and Chen `abandoned`.

Final gates: 182 infrastructure-enabled backend tests; 34 frontend tests; Ruff,
mypy, schema export, TypeScript, ESLint, Prettier, Next.js production build;
reversible `0007 -> 0008 -> 0009 -> 0007 -> head`; and clean Alembic drift.

## Next Planned Task: TASK-020

TASK-020 will implement the first auditable long-term memory and continuity
evaluation milestone. TASK-019 now provides seven days of importance-bearing
history, but the current Agent decision path has no persisted memories, embeddings,
hybrid retrieval, bounded memory context, or recall/privacy evaluation.

Before implementation, TASK-020 requires a dated ADR and executable, Gray
Harbor-shaped comparison of PostgreSQL/pgvector exact and approximate search,
PostgreSQL lexical search, dedicated vector stores, embedding options, memory
frameworks, ranking/reranking methods, and evaluation tools. The planned slice
includes typed episodic/semantic/emotional/Oracle memories, immutable provenance,
asynchronous versioned embeddings, hard owner/world/time filtering, auditable
hybrid scoring, lexical fallback, bounded prompt assembly, decision freshness,
consolidation, replay/UI, and a fixed Day-1-through-Day-7 continuity corpus with
zero forbidden-memory exposure.

Production push/email, free world creation, automatic personality or relationship
mutation, and a dedicated vector service are not preselected. TASK-021 will be
chosen from measured memory-aware playtest, recall, executability, return, privacy,
latency, and cost evidence.

## TASK-020 Foundation Update

ADR-013 selects PostgreSQL as canonical memory/audit storage, structured plus
lexical retrieval as the outage-safe baseline, exact cosine search as the vector
correctness baseline, and small internal writer/retriever ports. Approximate search
remains disabled until its owner-filtered recall gate passes.

Strict episodic, semantic, emotional, Oracle, and stage-summary contracts now
enforce bounded text, time order, finite vectors, and same-owner/same-world
provenance. Their deterministic JSON Schemas are exported. Migration
`20260728_0010` adds normalized immutable memory/source records, revisioned
embeddings, fenced embedding jobs, retrieval runs, and per-candidate score traces.
The migration passes `0009 -> 0010 -> 0009 -> 0010` and Alembic drift.

Pure policies implement versioned importance admission, deterministic offline fake
embeddings, pre-ranking owner/world/time/type filters, transparent weighted hybrid
scores, stable tie-breaking, whole-record context budgets, diversity exclusions,
lexical fallback, and a memory-aware freshness watermark. The initial
`gray-harbor-memory-eval` 1.0.0 corpus declares required and forbidden memories for
Lin, Chen, and Zhou. Backend regression is 181 passed and 21 opt-in infrastructure
tests skipped.

TASK-020's completed source-to-memory runtime pipeline admits
episodic, semantic, emotional, and Oracle projections exactly once; a fenced
two-worker deterministic embedding path, hybrid/lexical retrieval traces, bounded
stage consolidation, owner APIs, offline evaluation API, and the first frontend
memory/evaluation surface are implemented. TASK-016 prompts carry selected memory
context and reject a proposal when either its Observation or memory watermark
changes after inference.

PostgreSQL integration proves 34 admitted memories from the current 226
owner-visible Observation records, zero new records on repeat projection, 34
unique embeddings across two workers, owner-isolated retrieval, and idempotent
consolidation without raw-memory deletion. Targeted memory plus decision recovery
passes 12 tests; the default backend suite passes 182 with 23 infrastructure tests
skipped. Frontend passes 34 tests, typecheck, lint, format, and production build.

Embedding provider calls now execute after the claim transaction closes.
Timeout/rate-limit/unavailable failures classify as transient with bounded
deterministic retry; invalid/permanent failures dead-letter, and stale worker
results must still match owner and fencing token. A PostgreSQL test opens a second
`FOR UPDATE` session during the provider callback, proving the provider runs
without retaining the embedding-job lock. Retrieval continues in
`lexical_structured_fallback` mode during the outage.

Observer replay decisions now expose only retrieval ID/mode, selected memory IDs,
bounded character use, and the context watermark; they do not expose vectors, raw
prompts, or provider payloads. The Replay Inspector renders that bounded decision
memory context.

TASK-020 is complete. The versioned corpus now executes the production ranking and
packing code in both hybrid and embedding-outage fallback modes instead of
returning prewritten result rows. Both modes achieve required recall@k 1.0 and
zero forbidden exposure on all three fixed cases. The owner UI shows every latest
candidate's rank, selected/excluded state, total/lexical/semantic score, retrieval
mode, and character budget.

Oracle memories link the delivered advice Observation and Oracle window, plus the
subsequent decision action and generated authoritative outcome when available.
Replay exposes bounded retrieval metadata without vectors, raw prompts, or
provider payloads.

The TASK-019 reset-generation scan now includes every persisted
`scenario-gN-*` ActionIntent key, fixing repeat runs that previously replayed a
stale test action. The seven-day integration suite passes twice consecutively, and
the complete infrastructure-enabled backend suite passes 212 tests on the reused
PostgreSQL database.

The current PostgreSQL image reports the `vector` extension unavailable.
ADR-013 therefore keeps approximate pgvector search disabled and uses the selected
exact deterministic vector plus structured/lexical baseline. This is an explicit
deployment limitation, not silent fallback; extension activation remains
conditional on a future image providing pgvector and filtered recall@12 >= 0.99.

Final gates: 212 infrastructure-enabled backend tests; 34 frontend tests; Ruff,
Ruff format, mypy, schema export, TypeScript, ESLint, Prettier, Next.js production
build, reversible `0009 -> 0010 -> 0009 -> 0010`, and clean Alembic drift.

## Next Planned Task: TASK-021

TASK-021 is planned as **Auditable Identity, Relationship, and Oracle-Trust
Evolution**. The choice follows TASK-020's evidence-based branch: memory recall,
privacy, provenance, and fallback gates now pass, but traits and relationships
remain static and recalled experience has no bounded, versioned long-term effect
on behavior.

The task requires research of maintained open-source personality/role-continuity
evaluation, affect/appraisal, graph/relationship, policy, workflow, and evaluation
libraries before ADR-014 selects an architecture. It preserves immutable identity
baselines and World Engine authority; model output may only propose evidence-linked
deltas that code validates for ownership, time, caps, cooldowns, invariants,
freshness, and safety.

The vertical slice adds asymmetric Agent relationships, non-mechanical Oracle
reply/silence/advice/outcome assessment, exactly-once reflection, decision
freshness, causal replay, owner-safe APIs/UI, and a fixed 30-plus-decision Gray
Harbor corpus. Required gates include zero unsupported committed mutations, zero
forbidden evidence exposure, preserved core personality, calibrated Oracle
obedience, bounded dependence, deterministic fallback, and restart/two-worker
proof. Notifications and free world creation remain deferred until this defining
character-continuity risk is validated.

## TASK-021 Completion

TASK-021 is complete. ADR-014 selects immutable authored identity baselines,
bounded derived overlays, PostgreSQL directional edges, repository-native
Pydantic/pure-function policy, and the existing fenced-job architecture. Model
output remains untrusted; the completed vertical slice uses deterministic fallback
interpretation and code-owned owner/world/time/freshness/range/cap checks.

Migration `20260728_0011` adds baselines, identity and relationship histories,
reflection jobs, per-dimension decisions, and evidence links. It passes
`0010 -> 0011 -> 0010 -> 0011` and clean Alembic drift. Scenario reset removes
all derived evolution rows in dependency-safe order while preserving authored
world history.

TASK-020 memories now drive exactly-once reflection. Identity changes require two
independent evidence keys, cap at 0.08 per event and 0.30 cumulatively.
Relationship updates are directional, cap at 0.15 per event and 0.30 per world
day, with dependence capped at 0.45. Low-urgency silence causes no mechanical
trust loss; advice quality, independent choice, material outcome, luck, urgency,
contact possibility, and value conflict remain separate inputs.

Agent decisions persist and hash the exact identity version and relevant
relationship versions. A relevant projection update changes the decision input
watermark and triggers the existing stale-input rejection; replay and the owner
UI display the historical selected versions without exposing raw prompts,
provider payloads, vectors, or hidden reasoning.

The project-owned `gray-harbor-evolution-eval:1.0.0` corpus reports zero
unsupported commits, forbidden exposure, routine drift, and directionality
errors; all three L3 Agents have 30 deterministic later decisions. Oracle trials
include follow, reject, and partial-follow classes, and maximum dependence remains
0.45. Static consistency is 0.866667 and bounded evolved consistency is 0.955556.

Final gates: 230 infrastructure-enabled backend tests; 35 frontend tests; Ruff,
Ruff format, strict mypy, schema export, TypeScript, ESLint, Prettier, Next.js
production build, reversible migration, and clean Alembic drift.

TASK-021's deterministic evidence does not yet justify unrestricted external
notifications or free world creation. The next task must first build and test the
conservative in-site/offline return loop; broader dialogue remains a later branch
if playtests find stored relationship changes credible but insufficiently legible.

## Next Planned Task: TASK-022

TASK-022 is planned as **Instrumented Offline Return Loop, Safe Notifications,
and Narrative Continuity**. The 41-page product plan was reread page by page
against TASK-021's completion evidence. The largest remaining MVP risk is whether
a player returning to an autonomously advanced world can understand what mattered
and continue following an uncontrollable Agent without noisy, privacy-leaking,
guilt-based, or dependence-amplifying notifications.

The task completes the missing Stage-1 deliverables: an owner-scoped in-site
inbox, versioned offline intervals and causal summaries, preferences/quiet
hours/caps/aggregation, replay and cost/debug surfaces, privacy-minimized internal
playtest instrumentation, and optional Web Push that stays disabled until
explicit opt-in, security, copy-safety, and real-browser gates pass. The full
in-site experience must work when push is unsupported, denied, revoked, or down.

Before implementation, TASK-022 requires a dated ADR and executable research of
Next.js/native PWA approaches, service workers, Web Push libraries/VAPID,
PostgreSQL/Redis/Temporal delivery, deterministic versus model-assisted summaries,
anti-manipulation policy, privacy-safe analytics, browser automation, and human
comprehension/safety evaluation. Free world creation remains deferred until the
fixed Gray Harbor return loop produces credible player evidence rather than only
deterministic system metrics.

## TASK-022 Foundation Update

ADR-015 selects a repository-owned deterministic causal compiler, conservative
code-owned notification policy, the existing PostgreSQL fenced/outbox architecture
for future durable delivery, native App Router manifest, and a minimal
same-origin service worker. No new production dependency was introduced.

The implemented policy preserves objective/observed/believed/decided/outcome/
memory/relationship/unknown distinctions; validates owner, world, occurrence and
visibility bounds; hashes exact source versions; rejects coercive/fake-urgency
copy in English and Chinese; and enforces follow scope, channel consent, daily
caps, pause, expiry, timezone/DST quiet deferral, and no-push defaults.

An owner-scoped no-store demo endpoint and accessible return panel show one
source-linked fictional summary item, inclusion reasons, and zero-provider-call
debug data. The native manifest builds successfully. The service worker imports
nothing, uses redacted lock-screen copy and a fixed same-origin route, and remains
disabled by a kill switch. Minimized instrumentation accepts only declared event
codes behind caller identity and CSRF checks.

Current deterministic gates: backend 215 passed and 25 opt-in infrastructure
tests skipped; Ruff, formatting and strict mypy pass. Frontend 35 tests,
TypeScript, ESLint, Prettier, and production build pass.

Migration `20260728_0012` now adds normalized versioned notification preferences,
offline intervals, summaries, immutable source claims, inbox lifecycle, and
allowlisted playtest events. The durable projection uses stable logical keys and
PostgreSQL uniqueness, survives repeat calls with exactly one inbox item and four
source claims, isolates owner mutations, makes repeated read transitions no-ops,
and deduplicates playtest events by idempotency key. Scenario reset deletes every
new row in dependency order.

The real database passes `0011 -> 0012 -> 0011 -> 0012` and clean Alembic drift.
The complete infrastructure-enabled backend suite passes 243 tests. Frontend
still passes 35 tests, TypeScript, ESLint, Prettier, and production build; it now
registers the repository-owned worker and exposes browser permission only behind
an explicit gesture, plus durable read/dismiss controls.

TASK-022 remains in progress rather than being declared complete. Subscription
secret storage/provider delivery and revoke fencing, HTTPS/VAPID real-browser Web
Push tests, and a consented human playtest have not been executed. Push stays
disabled, no human metrics are fabricated, and TASK-023 expansion remains
unselected.

## TASK-022 Browser Verification Update

Playwright 1.62.0 and `pywebpush` 2.3.0 are now selected and installed after
ADR-015 research. Downloading Playwright-managed Chromium/Firefox timed out twice,
so the reproducible browser configuration uses the installed stable Google Chrome
channel without weakening assertions. Two real-browser tests pass: the complete
no-push causal summary renders with zero provider calls and the safe service
worker reaches ready state; notification permission remains `default` without an
automatic request and the only permission entry is a visible gesture control.

The browser suite uses a fixed intercepted API fixture because Docker became
unavailable later in the session; database behavior remains separately evidenced
by the earlier 243-test infrastructure run and real return-loop integration test.
This is not evidence of live provider delivery. A live subscription endpoint,
VAPID send, revoke/expiry receipt matrix and multi-browser coverage remain open.

## TASK-022 Completion

TASK-022 is complete with an explicitly inconclusive expansion result. One
consented internal participant completed the minimized causal-summary condition.
No name, raw free text, IP, user agent, or browser fingerprint was retained.

The participant answered all five causal-comprehension questions correctly
(100%), identified the action as based on character knowledge and judgment,
wished to continue following Chen Mo, and did not feel prompted or blamed.
Clarity and usefulness were each 3/5 and fiction framing was 4/5. The participant
initially entered pressure and anxiety as 4/5 while rating the fictional
character's environment rather than the effect on the participant. After the
question scope was clarified, both participant-experienced ratings were corrected
to 1/5. The original values remain documented as invalidated rather than silently
overwritten. With n=1, no chronological-control participant, and no confidence
interval of practical value, the result is directional only and cannot establish
an interest improvement.

All deterministic privacy/provenance/copy/idempotency gates and the complete
no-push experience pass. External Push is optional and remains disabled because
live VAPID/provider/revoke/expiry and multi-browser evidence is incomplete.
No TASK-023 feature-expansion branch is justified yet. Safety and comprehension
pass directionally, so the next evidence step is a larger controlled return-loop
playtest with unambiguous participant-directed rating wording. Creation, dialogue,
action, and delivery expansion remain deferred; the no-push fallback remains.

## Next Planned Task: TASK-023

TASK-023 is planned as **Controlled Fixed-World Product Validation and Stage-2
Expansion Gate**. The 41-page product and technical implementation plan was read
page by page on 2026-07-30. Page 36 places world/character creation, event
authoring, promotion, and conflict detection in Stage 2, while page 39 explicitly
requires proving that fixed-world characters are worth following before building
a large general editor.

TASK-022 is directionally positive but cannot satisfy that gate with one
participant and no chronological control. TASK-023 therefore builds a
preregistered, privacy-minimized, reproducible multi-session study using
counterbalanced causal-summary and chronological conditions over matched Gray
Harbor intervals. It adds durable consent, opaque assignment, exact exposure
versions, bounded responses and correction audit, withdrawal/deletion,
participant-directed safety wording, a focused accessible playtest shell,
small-sample analysis, and concrete nonfunctional probes for creation, promotion,
dialogue, actions, and delivery demand.

Before design, TASK-023 requires official/upstream research and executable
comparisons of repository-native assignment/analytics versus maintained
experiment and privacy analytics tools; accessible survey systems; statistical
libraries and crossover methods; causal/fallback narrative layouts; accessibility
automation; and local/hosted study deployment. ADR-016 must select the smallest
architecture without session replay, fingerprinting, raw narrative capture, or
engagement optimization.

The target is at least 16 completed participants; fewer than 8 remains directional
and cannot trigger expansion. TASK-023 may finish with a negative or inconclusive
result. TASK-024 will be exactly one evidence-backed branch—creation, promotion,
dialogue, actions, return-loop UX, or delivery—or an explicit decision to defer
expansion.

## TASK-023 Completion

TASK-023 is complete with an explicit `n=0` directional result and
**defer expansion** decision. ADR-016 selects repository
native assignment, coded responses, standard-library analysis, normalized study
records and a focused `/playtest` route. No analytics SDK, replay, fingerprint,
free-text collection, model prose or functional Stage-2 editor was introduced.

The fixed corpus has two matched reject/partial-follow intervals and privacy
decoys. Tests cover stable allocation, exact condition source equality, ambiguous
safety wording rejection, small-cell suppression, low-sample deferral and
retention of low ratings. No participant was enrolled or fabricated, so no human
comprehension, safety, offline-return or demand estimate exists and no TASK-024
expansion branch is justified. Production migration/browser/accessibility gates
The durable boundary now covers frozen consent and questions, opaque access-code
hashes, race-safe deterministic AB/BA assignment, two source-fenced periods,
bounded idempotent responses, append-only corrections, concrete demand probes,
withdrawal/deletion, a default-off enrollment kill switch and a suppressed
admin-only aggregate report.

Migration `20260730_0013` upgraded the real PostgreSQL database from 0012 with
clean Alembic drift. A self-deleting real database flow and two-worker duplicate
enrollment race pass. Final gates: 253 infrastructure-enabled backend tests,
37 frontend tests, Ruff, TypeScript, ESLint, Prettier, Next.js production build,
and one real Chrome narrow-view/calm/no-push test.

No participant was enrolled for product evidence or fabricated. Consequently no
human comprehension, safety, offline-return or demand estimate exists; all
Stage-2 branches remain deferred. Any later study may operate the frozen protocol
but may not retroactively change TASK-023's `n=0` result.
