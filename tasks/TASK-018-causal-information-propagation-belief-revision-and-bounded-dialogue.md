# TASK-018: Causal Information Propagation, Belief Revision, and Bounded Multi-Agent Dialogue

**Status:** Done
**Planning date:** 2026-07-27
**Depends on:** TASK-001 through TASK-017
**Primary product source:** `D:\娴忚鍣╘AI 涓栫晫瑙傚療涓庡共棰勬ā鎷熷櫒浜у搧涓庢妧鏈疄鏂借鍒掍功.pdf` (41 pages, fully reviewed during planning)

## 1. Why This Task Is Next

TASK-017 completes the durable single-Agent loop: a persisted event wakes Chen, a restart-safe Oracle window resolves by reply or timeout, and a fresh decision reaches the authoritative World Engine without duplicate work. It proves offline continuity and delayed player intervention, but not the product's central social-world promise.

The product plan's first technical milestone explicitly requires one secret event to travel through different channels, reach three special characters at different times and in different forms, alter their local beliefs, and produce thought/action/dialogue consequences. The current runtime delivers one event-derived Observation directly to Chen. There is no durable message-in-transit lifecycle, channel delay, source provenance, reliability/distortion representation, belief revision history, Agent-authored communication action, or bounded multi-Agent conversation.

This is the largest missing part of the first milestone. Long-term vector memory would optimize recall before there is a sufficiently rich social history to recall. Free world creation would generalize an unproven interaction loop. Browser push would improve return behavior before internal events are rich enough to merit returning for.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Causal propagation + belief revision + bounded dialogue | **Selected.** Completes the missing multi-character half of the first milestone and tests information asymmetry, misunderstanding, correction, and agency. |
| Long-term memory / pgvector | Deferred until repeated provenance-rich experiences expose measurable recall failures. |
| Richer physical actions | Deferred; add only narrow communication actions required by this scenario. |
| Notification/PWA/email | Deferred until playtests show player return is the bottleneck. |
| World creator/event editor | Deferred because the product plan says to validate the fixed-world character loop first. |
| General NPC population simulation | Deferred; one typed courier/background source may exist only as fixture data. |

## 3. One-Sentence Acceptance Target

Advance Gray Harbor deterministically through one objective north-gate fact that reaches Lin, Zhou, and Chen through different persisted channels, delays, reliability, and wording; creates three owner-scoped and possibly conflicting belief histories; leads to one server-validated, time-bounded Chen?Zhou exchange that can correct or preserve a rumor; and remains privacy-safe, restart-safe, idempotent, cost-bounded, and fully replayable.

## 4. Required Fixed Scenario

1. At a known world time, World Engine publishes the objective fact that the north gate will close at a specified time.
2. The fact is not globally visible to Agents and is never copied wholesale into all prompts.
3. Lin receives an immediate direct/official Observation with high reliability because role and location permit it.
4. Zhou receives a delayed official bulletin through a persisted channel.
5. Chen receives a later courier rumor with typed distortion, such as believing all gates may close earlier.
6. Each delivery records provenance and creates or revises only the receiving Agent's belief.
7. At an intermediate world-time checkpoint, the three Agent inputs contain demonstrably different claims.
8. Chen is selectively awakened and may choose a server-offered `send_message`/`speak` affordance to ask Zhou for confirmation.
9. World Engine validates channel availability and creates a message transmission; the model cannot deliver text directly.
10. Zhou receives the message as an Observation, wakes, and may reply with the official version or decline/end the exchange.
11. Chen receives the reply after channel delay and revises, retains, or marks conflict according to versioned evidence policy.
12. The conversation terminates through an explicit reason within strict turn/time/token limits.
13. Observer replay explains the chain while each Agent API sees only its own records.
14. Restart at in-transit and between-turn checkpoints loses no work and creates no duplicate delivery, wake, belief revision, model call, action, or notification.

All deadlines and delays use deterministic virtual-time advancement. Tests may not sleep.

## 5. Mandatory Preliminary Official/Open-Source Research

Implementation starts with a dated ADR and executable spikes. Record versions checked on the implementation date, licenses, maintenance, Python/platform support, operational footprint, privacy, deterministic-test support, failure semantics, and removal cost. No production dependency is added before this evidence.

### 5.1 Propagation graph and routing

