# TASK-019: Seven-Day Gray Harbor Plans, Resources, and Authoritative Consequences

**Status:** Planned  
**Planning date:** 2026-07-27  
**Depends on:** TASK-001 through TASK-018  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf`
（41 页，本次规划已完整阅读）

## 1. Why This Task Is Next

TASK-018 closes the product plan's first technical milestone: a fixed objective fact
can propagate through different channels, create divergent local beliefs, wake
multiple Agents, and terminate a bounded correction exchange without sharing global
truth. The project can now explain what characters know and why.

The remaining product risk is no longer information flow. It is whether those
beliefs lead to a sustained, consequential, and internally playable world rather
than repeated `wait`/`move`/message demonstrations.

The product plan's Stage 1 vertical slice requires a seven-day lockdown town,
approximately 30 residents, three special Agents, world-time progression, offline
operation, character pages, notifications, replay, and cost visibility. The current
Gray Harbor has four locations, three special Agents plus one witness, one short
propagation scenario, and primarily `wait`, `move`, and fixed dialogue behavior.
It lacks:

- durable character plans and plan completion/failure;
- food, medicine, shelter capacity, access rights, and other contested resources;
- authoritative acquire/use/transfer/help/queue/escape action consequences;
- 30-resident tiered simulation without 30 continuously running LLM Agents;
- a multi-day causal arc with resource depletion and irreversible choices;
- stable seeded adjudication for uncertain attempts;
- evidence that personality, beliefs, goals, plans, and executable actions remain
  coherent across many wakes;
- a playable Stage 1 start/pause/advance/replay loop rather than isolated feature
  panels.

Long-term memory is premature until the simulation produces enough important
experiences to retrieve. Notifications cannot prove return value until there is a
multi-day story worth returning to. World creation would generalize a loop that has
not yet demonstrated sustained consequences. Therefore TASK-019 should build one
deep fixed-world vertical slice, not another broad platform layer.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Seven-day Gray Harbor with plans, resources, tiered residents, and richer authoritative actions | **Selected.** Converts the proven information loop into a sustained playable fate-and-consequence loop and completes the largest missing part of Stage 1. |
| Long-term memory / pgvector | Deferred. TASK-019 must first create a sufficiently long, importance-labeled history and measure recall failures. |
| Notification/PWA/offline summary | Deferred to the next evidence-based decision. Existing outbox is enough to record important moments during this task; delivery UX is not the current core risk. |
| Free world creator/event editor | Deferred according to the product plan: prove the fixed Gray Harbor loop is engaging before generalizing it. |
| General population multi-Agent simulation | Rejected. Thirty LLM Agents would violate cost and event-driven principles. TASK-019 uses simulation tiers and only three special Agents. |
| Oracle relationship/personality evolution | Deferred as a primary scope. This task may record typed inputs for later change, but must not mechanically rewrite personality or player trust. |

## 3. One-Sentence Acceptance Target

Advance a resettable Gray Harbor deterministically through seven world days with
30 persisted residents, three special Agents, finite plans, contested food and
medicine, at least five server-authoritative action types, hard and conditional
events, resource and capacity invariants, meaningful success/failure/death-or-
survival consequences, bounded selective Agent wakes, and a replay/UI that proves
why every important outcome occurred without leaking hidden information or
exceeding recorded model/cost budgets.

## 4. Required Fixed Seven-Day Scenario

The acceptance fixture must be authored as versioned scenario data, not scattered
test conditionals.

1. **Day 1 — illness detected:** clinic medicine and beds are limited; Lin receives
   direct evidence and begins a triage plan.
2. **Day 2 — panic buying:** store food/water stock falls; Chen must choose between
   rationing, ordinary sale, reserving supplies, or helping a specific household.
3. **Day 3 — lockdown:** the north gate closes through the TASK-018 propagation
   channels; Zhou receives an official duty plan while Chen receives a distorted
   version.
4. **Day 4 — plan collision:** a clinic supply plan, an official checkpoint plan,
   and a household survival plan compete for time, access, and transport.
5. **Day 5 — food shipment stops:** a hard event removes expected replenishment;
   at least one current plan becomes blocked and causes a typed wake.
6. **Day 6 — shelter/clinic pressure:** capacity or medicine is insufficient.
   Characters may queue, transfer supplies, help, refuse, abandon a plan, or attempt
   a risky route. Outcomes must follow authoritative rules.
7. **Day 7 — ten rescue places:** eligibility, location, health, relationships, and
   prior actions create a consequential choice. At least two valid deterministic
   branches must exist, and the acceptance seed chooses one reproducibly.

The scenario must demonstrate:

- at least one completed plan;
- at least one blocked or abandoned plan;
- at least one accepted resource transfer;
- at least one rejected action with a stable failure code;
- at least one uncertain action resolved by versioned seeded adjudication;
- at least one action that helps another resident at a real cost;
- at least one irreversible consequence such as rescue allocation, permanent
  health degradation, disappearance, or death;
- different final beliefs, resources, locations, and plan states for Lin, Zhou,
  and Chen;
- a causal chain from information to belief to goal/plan to action to world event
  to later consequence.

Tests advance virtual time and never sleep.

## 5. Mandatory Preliminary Official/Open-Source Research

Implementation begins with a dated ADR and executable spikes. Record versions
checked on the implementation date, license, maintenance activity, Python 3.12+
support, deterministic-test support, persistence/restart semantics, operational
footprint, privacy impact, failure modes, and removal cost. No production
dependency may be added before the ADR evidence.

### 5.1 Discrete-event simulation and scheduling

Compare:

- extending the current dependency-free `WorldRuntimePort`;
- SimPy;
- Mesa's time/event schedulers;
- salabim or another maintained Python discrete-event simulator;
- PostgreSQL scheduled-work rows;
- Temporal only as a durable-workflow baseline.

Evaluate virtual time, stable equal-time ordering, pause/resume, crash recovery,
transaction integration, deterministic seeds, conditional events, 30–50 resident
performance, state inspection, replay linkage, and whether the library would become
a second authority beside PostgreSQL.

The current PostgreSQL runtime remains the default unless a spike proves that a
library materially improves correctness without taking ownership of state.

### 5.2 Rules, plans, and finite-state workflows

Compare:

- typed Python policy objects and explicit FSMs;
- `transitions`;
- `python-statemachine`;
- durable_rules;
- business-rules or another maintained JSON rules engine;
- JSONLogic implementations;
- behavior trees or GOAP libraries only as planning baselines.

Evaluate rule versioning, static validation, explainability, arbitrary-code risk,
serialization, deterministic replay, stale-state handling, authoring ergonomics,
schema compatibility, and whether rules can bypass Action Validator or World
Engine. General-purpose executable user rules are forbidden in this task.

### 5.3 Resource, inventory, and capacity modeling

Compare normalized balance/ledger tables, event-sourced inventory ledgers,
double-entry accounting ideas, JSONB snapshots, SQL constraints/triggers, and
existing maintained inventory/economic simulation libraries.

Evaluate non-negative stock, conservation, reservations, concurrent transfers,
expiry/spoilage, capacity, units, rollback, audit history, idempotency, and
performance. PostgreSQL constraints plus an append-only resource ledger are the
expected baseline.

### 5.4 Deterministic uncertainty and adjudication

Compare:

- fully deterministic threshold rules;
- Python `random.Random` with stored seed/state;
- NumPy `Generator`/PCG64;
- `randomgen`;
- PostgreSQL random functions as a rejected or baseline option;
- commit-reveal/verifiable-random approaches only if they improve replay trust.

Define precisely where randomness is allowed. The model may describe intent or
social interpretation but cannot choose a random result. Persist algorithm,
version, seed derivation inputs, roll, modifiers, probability/threshold, and final
outcome. Never use wall clock, process hash randomization, unordered collections,
or unrecorded global RNG state.

### 5.5 Tiered population and background simulation

Compare:

- deterministic schedule templates;
- Mesa AgentSet/population facilities;
- ECS-style entity processing;
- batch SQL state transitions;
- LLM-driven background residents as a rejected cost baseline.

Evaluate L0/L1/L2/L3 boundaries from the product plan, promotion seams, encounter
generation, wake suppression, privacy, aggregate resource consumption, replay
granularity, and cost. Only the three existing special characters are L3 in the
acceptance scenario.

### 5.6 Planning and behavioral evaluation

Compare deterministic pytest/replay scoring with optional DeepEval, Promptfoo,
Langfuse, Phoenix, and OpenTelemetry metrics. Research maintained planning
benchmarks or lightweight evaluation methods for:

- action executability;
- goal continuity;
- plan completion/blockage;
- personality consistency;
- causal reference accuracy;
- knowledge leakage;
- loop/repetition rate;
- resource invariant violations;
- model calls and token cost per simulated day.

Paid/live evaluation remains opt-in and cannot be required for CI.

### 5.7 Required executable research spikes

The ADR must link executable evidence for:

1. stable equal-time order for 100 scheduled plan/resource operations;
2. two workers competing for the same resource, with stock never below zero;
3. crash before and after ledger/result commit, with exact-once recovery;
4. conditional Day-5 event firing once when its predicate becomes true;
5. a plan completing, blocking, replanning, and terminating without a loop;
6. the same stored seed producing the same uncertain outcome after restart;
7. 30 residents advancing seven days with only bounded L3 model calls;
8. removal seams for every selected library.

## 6. Authority and Architecture

```text
WorldRuntimePort advances virtual time
  -> due hard/conditional events and plan steps
     -> World Engine publishes objective WorldEvent/WorldFact
        -> TASK-018 propagation/Observation/belief/wake
           -> Agent decision receives goals + relevant plan/resource Observations
              -> server-offered Action affordances
                 -> ActionIntent
                    -> Action Validator
                       -> World Engine adjudication
                          -> atomic state + resource ledger + ActionResult + events
                             -> later plan/event consequences and replay
