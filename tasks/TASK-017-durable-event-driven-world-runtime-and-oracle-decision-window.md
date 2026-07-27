# TASK-017: Durable Event-Driven World Runtime, World Clock, and Oracle Decision Window

**Status:** Done
**Planning date:** 2026-07-26  
**Depends on:** TASK-001 through TASK-015; TASK-016 completion gates in section 5  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf` (41 pages)

## 1. Planning Basis

The product plan makes three promises the current system does not prove: the world continues while the player is offline; Agents wake because meaningful events occur rather than continuous polling; and a major decision may wait durably for player revelation, then continue after either reply or timeout, with both reply and silence becoming part of the character's experience.

TASK-013 through TASK-016 established persisted visibility-filtered Observations, authoritative wait/move adjudication, concurrency-safe mutation, and a manually triggered Observation-only model decision. The largest remaining gap in the first technical milestone is durable orchestration across world time, process restarts, player absence, and delayed external input.

## 2. Candidate Comparison

| Candidate | Why not TASK-017 |
| --- | --- |
| Long-term vector memory | Optimizes continuity, but there is no autonomous sequence yet. |
| More actions/dialogue | Adds expression without proving offline continuity or delayed interaction. |
| World creator | The plan says to validate the fixed-world character loop before broad creation tools. |
| Notification/PWA | Needs a trustworthy durable Oracle/runtime source first. |
| Oracle request alone | Cannot safely resume without a durable clock and timeout runtime. |
| Durable runtime + Oracle window | Completes the largest missing part of the first milestone; selected. |

## 3. One-Sentence Acceptance Target

Run Gray Harbor through a deterministic persisted sequence in which a scheduled event wakes Chen, Chen opens one major-decision Oracle window, the world survives API/worker restart while waiting, and either a player reply or deterministic timeout becomes an owner-scoped Observation before Chen independently proposes a server-offered action that is authoritatively adjudicated and visible in one privacy-safe causal replay without duplicate events, model calls, notifications, or actions.

## 4. Required Demo Scenario

1. A persisted scheduled event becomes due at a known world time.
2. The runtime claims and publishes it exactly once through World Engine.
3. Observation Builder determines recipients.
4. Wake policy selects Chen because his new Observation materially affects his plan.
5. A deterministic decision fixture marks the situation major and Oracle-eligible.
6. The system creates one Oracle request with world-time and real-time deadlines.
7. Chen may perform only an explicit safe interim `wait`; this is not the final answer.
8. Reply branch: player advice becomes an `oracle` Observation.
9. Timeout branch: no advice is fabricated; a typed silence Observation records no reply.
10. Chen reloads fresh state and Observations and submits `wait` or adjacent `move` through TASK-016/TASK-015.
11. Replay connects schedule, event, Observations, wake, model assessment, Oracle window, reply/timeout, final decision, action, result, state and recipients.

Both branches are mandatory. Tests advance virtual time and never sleep for deadlines.

## 5. Mandatory TASK-016 Closure Gate

Worker-driven decisions remain disabled until these inherited gaps close:

- atomic expired-lease takeover with fencing tokens;
- crash recovery after persisted model completion without another model call;
- crash recovery after action submission without another action;
- barrier/hook same-key and different-key concurrency tests;
- stale-after-inference rejection;
- leakage and prompt-injection fixtures;
- mocked real-provider refusal/incomplete/rate-limit/timeout tests;
- decision records integrated into observer replay;
- clean migration upgrade/downgrade/check, including existing `location_edges` drift;
- decision frontend state tests and clean production build.

The final report must separate inherited TASK-016 closure from new TASK-017 work.

## 6. Required Preliminary Official/Open-Source Research

Implementation starts with a dated ADR and executable spikes. Compare current versions, licenses, maintenance, Python support, operational footprint, privacy, failure semantics, and removal cost.

### 6.1 Durable orchestration

Compare:

- Temporal Server/Cloud and official Temporal Python SDK;
- PostgreSQL state machines using `FOR UPDATE SKIP LOCKED`, advisory locks and LISTEN/NOTIFY;
- Celery with Redis/RabbitMQ;
- Dramatiq, arq or an equivalent maintained worker;
- APScheduler;
- synchronous API-only orchestration as the no-new-library baseline.

Evaluate durable timers, player signals, workflow/activity retries, at-least-once semantics, deterministic replay/versioning, crash recovery, cancellation, pause/resume/speed change, local CI complexity, history limits, async support and migration cost. Select Temporal only if its timer/signal/replay benefits justify MVP operations. If PostgreSQL is selected, document its ceiling and a concrete Temporal migration seam; do not accidentally build an unbounded custom scheduler.

### 6.2 Clock, claims, messaging and tests

Research SimPy or an equivalent discrete-event design for simulation-time semantics; PostgreSQL/SQLAlchemy row locks, `SKIP LOCKED`, advisory locks and isolation; polling versus LISTEN/NOTIFY, Redis Streams/PubSub, SSE and WebSocket; and Temporal time-skipping versus deterministic fake clocks. Spike a durable timer plus player signal, two workers claiming one item, restart/replay, and virtual-time timeout. No concurrency/timer spike may depend on probabilistic sleep.

### 6.3 Required research output

The ADR must contain a capability/license/maintenance matrix, spike results, selected/rejected architecture, local/production topology, retry/timeout/cancellation/versioning rules, workflow-history privacy analysis, removal plan, and the exact reason Temporal is adopted, deferred behind a port, or rejected.

## 7. Target Architecture

```text
WorldRuntimePort
  -> selected durable adapter
     -> WorldTickOrchestrator
        -> claim due ScheduledWorldEvent
        -> World Engine -> Observation Builder
        -> WakePolicyEvaluator
        -> TASK-016 Agent decision
           -> major-decision policy
           -> OracleDecisionWindow
              -> player signal OR timeout
              -> reply/silence Observation
           -> fresh final decision
           -> TASK-015 Action Service
        -> notification outbox -> replay projection