Compare dependency-free typed adjacency rules, NetworkX, python-igraph, rustworkx, PostgreSQL recursive CTEs, and pgRouting only if spatial routing is genuinely needed. Evaluate directed multi-edges, channel attributes, time-dependent availability, deterministic order, path explanation, graph versioning, serialization, 30?50 resident performance, dependency weight, and authority boundaries. At this scale, dependency-free or SQL-backed rules remain the default unless a spike proves material correctness value.

### 5.2 Durable message delivery and fan-out

Compare normalized PostgreSQL transmission rows using existing runtime fencing, LISTEN/NOTIFY as a hint, Redis Streams/PubSub, NATS JetStream, Kafka/Redpanda, and Celery/Dramatiq where relevant. Evaluate world-time delay, ordering, recovery, deduplication, dead letters, replay linkage, local CI complexity, retention, privacy, and migration cost. PostgreSQL remains authority; Pub/Sub alone is not durable; no broker may create Observations or beliefs.

### 5.3 Belief revision and uncertainty

Compare a deterministic evidence ledger with bounded confidence updates, pgmpy, PyMC as a complexity baseline, maintained truth-maintenance/Dempster?Shafer options, and LLM-only updates as a rejected baseline. Evaluate conflicting evidence, shared-source deduplication, reliability, recency, correction/retraction, explainability, deterministic replay, calibration, and false precision. The task does not solve general epistemology. A model may propose a bounded interpretation but cannot declare objective truth or rewrite evidence.

### 5.4 Dialogue orchestration

Compare explicit finite-state orchestration with current maintained versions of LangGraph, Microsoft AutoGen, CAMEL or equivalent, and PydanticAI graph/agent capabilities. Evaluate turn limits, interruption, participant authorization, durable checkpoints, structured output, provider independence, prompt isolation, unrestricted-tool risk, transcript privacy, deterministic fixtures, duplicate-call recovery, and removal cost. Frameworks that let Agents call each other directly or share global context are unsuitable.

### 5.5 Evaluation and observability

Compare deterministic pytest/replay assertions with optional DeepEval, Promptfoo, Langfuse, Phoenix, and OpenTelemetry GenAI conventions. Define measurements for leakage, provenance accuracy, belief divergence/convergence, action executability, dialogue loops, token/cost budgets, and prompt injection without storing raw private prompts in telemetry.

### 5.6 Required research spikes

The ADR must include executable evidence for:

1. deterministic equal-time routing through a multi-edge graph;
2. one delayed transmission claimed by two workers but delivered once;
3. restart before and after Observation delivery;
4. conflicting evidence producing history instead of destructive overwrite;
5. a bounded two-Agent conversation that terminates without recursive calls;
6. a decoy secret that never crosses recipient boundaries;
7. removal seams for any selected library or broker.

## 6. Target Architecture and Authority

```text
World Engine publishes WorldEvent/WorldFact
  -> InformationPropagationPolicy (pure, server-owned)
     -> MessageClaim + persisted Transmission
        -> WorldRuntimePort schedules arrival
           -> Observation Builder creates recipient-only Observation
              -> BeliefRevisionService appends evidence/revision
                 -> WakePolicyEvaluator coalesces wake
                    -> TASK-016 decision with server affordances
                       -> communication ActionIntent
                          -> Validator -> World Engine -> ActionResult
                             -> reply Message/Transmission within budget
```

- World Engine alone creates authoritative state changes, ActionResult, and action-caused WorldEvent records.
- Propagation Policy chooses allowed routes but does not change facts or beliefs.
- Observation Builder remains the only Observation construction boundary.
- Belief Revision changes only subjective AgentBelief/evidence, never WorldFact.
- Model Gateway may propose wording, interpretation, or an offered action; it cannot choose hidden recipients, set delivery success/delay/reliability, write beliefs, or mutate the world.
- Runtime coordinates claims/time but invents no content, recipient, belief, or outcome.
- PostgreSQL remains replay authority; queue/notification systems are transport or wake hints.

Any ownership change requires an ADR and architecture-handbook update before implementation.

## 7. Domain Contracts

Define strict Pydantic contracts and generated Schema/TypeScript types for real public boundaries. Lifecycle-critical fields must not hide in opaque JSONB.

### 7.1 CommunicationChannel

Represent stable ID/version, typed kind (`direct`, `official_bulletin`, `courier`, `local_rumor`), allowed scope, world-time delay policy, availability, reliability/distortion policy IDs, privacy class, payload/capacity limits, and validity interval. Clients/models cannot invent routes.

### 7.2 Message and claim