```

Authority rules:

- World Engine alone mutates objective character, resource, capacity, access,
  rescue, health, and world state and creates `ActionResult`.
- Action Validator alone decides whether an attempted action is currently legal.
- Runtime may trigger due work but cannot invent events, plan outcomes, resource
  changes, or random results.
- Agent/model may choose only from server-derived affordances. It cannot invent
  resource IDs, amounts, targets, probability, witnesses, success, or damage.
- Plan Coordinator may propose/advance typed plan steps but cannot commit world
  mutation outside the normal Action lifecycle.
- Observation Builder remains the only creator of Agent input.
- TASK-018 propagation remains the route for non-local information.
- PostgreSQL remains replay authority. Redis, a simulator library, or telemetry may
  accelerate work but cannot become truth.
- Any authority change requires an ADR and architecture-handbook update before
  implementation.

## 7. Domain Contracts

Define strict Pydantic contracts and generate JSON Schema/TypeScript types for
public boundaries. Lifecycle-critical fields must be normalized, not hidden only
inside generic JSONB.

### 7.1 ResourceDefinition and ResourceAccount

Represent stable resource type/version, unit, divisibility, conservation policy,
expiry policy, privacy class, capacity rules, and allowed holder kinds.

An account identifies a world/location/character/organization holder and tracks
authoritative available, reserved, and consumed totals with an optimistic version.
Amounts use bounded integers or fixed precision; binary floating-point inventory
is forbidden.

### 7.2 ResourceLedgerEntry and Reservation

Append-only entries record transfer, consume, produce, reserve, release, expire,
loss, and correction with source action/event, idempotency key, world time,
transaction time, actor, from/to accounts, amount, unit, prior/new versions, and
safe reason code.

Reservations have explicit lifecycle and expiry. A failed action cannot create a
successful ledger entry.

### 7.3 AgentGoal and AgentPlan

Goals record owner, typed objective, priority, status, origin, world-time horizon,
success/failure predicates, version, and privacy class.

Plans contain bounded typed steps and use:

```text
draft -> active -> waiting
              -> blocked -> active | abandoned | failed
              -> completed