```

Runtime code coordinates but never authors world facts, action success, recipients or Agent output. World time is domain state, not scattered `datetime.now()`. Histories carry IDs/privacy-safe references, never secrets, hidden facts, raw prompts or chain-of-thought. Every handler is idempotent. FastAPI never hosts an unbounded loop. PostgreSQL remains replay authority. Player reply is Observation, never Action.

## 8. World Clock Contract

Persist world ID, current world time, `stopped|running|paused|faulted`, speed/mode/version, real-time anchor, last advancement, next due reference, runtime generation/fencing token, catch-up limit, failure count and typed failure.

Rules:

- world time never moves backward;
- pause freezes simulation without erasing work;
- speed change is versioned and audited;
- equal-time work has total order `(due_world_time, priority, created_at, id)`;
- catch-up is bounded and resumable;
- OS clock changes cannot reorder persisted work;
- stale runtime generations fail fencing;
- only World Engine produces state/event mutations.

## 9. Scheduled Event and Wake Contracts

Use a lifecycle such as `scheduled -> due -> claimed -> executing -> published`, with retryable/terminal failure and cancellation. Persist stable schedule/idempotency IDs, due world time, priority, typed parameters, precondition version, claim/fencing token, attempts, linked event/state IDs, correlation and typed failure. TASK-017 supports one fixed Gray Harbor hard event, not general natural-language compilation or cron.

`WakePolicyEvaluator` is pure code. Required reasons are relevant new Observation, Oracle reply, Oracle timeout, and action/plan completion/failure. One causal watermark creates at most one active wake; duplicates coalesce; unrelated Observations do not wake Chen; budgets bound wake/model frequency; wake never bypasses TASK-016 isolation.

## 10. Major-Decision and Oracle Eligibility

An unrestricted model boolean cannot open player contact. The model may propose bounded assessment fields; deterministic server policy validates reversibility/risk tags, Agent Oracle policy, cooldown, existing requests, contact availability and budget. Persist bounded rationale, server-provided risk enums, `major_decision`/`seek_oracle` proposals, policy result/rejection code, and prompt/model audit references. Allow only one open request per world/Agent/decision correlation.

## 11. Oracle Decision Window

Lifecycle:

```text
requested -> waiting
waiting -> replied -> delivered -> resumed -> completed
waiting -> timed_out -> silence_delivered -> resumed -> completed
waiting -> cancelled
```

Requirements:

- explicit precedence between world-time and real-time deadlines;
- reply endpoint resolves Agent/world/request from server state;
- first valid reply wins; duplicates replay or return a stable closed code;
- reply/timeout race has one transactional winner;
- bounded player text is stored as player content, not truth;
- Observation Builder is the only delivery boundary;
- timeout creates no fake player content;
- silence Observation permits bounded interpretation but does not mechanically change trust;
- cancellation, pause, inactive/dead Agent and supersession are explicit;
- API/worker restart loses neither timer nor signal.

While waiting, optional interim `wait` has its own action key and lifecycle and is visibly separate from the final decision. Model failure or timeout never silently becomes a successful final wait.

## 12. Persistence and Constraints

Add reversible normalized persistence for world runtime state, scheduled events/execution attempts, wake claims, decision assessments, Oracle windows/workflow references and notification outbox. Enforce where possible:

- one active runtime generation;
- unique event publication;
- unique active wake key;
- one open Oracle window per decision;
- one reply/timeout winner;
- one final continuation/action;
- valid monotonic versions/lifecycle transitions.

JSONB round-trips through strict Pydantic models. Never store credentials, headers, raw reasoning, unrestricted prompts or unrelated private data.

## 13. Explicit Workflow

1. Start/resume Gray Harbor under a feature flag.
2. Select the next persisted due item from authoritative world time.
3. Claim with fencing and close the transaction.
4. Revalidate generation, schedule, world version and preconditions.
5. Publish through World Engine transaction.
6. Persist event/state and recipient Observations atomically.
7. Create coalesced wake records.
8. Claim Chen's wake and call completed TASK-016 without world lock.
9. Persist/validate major-decision and Oracle eligibility.
10. If ineligible, submit normally.
11. If eligible, create Oracle window, optional interim wait and outbox notification.
12. Wait durably for reply, either deadline, cancellation or invalidation.
13. Atomically choose one terminal window transition.
14. Convert reply or silence through Observation Builder.
15. Reload fresh Agent state/Observations/affordances and decide again.
16. Submit through Validator/World Engine and finalize causal links.
17. Checkpoint runtime and continue only within event/cost bounds.

## 14. API Contract

Candidate fixed-demo endpoints:

```http
POST /demo/worlds/gray-harbor/runtime/start
POST /demo/worlds/gray-harbor/runtime/pause
POST /demo/worlds/gray-harbor/runtime/resume
POST /demo/worlds/gray-harbor/runtime/advance
GET  /demo/worlds/gray-harbor/runtime
GET  /demo/worlds/gray-harbor/oracle-requests
POST /demo/worlds/gray-harbor/oracle-requests/{request_id}/responses
GET  /demo/worlds/gray-harbor/notifications
```

Runtime controls and inbox are observer/dev boundaries. Agent reads cannot list other Agents' windows. Clients cannot choose provider, prompt, actor, deadline outcome, versions, recipients, result or world-time mutation. `advance` is a bounded deterministic dev/test control. All commands are idempotent and all expected failures use JSON.

Stable codes include `WORLD_RUNTIME_DISABLED`, `WORLD_RUNTIME_ALREADY_RUNNING`, `WORLD_RUNTIME_GENERATION_CONFLICT`, `WORLD_RUNTIME_PAUSED`, `WORLD_ADVANCE_LIMIT_EXCEEDED`, `SCHEDULED_EVENT_CLAIM_CONFLICT`, `AGENT_WAKE_IN_PROGRESS`, `ORACLE_NOT_ELIGIBLE`, `ORACLE_REQUEST_ALREADY_OPEN`, `ORACLE_WINDOW_CLOSED`, `ORACLE_REPLY_ALREADY_ACCEPTED`, `ORACLE_REPLY_TIMEOUT_RACE_LOST`, and `WORKFLOW_TEMPORARILY_UNAVAILABLE`. Existing model/action codes remain distinct.

## 15. Frontend Vertical Slice

Add:

1. **World Runtime Control** — state, world time, speed/mode, generation, next due event, bounded advance, catch-up/failure status.
2. **Oracle Inbox** — Chen's bounded context, both deadlines, waiting/replied/timed-out/resumed state, validated reply, duplicate/late behavior, and clear advice-not-command language.
3. **Unified Causal Replay** — objective event, recipient Observation, wake, model assessment, server eligibility, reply/silence, final proposal, authoritative result/state/Observations.

Live updates may use the selected transport, but reconnect always refetches authoritative cursor/read APIs.

## 16. Notification Outbox

Use a PostgreSQL transactional outbox for Oracle opened, Oracle timed out, final decision completed and runtime faulted. Records require logical dispatch keys, attempts, status and cursor reads. Transport may be in-process for this slice; browser push/email are out of scope. Outbox is delivery intent, not proof of display.

## 17. Configuration and Safety

Document runtime mode/feature flag, adapter, worker identity/concurrency, event/catch-up limits, speed defaults, leases/heartbeats, deadline precedence, reply limit, wake/model/token budgets, retry/backoff, history retention, notification transport and test virtual-time controls. Defaults start with runtime disabled. Health checks never advance time, start work, notify or call models. Logs redact replies and Agent-private payloads.

## 18. Deterministic and Adversarial Fixtures

Cover:

- publish once and stable equal-time order;
- pause/resume/speed/downtime catch-up and catch-up bound;
- two-worker claim race;
- crash before/after event publication;
- duplicate wake coalescing and unrelated Observation suppression;
- Oracle eligible/ineligible and duplicate-window attempts;
- reply just before timeout and timeout just before reply;
- duplicate/late replies;
- restart while waiting;
- pause/inactive Agent while waiting;
- reply prompt injection/unsupported action request;
- timeout silence without fabricated advice;
- stale/unavailable pre-window action after fresh reload;
- model failure after reply with zero final mutation;
- outbox retry without duplicate logical notification;
- decoy global/other-Agent secrets absent throughout.

No test may use probabilistic sleep.

## 19. Backend and Frontend Tests

Backend tests cover strict contracts/schema hashes, migrations/indexes/constraints/JSONB, clock math/order, fencing/takeover/stale worker, at-least-once execution, pause/resume/catch-up, restart/replay compatibility, reply-timeout race, reply idempotency, Observation isolation, no DB/world lock during model calls, fresh final state, accepted/rejected final actions, outbox recovery, replay completeness, import boundaries and full TASK-001–016 regression. Temporal selection additionally requires saved-history replay and time-skipping; PostgreSQL selection requires multi-process/container crash checkpoints.

Frontend tests cover runtime states/commands, world time/next event, all Oracle inbox states, reply contract and duplicate/late errors, advice/proposal/result separation, silence display, reconnect recovery, replay ordering, notification projection, privacy-negative assertions and all existing surfaces.

## 20. Observability and Cost Controls

Persist/expose observer-safe due-event claim latency/attempts, wake reason/coalescing, Oracle duration/outcome, model attempts/latency/tokens/nullable cost, catch-up backlog, outbox attempts and typed runtime failures. Hard-limit events per activation, wakes per interval, concurrent model calls, retries and daily budget. Exhaustion pauses/defers with an audited code and never invents an action result.

## 21. Allowed Changes

- world clock/runtime contracts and one researched adapter;
- scheduled-event, wake, Oracle-window, workflow-reference and outbox persistence;
- fixed Gray Harbor event/wake/Oracle scenario;
- section 5 TASK-016 recovery/replay closure;
- runtime/Oracle/notification APIs;
- runtime controls, Oracle inbox and unified replay UI;
- migrations, tests, worker/container config, ADRs, docs and runbook.

## 22. Explicitly Out of Scope / Forbidden

- polling every Agent;
- long simulation in FastAPI handlers or `BackgroundTasks`;
- general event compiler/editor, arbitrary conditions or recurring cron;
- broad actions, combat, trade or full dialogue;
- vector memory/pgvector/biography compression;
- direct relationship/emotion/goal mutation without an authority contract;
- production browser push/email;
- world creator, promotion or multiple-world scheduling;
- Redis/workflow history/transport as truth;
- model-authored deadlines, recipients, state, results or workflow transitions;
- raw prompts/reasoning/secrets in workflow history;
- infinite retries, unbounded catch-up or silent fallback;
- Kubernetes/production HA.

## 23. Required Implementation Sequence

1. Complete research ADR and spikes.
2. Select runtime architecture and update ADR-007/boundaries.
3. Close every section 5 TASK-016 gate.
4. Write failing virtual-time, race, restart, privacy and replay tests.
5. Define clock, schedule, wake, Oracle and outbox contracts.
6. Add reversible migrations/constraints.
7. Implement pure time/order/catch-up logic.
8. Implement claims/fencing/exactly-once logical publication.
9. Implement selected adapter behind `WorldRuntimePort`.
10. Publish one fixed event through World Engine/Observation Builder.
11. Implement wake/coalescing/budgets.
12. Add bounded major-decision proposal and server Oracle policy.
13. Implement reply/timeout/cancellation races.
14. Deliver reply/silence and make fresh final decision.
15. Link final action/state/Observations and replay.
16. Add outbox and recoverable updates.
17. Add frontend surfaces.
18. Run restart/crash/concurrency/virtual-time/leakage/regression suites.
19. Record deterministic reply and timeout end-to-end smokes.
20. Optionally run explicitly authorized budget-capped live model smoke.
21. Synchronize task/status/architecture/development/runbook docs.

## 24. Verification Gates

Backend:

```powershell
$env:RUN_INFRA_TESTS='1'
$env:RUN_WORKFLOW_TESTS='1'
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy .
python scripts/export_schemas.py --check
python -m alembic check
python -m alembic downgrade <previous_revision>
python -m alembic upgrade head
```

Frontend:

```powershell
npm run generate:domain-types
npm test
npm run typecheck
npm run lint
npm run format:check
npm run build
```

Operational: clean database, seed, start runtime, advance to event, restart worker while waiting, complete reply branch, reset/reseed and complete timeout branch, retry same commands, inspect DB/UI replay, and prove no paid call unless explicitly enabled.

## 25. Acceptance Criteria

TASK-017 is complete only when:

- research/ADR justifies the runtime with working spikes;
- all TASK-016 closure gates pass before automation;
- runtime defaults disabled;
- fixed event is ordered, claimed and published exactly once;
- world time is monotonic, pausable, resumable, speed-aware and virtual-time testable;
- catch-up is bounded/auditable/resumable;
- stale generations cannot commit;
- only affected Agents wake and duplicates coalesce;
- no periodic all-Agent model polling exists;
- Oracle eligibility uses server policy;
- one Oracle window survives restart;
- reply/timeout has one transactional winner;
- reply becomes owner-scoped Observation, never command;
- timeout creates explicit silence without fabricated advice;
- final decision reloads fresh state/Observations/affordances;
- final action uses Validator/World Engine;
- failures never silently create success/mutation;
- the entire schedule-to-result chain is replayable;
- histories/logs/APIs/UI preserve ADR-002 privacy;
- outbox intent is atomic/idempotent/recoverable;
- crash, race, restart and replay-version tests pass;
- deterministic reply and timeout smokes are recorded;
- all backend/frontend/migration/regression gates pass;
- docs/runbook are synchronized.

## 26. Completion Report

Report selected/rejected orchestration choices and versions/licenses; files/migrations/topology; TASK-016 closure; clock/fencing/idempotency invariants; two-worker race; restart-while-waiting; both reply-timeout winners; complete reply and timeout replay chains; zero-duplicate proof; leakage evidence; quality-gate output; optional live cost; remaining risks and evidence-based TASK-018 recommendation.

## 27. Follow-On Decision

Do not preselect TASK-018. Choose memory if autonomous sequences expose recall failures; dialogue/channels if social propagation is too shallow; notification/PWA if player return is the bottleneck; richer authoritative actions if executability is constrained by wait/move; world creation only after the fixed-world loop is engaging and stable.