Separate authorship from delivery. A message records sender, bounded subjective claims, content kind, visible evidence references, world time, correlation, and schema version; it does not assert delivery or objective truth. Claims distinguish observed/heard/inferred/uncertain/denied/corrected stance and attribution. Hidden WorldFact IDs must not leak merely as identifiers.

### 7.3 Transmission

Use an explicit lifecycle:

```text
created -> scheduled -> due -> claimed -> delivered
                              -> retryable_failed -> scheduled
                              -> terminal_failed
created/scheduled -> cancelled | expired
```

Persist delivery key, channel/message/sender/recipient, send/arrival world times, stable order, attempts, lease token/deadline, runtime generation, delivered Observation/wake IDs, typed failure, and causal IDs.

### 7.4 Belief evidence and revision

Beliefs are not silently overwritten. Persist Agent/proposition key, prior revision, source references visible to the Agent, stance, bounded confidence/reliability inputs, policy/version, world and transaction times, active/superseded/conflicted status, and safe reason codes. An Agent may remain wrong, stale, uncertain, or conflicted.

### 7.5 Conversation

Persist session/correlation, fixed participants, initiating action/message, state (`opening`, `active`, `awaiting_delivery`, `completed`, `cancelled`, `faulted`), turn/current speaker, deadlines, maximum turns, model/token/cost budget, terminal reason, latest transmission, and fencing/version. Each turn is a durable activation; there is no nested model loop.

## 8. Deterministic Propagation Policy

Pure policy code must prove route eligibility from versioned channel/location/organization/world-time data; stable order `(arrival_world_time, priority, created_at, transmission_id)`; direct/relayed provenance; bounded delays; deterministic distortion fixtures; explicit relay authority; server-derived recipients; fan-out/hop limits; cycle prevention; cancellation on invalid state; and retry under the same logical key. Seeded randomness may come later, but acceptance uses fixed seed and versioned algorithms.

## 9. Belief Revision Policy

For the fixed gate proposition:

- consume only the Agent's current beliefs and new Observation/evidence;
- append evidence before deriving current projection;
- distinguish independent corroboration from copies of one causal source;
- represent conflict instead of forcing convergence;
- use bounded reliability, recency, directness, and correction rules;
- preserve old revisions for replay;
- reject stale/fenced writes after a newer Observation watermark;
- version the policy and expose typed safe reason codes;
- never mechanically alter personality, emotion, goals, relationships, or Oracle trust.

Model interpretation, if used, is enum/schema bounded. Failure leaves evidence persisted and belief pending; it never fabricates certainty.

## 10. Communication Action and Adjudication

Add only scenario-required `send_message` and `end_conversation` actions. Affordances fix allowed recipient/channel/conversation/claim references and limits. Validator checks actor state, authorization, reachability, versions, turn, budget, and content. World Engine creates ActionResult plus message/transmission or typed rejection. Sending is not delivery; speech is subjective content, not truth; prompt injection remains untrusted; deterministic IDs prevent duplicates.

Silence, refusal, channel failure, timeout, movement, incapacitation, or external interruption must have typed terminal/suspension reasons. Combat, trade, arbitrary tools, and unrestricted dialogue are excluded.

## 11. Bounded Dialogue Coordinator

- Maximum three delivered turns for the fixed scenario unless research justifies fewer.
- At most one model call per claimed Agent turn using TASK-016 fencing/recovery.
- No DB/world lock during inference and no Agent-to-Agent function recursion.
- Each prompt contains only that Agent's own state, Observations, beliefs, relevant messages, and server affordances.
- Other participants' hidden prompts, beliefs, memories, secrets, and future work are absent.
- Every reply is an ActionIntent through Validator/World Engine.
- Failure, unsupported output, stale context, or exhausted budget terminates/defers with typed status and no fake speech.
- Restart replays completed work without duplicate call/action/message.
- Termination is explicit in replay and UI.

## 12. Persistence and Migration

Add reversible normalized tables for channel versions, messages/claims, transmissions/attempts, belief evidence/revisions, and conversation sessions/turn references as justified by the ADR.

Enforce where possible:

- one logical recipient delivery per message/channel/version;
- one Observation and wake per successful delivery/watermark;
- one active turn per conversation;
- monotonic turn/version/fencing tokens;
- unique action/message per decision idempotency key;
- valid lifecycle transitions and bounded lengths/counts;
- safe causal referential integrity;
- indexes for due transmissions, Agent inbox, active beliefs, active conversations, and replay.