draft/active/waiting -> cancelled
```

Persist current step, expected versions, start/deadline, retry/replan count,
blockage code, linked decisions/actions/events, and fencing token. Plans are not
free-form executable code.

### 7.4 ScheduleTemplate and ResidentTier

Represent L0 population aggregates, L1 background residents, L2 relevant
residents, and L3 special Agents. Schedule templates create deterministic due work
and resource demand without model calls during ordinary life.

Promotion to a higher tier is explicitly out of acceptance scope, but persistence
must not make future promotion impossible.

### 7.5 ConditionalWorldEvent

Define a restricted condition AST with allowlisted fields/operators, versioned
evaluation policy, deadline, one-shot/repeat policy, idempotency key, resulting
event specification, and status. Do not evaluate Python, SQL fragments, Jinja,
JavaScript, or player-authored arbitrary expressions.

### 7.6 AdjudicationTrace

For uncertain attempts persist policy/version, seed algorithm/version, seed hash,
bounded modifiers, threshold or probability, roll, decision, and causal IDs.
Agent-facing Observations expose only what the character could perceive; observer
replay may show safe adjudication detail.

## 8. Narrow Action Vocabulary

Add only actions required for the seven-day scenario:

- `acquire_resource` — obtain allowed stock through a location/account;
- `transfer_resource` — give or allocate held stock to an allowed target;
- `consume_resource` — use food, water, or medicine on self/authorized target;
- `help_character` — spend time and optionally reserved resources on a typed need;
- `queue_for_service` — enter a clinic, shelter, or rescue queue;
- `attempt_route` or `attempt_escape` — attempt a server-offered risky route;
- `abandon_plan` — explicitly terminate the actor's current plan;
- existing `wait`, `move`, and communication actions remain.

If research proves two actions can share one safer generalized contract, document
that decision. Do not add combat, arbitrary crafting, unrestricted trade,
persuasion probability, stealing, or generic `custom` execution.

Every affordance fixes:

- allowed action type;
- actor and allowed target;
- resource/account IDs and maximum amount;
- expected world/character/account/plan versions;
- location, access, capability, time, and plan preconditions;
- duration and possible observable consequences;
- adjudication policy ID when uncertain;
- expiry/watermark and idempotency scope.

## 9. Plan Coordinator

- Plans are external durable state, not hidden model chain-of-thought.
- The model may choose a goal/plan template or request one bounded replan, but the
  server validates every step.
- Ordinary plan steps execute without an LLM when preconditions remain valid.
- A plan wake occurs only on new relevant Observation, step completion/failure,
  resource shortage, deadline, encounter, or explicit reflection checkpoint.
- Replanning is capped per plan and per world day.
- Repeated identical blocked steps trip a loop breaker and end with a typed reason.
- Restart at any step observes persisted completion and never duplicates an action,
  resource entry, wake, or model call.
- A plan never reserves resources indefinitely; reservations expire or release on
  completion, cancellation, death, incapacity, and deadline.

## 10. Resource and Capacity Invariants

- Available/reserved/consumed values never become negative.
- Conservation holds for transfers unless a typed source/sink policy applies.
- One logical action creates at most one logical ledger effect per resource leg.
- Account and world versions fence stale writes.
- Concurrent allocation of the final unit has one winner and an auditable loser.
- Clinic beds, shelter capacity, queue positions, and rescue seats cannot
  over-allocate.
- Resource visibility is scoped: an Agent sees owned/local/offered quantities, not
  all hidden stock.
- Corrections append compensating entries; historical ledger rows are not edited.
- Rollback leaves no partial ActionResult, state update, ledger entry, event,
  Observation, plan advance, or notification.

## 11. Deterministic Uncertain Adjudication

Use randomness only where the scenario requires uncertain escape/search/service
outcomes. Store enough information to reproduce the result exactly.

Seed derivation must use stable bytes from versioned inputs such as world ID,
scenario version, action idempotency key, policy version, and attempt number.
Never include transaction timestamp, worker identity, process ID, Python `hash()`,
or database row enumeration order.

The same idempotency key returns the first result. A different attempt number may
produce a new roll only when policy explicitly permits retry and consumes time or
resources. The UI must distinguish probability before action from actual outcome.

## 12. Thirty-Resident Tiered Simulation

Seed exactly 30 fixed residents for the acceptance world:

- 3 L3 special Agents: Lin, Zhou, Chen;
- 10–12 L2/L1 named relevant residents involved in clinic, government, market,
  household, gate, and rescue arcs;
- remaining residents as L1 or L0 background population.

Requirements:

- all residents have objective identity, location/tier, status, household or role,
  and minimal schedule/resource demand;
- only L3 Agents receive full decision prompts;
- L2 residents may use bounded model calls only if research and a recorded budget
  justify it; deterministic fixtures use none;
- L1 ordinary schedules run as templates;
- L0 demand may be aggregated but must preserve total population/resource counts;
- encounters and queue membership are server-derived;
- background residents cannot reveal hidden facts merely because aggregate state is
  available to the engine;
- seven-day advancement remains bounded and resumable.

## 13. Persistence and Migration

Add reversible normalized tables as justified by the ADR for:

- resource definitions/accounts/ledger/reservations;
- goals/plans/plan steps or references;
- schedule templates/resident simulation state;
- conditional events/evaluation records;
- adjudication traces;
- scenario version/checkpoint metadata.

Enforce with database constraints where possible:

- non-negative and bounded amounts;
- fixed units/precision;
- unique logical ledger entry per action/resource leg;
- monotonic account/plan versions;
- one active plan in a declared plan slot;
- bounded retry/replan counts;
- valid plan and reservation transitions;
- unique conditional-event firing key;
- no over-capacity allocation;
- indexes for due plan/schedule work, active plans, account balances, queues,
  conditional events, and replay.

Migration must downgrade cleanly to `20260727_0007`, upgrade to head, and pass
Alembic drift check on real PostgreSQL. Preserve TASK-001–018 history.

## 14. Runtime, Concurrency, and Restart

- Reuse `WorldRuntimePort`; do not create a second clock.
- Equal-time operations use a documented total order.
- One advance processes bounded work and returns a continuation/backlog cursor when
  more is due.
- Pause freezes world-time plans, schedules, reservations, and conditional events
  without deleting them.
- World/runtime generation and row claim tokens fence stale workers.
- Independent Agent thinking may run concurrently; authoritative commits are
  serialized per world or protected by equivalent proven fencing.
- No world/account lock is held during model inference.
- Crash before commit retries safely; crash after commit reads completion.
- Failed work never becomes a successful plan step or resource consequence.
- Seven-day catch-up is bounded so one API call cannot monopolize the worker.
- Reset/reseed is explicit, demo-only, idempotent, and cannot affect another world.

## 15. Agent Decision Integration

Extend TASK-016 input only with owner-visible:

- active goals and plan summaries;
- current plan blockage/completion Observation;
- owned/local/offered resource summaries;
- relevant relationships already allowed by existing contracts;
- server-derived action affordances.

Do not copy the full resource ledger, all residents, all plans, hidden capacities,
future events, objective truth, or other Agents' private state into prompts.

The 32-Observation bound remains. Add explicit bounded fields and retrieval rules;
do not silently expand prompt size. Each accepted L3 decision records prompt/schema
versions, attempts, tokens, nullable cost, selected affordance, validation, result,
and plan linkage.

## 16. Privacy, Security, and Content Safety

- Agent endpoints derive owner from the existing server-side caller boundary.
- Observer/dev endpoints may show objective branches but not raw prompts, reasoning,
  credentials, hidden future events, or unrelated private memories.
- Resource IDs, plan IDs, condition IDs, and resident IDs are server-offered; model
  or client cannot forge them.
- Condition AST rejects unknown fields/operators, excessive depth/count, strings
  resembling code, and injection content.
- Narrative text is untrusted and cannot become a condition, resource amount,
  target, or state update.
- Add decoy future rescue list, hidden medicine cache, private diagnoses, Agent
  goals, and prompt-injection fixtures.
- No action may infer authorization from a model rationale.
- Death, illness, minors, and distressing notifications follow the project's
  fiction/content labeling and avoid manipulative urgency.

## 17. API Contract

Candidate fixed-demo endpoints:

```http
POST /demo/worlds/gray-harbor/scenario/reset
GET  /demo/worlds/gray-harbor/scenario
GET  /demo/worlds/gray-harbor/resources
GET  /demo/worlds/gray-harbor/plans
GET  /demo/worlds/gray-harbor/residents
GET  /demo/worlds/gray-harbor/outcomes
GET  /demo/worlds/gray-harbor/me/resources
GET  /demo/worlds/gray-harbor/me/goals
GET  /demo/worlds/gray-harbor/me/plans
```

Existing runtime start/pause/resume/advance endpoints remain the only way to advance
time. No endpoint may directly mark a plan completed, fire a condition, allocate a
seat, modify a balance, choose a random result, or write an ActionResult.

Stable candidate error codes:

- `RESOURCE_NOT_FOUND`
- `RESOURCE_AMOUNT_INVALID`
- `RESOURCE_INSUFFICIENT`
- `RESOURCE_UNIT_MISMATCH`
- `RESOURCE_ACCOUNT_VERSION_CONFLICT`
- `RESOURCE_RESERVATION_EXPIRED`
- `CAPACITY_EXHAUSTED`
- `ACTION_TARGET_NOT_ALLOWED`
- `ACTION_AFFORDANCE_STALE`
- `PLAN_NOT_ACTIVE`
- `PLAN_STEP_CONFLICT`
- `PLAN_PRECONDITION_FAILED`
- `PLAN_REPLAN_LIMIT_REACHED`
- `PLAN_LOOP_DETECTED`
- `CONDITIONAL_EVENT_INVALID`
- `CONDITIONAL_EVENT_ALREADY_FIRED`
- `ADJUDICATION_POLICY_MISMATCH`
- `ADJUDICATION_ATTEMPT_NOT_ALLOWED`
- `WORLD_ADVANCE_WORK_LIMIT_EXCEEDED`

Errors use the existing JSON envelope.

## 18. Frontend Vertical Slice

Build one coherent internal-playtest surface, not disconnected debug widgets.

### 18.1 Seven-Day Control and Timeline

Show current day/hour, runtime state, next due work, backlog, scenario version, and
bounded advance controls. Clearly label demo reset as destructive to the fixed
scenario and require confirmation.

### 18.2 Resource and Capacity Board

Show observer-safe food, water, medicine, clinic beds, shelter capacity, and rescue
seats with changes linked to actions/events. Distinguish available, reserved,
consumed, and unknown-to-selected-Agent values.

### 18.3 Goals and Plans

For Lin, Zhou, and Chen show active/completed/blocked/abandoned plans, current step,
deadline, blockage reason, and linked actions. Do not display raw private reasoning.

### 18.4 Resident and Queue View

Show 30 residents by simulation tier, location/role/status, and relevant public
queue membership. Preserve privacy for diagnoses, secrets, beliefs, and private
goals.

### 18.5 Consequence Replay

Extend replay across:

```text
hard/conditional event
 -> propagation/Observation/belief
 -> goal/plan/step
 -> decision/affordance/ActionIntent
 -> validation/adjudication trace
 -> ActionResult/resource ledger/state mutation
 -> witnesses/Observations
 -> later blocked/completed plan and final Day-7 outcome
```

### 18.6 Agent-Local Preview

Show only the selected owner’s resources, goals, plans, received consequences, and
available actions. Query keys must include Agent identity and scenario version;
switching Agents must not reuse private cache data.

## 19. Replay, Metrics, and Evaluation

Observer replay must expose safe IDs, versions, world times, state transitions,
resource legs, plan transitions, condition evaluations, adjudication modifiers and
rolls, model/token/cost metadata, and typed failures.

Persist or derive:

- action offered/submitted/accepted/rejected/executed counts;
- action executable rate;
- plan completed/blocked/abandoned/loop-broken counts;
- resource conservation and capacity checks;
- wakes by reason and coalescing rate;
- model calls/tokens/cost per Agent and simulated day;
- L0/L1/L2/L3 operations;
- knowledge leakage fixture results;
- goal continuity and causal-reference fixture results;
- seven-day wall-clock execution time in deterministic CI;
- backlog high-water mark.

Raw prompts/reasoning and private message bodies are not telemetry.

## 20. Deterministic and Adversarial Fixtures

Cover at minimum:

- all seven days and required scenario branches;
- exact 30-resident and tier counts;
- normal schedule execution without model calls;
- resource transfer, reservation, consume, expiry, shortage, rollback, and
  conservation;
- two workers racing for the final medicine unit and final rescue seat;
- accepted, rejected, stale, forged, expired, and duplicate action affordances;
- plan completion, blockage, replan, abandonment, deadline, loop breaker, and
  actor death/incapacity;
- hard and conditional event exact-once firing;
- restart before/after plan step, action, ledger, event, Observation, wake, model
  completion, and checkpoint;
- deterministic uncertain result across restart and two workers;
- pause/resume and bounded multi-day catch-up;
- invalid units, negative/overflow amounts, hidden account, unauthorized target,
  and cross-world IDs;
- injection in event text, resident speech, resource label, plan rationale, and
  condition-like text;
- decoy future events, rescue list, medicine cache, diagnoses, plans, and secrets
  absent from unauthorized prompts/APIs/logs;
- same-key retries with zero duplicate result, mutation, ledger entry, plan step,
  event, Observation, wake, model call, or outbox intent.

No test may sleep or depend on probabilistic timing.

## 21. Performance and Cost Budgets

Before implementation, record baseline TASK-018 counts. Acceptance budgets:

- seven virtual days and 30 residents complete in a bounded deterministic test
  suitable for local CI;
- ordinary L0/L1 schedules use zero model calls;
- deterministic acceptance uses fake models and paid cost US$0;
- maximum L3 model calls per Agent/day and per scenario are explicit and enforced;
- plan/replan, action retry, condition evaluation, queue processing, and catch-up
  limits are explicit;
- prompt Observation count remains at most 32 and all new fields have size limits;
- no unbounded fan-out, queue scan, dialogue, plan depth, or resource entry batch;
- budget exhaustion pauses/defers or terminates with an audited code and invents no
  action.

The task must record actual counts and timings, not merely state that they are
“small”.

## 22. Backend and Frontend Tests

Backend tests cover:

- strict contracts and generated schemas;
- pure condition/plan/resource/adjudication policies;
- Pydantic/JSONB round trips;
- database constraints and reversible migrations;
- repository owner isolation;
- resource and capacity concurrency;
- World Engine authority and rollback;
- runtime virtual time, pause/resume, catch-up, fencing, and restart;
- decision prompt isolation and action affordances;
- full seven-day replay and exact counts;
- TASK-001–018 regression.

Frontend tests cover loading, empty, error, partial day, in-progress, blocked plan,
resource shortage, stale retry, irreversible outcome, reset confirmation, reconnect,
Agent switch/cache isolation, malicious content rendering, sent-versus-outcome
separation, observer-versus-Agent privacy, and existing surfaces.

## 23. Verification Gates

Backend:

```powershell
$env:RUN_INFRA_TESTS='1'
$env:RUN_WORKFLOW_TESTS='1'
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m app.domain.export_schemas --check
python -m alembic check
python -m alembic downgrade 20260727_0007
python -m alembic upgrade head
python -m alembic check
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