JSONB must round-trip through strict Pydantic models and never store credentials, raw prompts/reasoning, unrestricted provider output, or unrelated private data. Migrations downgrade cleanly to `20260727_0006`, upgrade to head, and pass Alembic check on real PostgreSQL.

## 13. Runtime, Claims, and Failures

Reuse `WorldRuntimePort`; do not create a second scheduler. A transmission arrival is typed scheduled world work.

- Virtual-time advancement delivers only due bounded work.
- Pause freezes world-time delivery without deletion.
- Runtime generation and transmission claim token fence stale workers.
- Equal-time transmissions have total order; catch-up is bounded/resumable.
- The delivery winner atomically persists transmission state, Observation, belief evidence/revision, wake, and replay/outbox references where feasible.
- Crash before commit retries safely; crash after commit observes completion.
- Failure never becomes a successful Observation.
- Dead/inactive/invalid recipients, cycles, hop overflow, budget overflow, and expiry use typed outcomes.
- Real time cannot reorder world-time delivery.

## 14. Privacy and Security

- Agent APIs derive identity from the existing server-side demo caller boundary.
- A sender may communicate only server-offered claims derived from its own beliefs/evidence plus bounded subjective wording.
- Observation Builder strips server-only route and hidden provenance data.
- Observer replay labels objective and subjective branches but excludes raw prompts/reasoning, credentials, unrelated private content, and full provider responses.
- Oracle text and Agent speech are untrusted content, never system instructions.
- Add direct, synonym, encoded, indirect-inference, prompt-injection, recipient-confusion, and cross-conversation decoy fixtures.
- Logs redact bodies by default and use IDs, types, lengths, hashes, and safe summaries.
- Existing fiction/content labeling and bounded-input rules remain.

## 15. API Contract

Candidate fixed-demo endpoints:

```http
GET /demo/worlds/gray-harbor/propagation
GET /demo/worlds/gray-harbor/conversations
GET /demo/worlds/gray-harbor/conversations/{conversation_id}
GET /demo/worlds/gray-harbor/me/messages
GET /demo/worlds/gray-harbor/me/beliefs/history
```

Existing runtime `advance` triggers due work. No endpoint may directly mark delivery or write belief state. Observer/dev reads may inspect all causal branches; Agent reads remain owner-scoped. Errors use the existing JSON envelope.

Stable candidate codes:

- `COMMUNICATION_CHANNEL_UNAVAILABLE`
- `MESSAGE_RECIPIENT_NOT_ALLOWED`
- `MESSAGE_CLAIM_NOT_KNOWN`
- `MESSAGE_CONTENT_TOO_LARGE`
- `TRANSMISSION_ALREADY_DELIVERED`
- `TRANSMISSION_CLAIM_CONFLICT`
- `TRANSMISSION_EXPIRED`
- `PROPAGATION_HOP_LIMIT_EXCEEDED`
- `BELIEF_INPUT_STALE`
- `BELIEF_EVIDENCE_DUPLICATE`
- `CONVERSATION_NOT_ACTIVE`
- `CONVERSATION_TURN_CONFLICT`
- `CONVERSATION_PARTICIPANT_UNAVAILABLE`
- `CONVERSATION_BUDGET_EXHAUSTED`
- `CONVERSATION_MAX_TURNS_REACHED`

Clients cannot choose delivery outcome, arrival time, reliability, distortion, unauthorized recipients, belief confidence, speaker, action result, or wake target.

## 16. Frontend Vertical Slice

### 16.1 Propagation Inspector

Show the objective source event and three parallel branches with channel, sent/arrival world time, attribution, reliability/distortion, delivery status, and recipient. Clearly distinguish objective fact, communicated claim, Observation, and belief.

### 16.2 Belief Evolution

For each Agent show ordered revisions: prior stance/confidence, new evidence visible to that Agent, conflict/correction reason, and current projection. Never imply observer truth was available locally.

### 16.3 Bounded Conversation Thread

Show participants, turn/delivery status, world-time delay, subjective speech, ActionIntent/ActionResult, terminal reason, and remaining budget. Distinguish `sent`, `delivered`, `believed`, and `objectively true`.

### 16.4 Agent-local preview

Extend current-Agent preview only with owner-scoped inbox/outbox and belief history. Switching Lin/Zhou/Chen must not reuse cached private data. Reconnect always refetches authoritative cursor APIs; SSE/WebSocket remains optional transport.