Operational smoke:

1. Clean migrate and seed the versioned 30-resident scenario.
2. Start and advance through Day 1; inspect clinic resources and Lin's plan.
3. Restart while plans and Day-3 messages are pending.
4. Advance through Day 5; prove shipment-stop condition/event and blocked plans.
5. Race two workers for the final medicine unit and prove one winner.
6. Pause with due work pending; prove no world-time delivery until resume.
7. Restart before an uncertain attempt and prove the same adjudication result.
8. Advance through Day 7 and record all three special-Agent outcomes.
9. Retry all scenario commands and prove exact zero-duplicate counts.
10. Inspect observer and each Agent-local API/UI for decoy leakage.
11. Record model calls, tokens, nullable costs, elapsed time, and backlog high-water
    mark; paid cost must be zero unless explicitly authorized.

## 24. Required Implementation Sequence

1. Reconfirm the clean TASK-018 baseline and record counts.
2. Complete the dated research ADR and executable spikes.
3. Freeze the seven-day scenario specification and versioned acceptance seed.
4. Update authority/architecture documentation before implementation.
5. Write failing resource, plan, condition, adjudication, privacy, race, restart,
   and seven-day replay tests.
6. Define strict domain contracts and regenerate schemas/types.
7. Add reversible normalized persistence and constraints.
8. Implement pure resource, condition, plan-transition, and adjudication policies.
9. Extend World Engine and Action Validator with the narrow action vocabulary.
10. Integrate plan/schedule work with the existing runtime and fencing.
11. Seed 30 residents and tiered ordinary schedules.
12. Integrate owner-visible goals/plans/resources into bounded decision input.
13. Complete the Day 1–7 deterministic scenario.
14. Extend replay, metrics, APIs, and privacy-safe read models.
15. Build the coherent internal-playtest frontend surface.
16. Run crash/race/restart/pause/virtual-time/leakage/performance suites.
17. Run and record the full operational smoke and exact counts.
18. Synchronize status, architecture, development, runbook, known-issues, and
   completion documents.