## 17. Replay and Explainability

Extend unified replay through:

```text
WorldEvent/WorldFact
 -> propagation policy/version
 -> message claim
 -> channel/transmission
 -> recipient Observation
 -> belief evidence/revision
 -> wake
 -> model attempt/decision
 -> communication ActionIntent/ActionResult
 -> reply transmission
 -> recipient Observation/revision
 -> conversation terminal state
```

Expose privacy-safe IDs, statuses, world times, versions, policy identifiers, hashes, cost metadata, and typed failures. Preserve shared source lineage so repeated rumors are not shown as independent corroboration. Test historical projections across policy/schema versions.

## 18. Cost and Loop Controls

Persist observer-safe metrics for delivery attempts/outcomes, hops/fan-out/backlog, wake/coalescing, belief conflict/correction, dialogue turns, model calls/tokens/nullable cost, termination, and action acceptance. Hard-limit messages per event, hops, recipients, body size, active conversations, turns, world duration, model attempts/tokens, and daily world/Agent budget. Exhaustion terminates/defers with audited code and never fabricates work.

## 19. Deterministic and Adversarial Fixtures

Cover at minimum:

- direct, delayed-official, and distorted-rumor branches;
- three different intermediate Agent beliefs;
- stable equal-time route/delivery order;
- two-worker same-delivery race and parallel different deliveries;
- crash before/after message, claim, Observation, belief revision, wake, model completion, and action;
- duplicate/relayed source deduplication, cycles, and hop limits;
- unavailable/cancelled/expired channel and invalid recipient;
- pause/resume and bounded downtime catch-up;
- belief conflict, correction, retraction, stale write, and policy-version replay;
- dialogue reply, refusal, timeout, interruption, max-turn, model failure, and budget exhaustion;
- stale affordance after location/channel change;
- unsupported recipient/action and forged fact reference;
- prompt injection in rumor/dialogue content;
- decoy observer/global/Lin/Zhou/Chen secrets absent from unauthorized prompts/APIs/logs;
- restart at each durable checkpoint;
- same-key retries with zero duplicate delivery, Observation, revision, wake, model call, message, action, and outbox intent.

No test may use probabilistic timing or sleep.

## 20. Backend and Frontend Tests

Backend tests cover strict contracts/schema generation, pure routing/delay/distortion policies, Pydantic/JSONB round trips, repository isolation, real PostgreSQL constraints/migrations, rollback/fencing, virtual time, multi-worker races, Observation isolation, belief invariants, TASK-016 turn recovery, authoritative communication actions, replay completeness/privacy, import boundaries, and full TASK-001?017 regression.

Record one deterministic end-to-end smoke with all three propagation branches and the correcting dialogue. A paid live-model smoke is optional, authorized, budget-capped, and never required.

Frontend tests cover loading/empty/error/partial/in-transit/delivered/conflicted/corrected/conversation/terminal/retry/reconnect states; objective-versus-subjective separation; sent/delivered/believed separation; provenance; action/result separation; terminal budget; observer/Agent privacy; query cache isolation; safe malicious-content rendering; and regression of existing surfaces.

## 21. Verification Gates

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
python -m alembic downgrade 20260727_0006
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

1. Clean migrate and seed Docker PostgreSQL.
2. Advance to the objective event and inspect Lin's immediate delivery.
3. Restart the worker while Zhou/Chen transmissions are pending.
4. Advance to both arrivals and prove different local claims/beliefs.
5. Restart between dialogue turns and complete the exchange.
6. Retry commands and run two workers on the same due rows.
7. Inspect observer propagation/replay and each Agent-local API/UI.
8. Prove exact logical counts and no decoy leakage.
9. Record token/cost totals; paid cost is zero unless explicitly enabled.

## 22. Allowed Changes

- propagation/channel/message/transmission/belief-revision/conversation domain contracts;
- one fixed Gray Harbor topology and scenario;
- pure routing, distortion, belief, and conversation policies;
- PostgreSQL models/repositories/migrations/indexes;
- WorldRuntimePort delayed delivery and turn activation;
- Observation Builder extensions;
- narrow communication Validator/World Engine behavior;
- TASK-016 decision integration for three fixed Agents;
- observer and Agent-scoped APIs/read models;
- Propagation Inspector, Belief Evolution, Conversation Thread UI;
- replay, metrics, tests, ADRs, architecture/development/runbook/status docs;
- Docker config only if selected research proves a new service necessary.