## 25. Allowed Changes

- resource, goal, plan, schedule, condition, resident-tier, and adjudication domain
  contracts;
- Gray Harbor fixed scenario data and versioning;
- narrow Action Validator and World Engine action support;
- PostgreSQL models/repositories/migrations/indexes/constraints;
- current WorldRuntimePort due-work integration;
- TASK-016 decision input/affordance integration;
- TASK-018 propagation/Observation/wake integration;
- observer and owner-scoped APIs/read models;
- seven-day control, resource, plan, resident, outcome, and replay UI;
- metrics, tests, ADRs, architecture/development/runbook/status docs;
- Docker configuration only if research proves a required service and documents its
  removal seam.

## 26. Explicitly Out of Scope / Forbidden

- free world creation, arbitrary event editor, or general rules marketplace;
- player-authored executable Python/SQL/JavaScript/Jinja or unrestricted JSON rules;
- full Temporal migration unless research proves the current runtime cannot satisfy
  correctness and an explicit migration plan is approved;
- 30 independent LLM Agents or continuous polling;
- combat, unrestricted trade/economy, crafting, theft, complex persuasion, or
  real-time pathfinding;
- general organization AI, politics, reproduction, genetics, or population growth;
- long-term vector memory/pgvector and biography compression;
- automatic personality, emotion, relationship, or Oracle-trust mutation without
  a separately versioned authority policy;
- production authentication overhaul, push/email delivery, native apps, multi-world
  scheduling, world sharing, marketplace, or Kubernetes;
- LLM-authored facts, recipients, stock, amounts, probability, random results,
  action success, state mutation, queue priority, or rescue eligibility;
- raw prompts/reasoning, hidden future events, private diagnoses, unrelated Agent
  state, credentials, or provider responses in APIs/UI/logs;
- wall-clock sleeps, unseeded randomness, infinite retry/replan, or unbounded
  catch-up.

## 27. Acceptance Criteria

TASK-019 is complete only when:

- the dated ADR compares all mandatory research categories and records executable
  spikes before dependency selection;
- one versioned scenario advances exactly 30 residents through seven virtual days;
- only three residents are L3 special Agents and ordinary schedules require no LLM;
- at least five narrow authoritative action types traverse ActionIntent, Validator,
  World Engine, ActionResult, event/Observation, and replay;
- resources and capacities obey non-negative, conservation, reservation, version,
  and concurrency invariants;
- goals/plans are persisted, bounded, explainable, restart-safe, and demonstrate
  completion, blockage, replan/abandonment, and loop termination;
- hard and conditional events fire exactly once under restart and two workers;
- uncertain adjudication is versioned, stored, reproducible, and never model-owned;
- the required Day 1–7 causal arc and irreversible Day-7 consequence are visible;
- Lin, Zhou, and Chen end with meaningfully different local states and histories;
- no lock is held during model inference;
- forged/stale/hidden action, target, resource, plan, condition, and cross-world IDs
  cannot commit;