## 23. Explicitly Out of Scope / Forbidden

- general event/world/graph editor, pathfinding, geometry, or full organization simulation;
- unrestricted recipient selection or broadcast;
- player chat outside an Oracle request;
- combat, trade, inventory, persuasion probability, or broad actions;
- unbounded/recursive Agent dialogue or all background residents as LLM Agents;
- long-term vector memory, pgvector, biography compression, semantic retrieval;
- personality, emotion, goal, relationship, or Oracle-trust mutation without a separate authority contract;
- LLM-authored facts, visibility, recipients, reliability, arrival, confidence, delivery/result, or mutation;
- broker/Redis/telemetry as world truth;
- raw prompts/reasoning/credentials/hidden facts/cross-Agent state in messages, history, logs, APIs, or UI;
- production push/email, auth overhaul, multi-world scheduling, free creation, native apps, or Kubernetes;
- infinite retry, unbounded catch-up/fan-out, or invented fallback dialogue.

## 24. Required Implementation Sequence

1. Reconfirm the TASK-017 clean baseline.
2. Complete research ADR and executable spikes.
3. Define authority boundaries and update ADR/architecture docs first.
4. Write failing routing, privacy, race, restart, belief, dialogue, and replay tests.
5. Define strict contracts and regenerate schemas/types.
6. Add reversible normalized persistence and constraints.
7. Implement pure route/order/delay/distortion policy.
8. Integrate transmissions with runtime fencing/catch-up.
9. Extend Observation Builder without provenance leakage.
10. Implement append-only evidence/revision and current belief projection.
11. Add server-derived communication affordances and authoritative actions.
12. Implement bounded dialogue using TASK-016 recovery.
13. Complete the fixed three-branch scenario and correction exchange.
14. Extend replay, metrics, APIs, and privacy-safe read models.
15. Add frontend propagation/belief/conversation surfaces.
16. Run crash/race/restart/virtual-time/leakage/regression suites.
17. Record operational smoke and exact zero-duplicate counts.
18. Synchronize all status, architecture, development, runbook, and known-issues docs.

## 25. Acceptance Criteria

TASK-018 is complete only when:

- the dated ADR compares required libraries/frameworks and records spikes before dependency selection;
- one objective event creates different delayed provenance-rich claims for all three Agents;
- an intermediate checkpoint proves no shared global truth view;
- routes, recipients, times, reliability, and distortion are server-owned/versioned;
- restart and two workers still yield exactly one logical delivery;
- Observation Builder remains the sole delivery boundary;
- evidence is append-only, conflict preserved, and beliefs explainable;
- repeated relays of one source are not independent corroboration;
- Chen and Zhou complete or explicitly terminate one bounded dialogue;
- every speech attempt traverses Validator and World Engine;
- each turn uses owner-only fresh input and TASK-016 fencing/recovery;
- no DB/world lock exists during model calls;
- forged/stale/unsupported recipient, action, fact, and affordance cannot commit;
- loops and costs are bounded/auditable;
- failures invent no delivery, Observation, belief, dialogue, or success;
- replay connects the complete objective-to-subjective-to-action chain;
- Agent APIs/UI and query caches preserve owner isolation;
- injection/decoy fixtures prove no unauthorized leakage;
- retries produce zero duplicate delivery, Observation, revision, wake, model call, message, action, and outbox;
- deterministic operational smoke and exact counts are recorded;
- all backend/frontend/schema/migration/Docker/lint/type/format/build gates pass;
- docs describe topology, limits, privacy, recovery, and risks.

## 26. Completion Report

Report selected/rejected libraries with versions/licenses; architecture, tables, migrations, APIs/UI/topology; all three delivery/belief timelines; conflict/correction and source-deduplication proof; dialogue state/budget/termination/action proof; race/restart results; exact zero-duplicate counts; privacy/injection evidence; model/token/cost totals and paid-call status; full quality-gate output; remaining limits; and an evidence-based TASK-019 recommendation.

## 27. Follow-On Decision

Do not preselect TASK-019. Choose:

- long-term memory/pgvector if Agents fail to recall important propagated experiences;
- richer actions if decisions collapse to wait/move/message despite coherent beliefs;
- notification/PWA/offline summaries if the world is engaging but player return is the bottleneck;
- population simulation if three-Agent interaction feels socially empty;
- world creation only after the fixed Gray Harbor loop is engaging, explainable, private, and cost-controlled.