- retries create zero duplicate ActionResult, mutation, ledger entry, plan step,
  event, Observation, wake, model call, or outbox intent;
- Agent inputs/APIs/UI remain owner-isolated and decoy fixtures do not leak;
- observer replay connects information, belief, goal, plan, action, resource change,
  and final consequence;
- model calls, tokens, cost, wake frequency, plan loops, action executability,
  resource invariants, elapsed time, and backlog are recorded against explicit
  budgets;
- the internal-playtest UI supports reset/start/pause/advance and explains current
  resources, plans, residents, and consequences;
- migration downgrade to `20260727_0007`, upgrade to head, Alembic drift check,
  backend/frontend/schema/Docker/lint/type/format/build gates all pass;
- documentation describes scenario topology, rules, limits, privacy, recovery,
  costs, and residual risks.

## 28. Completion Report

Report:

- selected/rejected libraries with versions/licenses and removal seams;
- scenario version, 30-resident tier distribution, locations, resources, capacities,
  schedules, conditions, plans, and action vocabulary;
- all seven daily event/resource/plan timelines;
- Lin/Zhou/Chen belief-goal-plan-action-outcome chains;
- exact resource conservation/capacity proofs;
- deterministic adjudication seed/roll replay proof;
- plan completion/blockage/loop-break evidence;
- race/restart/pause/catch-up and exact zero-duplicate counts;
- privacy/injection/decoy evidence;
- action executable rate, model calls/tokens/cost per day and Agent, runtime elapsed
  time, and backlog high-water mark;
- complete quality-gate output;
- remaining limits and an evidence-based TASK-020 recommendation.

## 29. Follow-On Decision

Do not preselect TASK-020. Choose based on TASK-019 evidence:

- long-term memory/pgvector if important Day-1–5 experiences are missing from later
  decisions or prompts hit history limits;
- notification/PWA/offline summaries if the seven-day world is engaging but players
  fail to return or miss important moments;
- world creation if internal playtests find the fixed loop engaging, explainable,
  private, and cost-controlled and users want a second world;
- richer relationships/personality evolution if decisions remain coherent but lack
  long-term interpersonal consequences;
- more actions only if executable action coverage, rather than memory or return
  behavior, remains the measured bottleneck.
