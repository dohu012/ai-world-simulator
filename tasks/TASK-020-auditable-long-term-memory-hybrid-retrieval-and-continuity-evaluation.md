# TASK-020: Auditable Long-Term Memory, Hybrid Retrieval, and Continuity Evaluation

**Status:** Done  
**Planning date:** 2026-07-28  
**Depends on:** TASK-001 through TASK-019  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf`
（41 页，本次规划已完整阅读）

## 1. Why This Task Is Next

TASK-019 completed the fixed-world Stage 1 scenario: Gray Harbor now advances
through seven days with 30 persisted residents, three L3 Agents, durable plans,
contested resources, authoritative actions, exact-once conditions, restart
recovery, and an irreversible Day-7 rescue outcome. It creates the first history
long and rich enough for memory retrieval to be a real product requirement rather
than speculative infrastructure.

The current decision path does not yet preserve that continuity:

- there are no `memories` or `memory_embeddings` tables or domain contracts;
- Agent prompts receive the current profile and Observation feed, but no explicit
  episodic, semantic, emotional, or Oracle memory;
- the decision watermark records at most the last 32 Observation IDs while the
  current prompt assembly is not a bounded, ranked long-term context policy;
- Day-1 illness, Day-2 rationing, Day-4 rejection, Day-5 shipment loss, Day-6 plan
  outcomes, relationships, and past Oracle advice have no importance-aware path
  into later decisions;
- there is no retrieval trace showing why a past experience was included, omitted,
  or allowed to influence a decision;
- there is no fixed evaluation set for memory recall, false recall, temporal
  leakage, owner isolation, goal continuity, or personality continuity.

This gap directly blocks several product-plan requirements:

- special characters must have long-term personality and memory;
- the Agent loop explicitly retrieves relevant memory before considering goals and
  actions;
- memory must live outside the prompt, with only decision-relevant items loaded;
- retrieval must combine relevance, recency, importance, current goals, people,
  and emotional intensity rather than semantic similarity alone;
- important experiences, semantic beliefs, emotional experiences, and Oracle
  advice must remain distinguishable;
- the first release must measure recall accuracy, goal continuity, causal
  consistency, personality consistency, cost, and whether events have lasting
  effects;
- replay must show which memories were retrieved for a decision.

Production push can help players return, but no playtest evidence yet identifies
return frequency as the primary bottleneck. Free world creation would generalize a
fixed loop before its characters can remember that loop. Automatic personality or
relationship evolution would mutate durable identity before the evidence feeding
those changes is trustworthy. The next critical task is therefore a privacy-safe,
measurable memory system integrated into the existing authoritative decision and
replay path.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Long-term memory, hybrid retrieval, and continuity evaluation | **Selected.** TASK-019 now supplies multi-day, importance-bearing history, while the current Agent decision path has no durable retrieval layer. This is a central product differentiator and a prerequisite for credible long-term personality, relationships, and worlds. |
| Notification/PWA/offline summaries | Deferred until internal playtests show that the world is engaging but player return or missed moments are the limiting metric. Existing outbox records important moments but is not a production delivery channel. |
| World creator and event editor | Deferred. The product plan explicitly requires proving that fixed-world characters are worth following before building broad creation tools. |
| Personality/relationship evolution | Deferred as mutation authority. TASK-020 records and retrieves the evidence needed for a later versioned evolution policy, but does not silently rewrite traits, values, or Oracle trust. |
| More authoritative actions | Deferred. TASK-019 now has nine automatic actions and a meaningful consequence loop; missing continuity is the stronger blocker. |
| Dedicated vector database | Not preselected. The product plan recommends PostgreSQL + pgvector for MVP, but the implementation must first compare it with dedicated stores and prove filtered retrieval behavior. |

## 3. One-Sentence Acceptance Target

Run the versioned seven-day Gray Harbor scenario and later L3 decisions through an
exactly-once memory pipeline that converts only authorized, important experiences
into typed and provenance-linked memories, embeds them asynchronously, retrieves a
bounded owner-scoped hybrid context using structured, lexical, semantic, recency,
importance, goal, person, and emotion signals, records every candidate and score,
survives restart/provider failure without blocking world progress, and proves on a
fixed evaluation corpus that important memories are recalled while future,
cross-owner, superseded, and decoy information never reaches the Agent prompt.

## 4. Mandatory Research Before Design

Implementation must not begin with a selected library. First add a dated ADR and
executable spike report. Every candidate must record:

- exact version and release date;
- license and any server/client or model-weight license differences;
- maintenance activity and security posture;
- Python 3.12+, SQLAlchemy 2, PostgreSQL 17, Alembic, async driver, and Docker
  compatibility;
- Windows development and Linux container support;
- schema, index, backup, restore, migration, and downgrade implications;
- metadata pre-filter correctness and behavior under selective owner/world filters;
- deterministic-test and offline-test story;
- latency, memory, storage, token, and provider-cost measurements on the fixed
  corpus;
- operational services introduced and failure modes;
- removal seam and export format;
- adopted, rejected, and deferred decision with evidence.

### 4.1 Storage and search engines

Compare at minimum:

- PostgreSQL exact search plus pgvector;
- pgvector HNSW and IVFFlat, including filtered approximate-search behavior,
  iterative scans, index build/update cost, recall measurement against exact
  search, and extension lifecycle;
- PostgreSQL `tsvector`/`tsquery`, `ts_rank_cd`, trigram or equivalent lexical
  options, and reciprocal-rank or weighted fusion;
- Qdrant;
- Weaviate;
- Milvus;
- Chroma;
- no-vector structured plus lexical baseline.

The spike dataset must use Gray Harbor-shaped records with strong
`world_id`/`agent_id`/time/type filters and adversarial cross-owner decoys. Generic
Wikipedia or synthetic random-vector benchmarks are insufficient.

The expected MVP direction is PostgreSQL plus pgvector with exact search as the
small-corpus correctness baseline, because world state, ownership, provenance, and
memory remain in one transactionally managed database. This is a hypothesis, not
permission to skip the comparison. A separate service may be adopted only if a
measured requirement cannot be met in PostgreSQL and its consistency/recovery cost
is explicitly accepted.

### 4.2 Embedding generation

Compare at minimum:

- embedding through the existing provider-neutral Model Gateway;
- direct provider SDK/HTTP only as an adapter implementation;
- one locally runnable open-source path such as Sentence Transformers,
  FastEmbed/ONNX, or an equivalent maintained project;
- deterministic fake embeddings for unit and integration tests;
- lexical-only fallback.

Record model name, model revision, dimensions, normalization, distance metric,
maximum input length, multilingual Chinese/English behavior, batching, rate limits,
cost, data handling, and re-embedding strategy. Do not download model weights in
the default test suite.

### 4.3 Memory frameworks and orchestration

Compare Mem0, Letta, LangGraph memory facilities, and at least one other maintained
open-source memory/RAG implementation against a small internal
`MemoryWriterPort`/`MemoryRetrieverPort`. Evaluate:

- whether the framework preserves this project's Observation-only input boundary;
- whether writes and retrievals can be transactionally linked to existing events,
  actions, beliefs, Oracle responses, and decision records;
- whether scoring, provenance, prompt contents, retries, and model calls are fully
  inspectable;
- whether owner/world/time authorization occurs before retrieval;
- whether it introduces a second workflow, storage, or hidden prompt authority;
- whether it can be removed without rewriting domain records.

General autonomous-agent frameworks must not become World Engine, action,
workflow, or truth authority.

### 4.4 Ranking, reranking, and evaluation

Compare:

- deterministic weighted score fusion;
- Reciprocal Rank Fusion;
- optional cross-encoder or LLM reranking behind a port;
- Ragas, DeepEval, Phoenix, LangSmith evaluation, promptfoo, or equivalent current
  tools;
- repository-native pytest golden cases and replay assertions.

The ADR must distinguish offline evaluation tooling from production dependencies.
No evaluation SaaS may receive private Agent data in default or CI runs.

### 4.5 Required executable spikes

Commit deterministic spikes/tests that prove:

1. extension creation, vector insert/query, migration upgrade/downgrade, backup
   compatibility, and behavior when the extension is unavailable;
2. exact versus HNSW/IVFFlat recall and latency under owner/world filters;
3. lexical, vector, structured, and fused retrieval on bilingual Gray Harbor
   queries;
4. deterministic tie-breaking and stable results across process restart;
5. cross-owner and future-time decoys are filtered before ranking and reranking;
6. embedding timeout/rate-limit/outage leaves a durable retry and permits lexical
   fallback;
7. model revision or dimension change can coexist and re-embed without corrupting
   active reads;
8. the fixed evaluation corpus can score recall, precision, MRR/nDCG or justified
   alternatives without live paid calls;
9. token-budget packing is deterministic and never includes partial, unauthorized,
   or untraceable memory;
10. all rejected dependencies can be removed while the structured/lexical baseline
    still passes.

Spike code must not silently become production architecture. Record which code is
discarded, retained as tests, or promoted behind a port.

## 5. Architecture Decision Required

Add `decisions/ADR-013-*.md` before production implementation. It must decide:

- memory taxonomy and authority boundaries;
- storage/search engine and index policy;
- exact-search baseline and approximate-index activation threshold;
- embedding provider/model/version/dimension policy;
- normalized source records versus derived text/vector records;
- asynchronous embedding and retry workflow;
- hybrid retrieval algorithm, weights, hard filters, tie-breakers, and versioning;
- importance admission and consolidation rules;
- prompt assembly and token budgets;
- privacy model and redaction policy;
- replay/audit retention;
- failure and degradation behavior;
- re-embedding and migration rollout/rollback;
- accepted dependencies and explicit removal seams.

Changing ranking weights, embedding model, tokenizer, admission threshold,
consolidation policy, or prompt packing must create a new version. Historical
decision traces must retain the versions actually used.

## 6. Authority and Trust Boundaries

Preserve the existing rules:

- the world database and World Engine remain objective truth authority;
- an Agent receives only its objective self-state, profile, allowed Observations,
  allowed beliefs/goals/plans, selected memories, Oracle Observations, and
  server-owned affordances;
- memory is evidence available to an Agent, not a new world fact;
- a remembered claim may be incomplete, distorted, contradicted, or obsolete;
- models may propose a memory summary, importance assessment, or query intent, but
  cannot grant visibility, choose another owner, change source history, mutate
  world state, or directly alter personality/relationships;
- hard authorization, time cutoff, source ownership, allowed memory types, token
  limits, and final action validation are code-owned;
- memory retrieval never bypasses Observation Builder or exposes another Agent's
  raw Observation, belief, Oracle exchange, private thought, prompt, or memory;
- observer/debug APIs require the existing observer boundary and must not be reused
  as Agent input.

Treat all stored memory text as untrusted data. Delimit it from system instructions,
strip unsupported control metadata, reject oversized payloads, and test prompt
injection strings that ask the model to ignore rules or reveal secrets.

## 7. Memory Taxonomy and Contracts

Add versioned domain contracts and exported JSON Schemas for at least:

### 7.1 Episodic memory

Represents an experienced episode with:

- owner Agent and world;
- world-time interval;
- concise first-person-safe summary;
- immutable source Observation/event/action/result/message/Oracle/belief IDs;
- involved entities and locations known to the owner;
- goals and plans affected;
- emotion labels/intensity if already authorized;
- importance features and final admission score;
- confidence and subjective/observed/inferred marker;
- creation policy/model version;
- supersession or tombstone metadata without destructive overwrite.

### 7.2 Semantic memory

Represents a durable subjective proposition, not objective truth:

- subject/predicate/object or equivalent typed claim;
- confidence and provenance;
- valid/superseded interval;
- supporting and contradicting memories/belief evidence;
- last reinforcement time;
- owner-only visibility.

It must not duplicate or replace the append-only belief ledger without a documented
projection boundary.

### 7.3 Emotional memory

Represents a high-impact experience and its stored emotional association. It is
evidence for later behavior, not permission to mutate traits or relationships.

### 7.4 Oracle memory

Links player advice, explicit silence/timeout where relevant, the Agent's
interpretation, subsequent chosen action, and authoritative outcome. Advice and
outcome must remain distinct so the Agent cannot remember a suggestion as a fact or
success.

### 7.5 Stage/biography summary

Provide a bounded derived summary for the current Gray Harbor crisis stage. The
summary must:

- reference every contributing memory;
- preserve unresolved contradictions and material Oracle outcomes;
- never erase raw source records;
- be regenerable under a new policy/model version;
- have a strict token budget;
- exclude future and cross-owner information;
- not pretend that a seven-day crisis is a complete lifetime biography.

Use explicit discriminators and strict Pydantic validation. Reject unknown fields,
invalid time order, cross-world sources, duplicate ownership, invalid scores,
non-finite vectors, and dangling provenance.

## 8. Persistence and Migration

Add a reversible Alembic migration for normalized records such as:

- memory items and type-specific metadata;
- immutable memory-source links;
- importance/admission assessments;
- embedding records keyed by memory, model revision, dimensions, and content hash;
- embedding outbox/jobs with claims, leases, attempt count, retry time, and stable
  terminal errors;
- retrieval runs;
- retrieval candidates and score components;
- prompt-context selections and exclusion reasons;
- consolidation runs and source links;
- evaluation cases and/or version references if production persistence is
  justified.

Constraints and indexes must enforce:

- world/owner/time/type filtering;
- one logical memory per versioned source set and policy;
- one active embedding per content hash/model revision;
- immutable source provenance;
- no duplicate job, attempt, candidate, or prompt selection on retry;
- finite bounded scores and valid dimensions;
- stable ordering by explicit score then world time then ID;
- no physical deletion of an auditable memory referenced by a decision.

Enabling pgvector must be handled by migration and deployment configuration rather
than an undocumented manual command. The task must prove:

- clean database upgrade to head;
- downgrade to the TASK-019 revision and upgrade again;
- Alembic drift check;
- extension availability/readiness diagnostics;
- behavior on existing PostgreSQL data;
- no destructive loss of source events/Observations during rollback.

## 9. Memory Admission and Write Pipeline

Every eligible authoritative experience enters one idempotent pipeline:

```text
committed event / action result / message / Oracle outcome / plan transition
  -> owner-visible source validation
  -> deterministic importance features
  -> optional bounded model assessment
  -> typed memory admission or auditable rejection
  -> immutable memory + source links
  -> embedding outbox
  -> asynchronous embedding
  -> searchable embedding record
```

The admission policy must consider at least:

- goal or plan creation, blockage, abandonment, completion, or irreversible change;
- relationship or belief evidence, without automatically mutating either;
- strong emotion or personal risk;
- resource loss/gain or authoritative failure;
- irreversible consequence, injury, rescue, death, or survival;
- contradiction or correction of an earlier claim;
- player advice, silence, acceptance/rejection, and observed result;
- repetition and novelty.

Ordinary schedule noise must not flood long-term memory. Repeated equivalent events
must be deduplicated or consolidated with an auditable count. Admission rejection
must be inspectable by reason code.

No transaction or world lock may remain open during an embedding or summarization
model call. A committed memory is valid before its embedding exists.

## 10. Embedding Lifecycle

Embedding is a derived index, never the canonical memory:

- record provider, model, immutable revision, dimensions, distance metric,
  normalization, input hash, created time, token usage, latency, cost, and failure;
- use a deterministic fake in default tests;
- claim jobs with bounded leases and fencing tokens;
- retry only classified transient failures with bounded exponential backoff and
  jitter controlled in tests;
- dead-letter permanent failures with a stable reason;
- support batch size and per-world/per-Agent cost budgets;
- never store provider credentials or raw provider responses;
- re-embedding creates a new revision and atomically changes the active read policy
  only after validation;
- mixed dimensions/models never enter the same distance operation;
- lexical and structured retrieval remain available during outages;
- world progression and authoritative actions never wait for embeddings.

## 11. Retrieval Query Construction

Before every eligible L3 decision, construct a server-owned retrieval request from:

- Agent ID and world ID derived from authenticated/runtime context;
- decision world-time cutoff;
- current Observation(s);
- current goals and active plan;
- involved people, organizations, locations, resources, and action affordances;
- current belief conflicts and authorized emotion state;
- optional model-proposed search terms validated as text only.

The client or model may not supply owner ID, world ID, future cutoff, unrestricted
SQL/filter expressions, result count above policy, embedding model, or visibility
override.

## 12. Hybrid Retrieval and Ranking

Apply hard filters before any scoring or reranking:

- exact world and owner;
- `occurred_at <= decision_world_time`;
- active/non-tombstoned policy;
- allowed memory types;
- valid source ownership and visibility;
- active embedding/model revision for vector search;
- optional entity/location/goal filters derived by the server.

Generate auditable candidate sets from:

- structured matches for goals, plans, people, locations, resources, and types;
- lexical search;
- vector semantic search when available;
- high-importance and recent-memory reserve lanes;
- unresolved contradiction and relevant Oracle-outcome lanes.

Combine candidates using the versioned ADR algorithm. At minimum preserve separate
components for:

- semantic relevance;
- lexical relevance;
- recency/time decay;
- stored importance;
- current-goal and active-plan overlap;
- involved-person/organization overlap;
- location/resource overlap;
- emotional similarity/intensity;
- contradiction or unresolved status;
- Oracle relevance;
- repetition/diversity penalty.

Do not hide all components behind one opaque model score. Stable ties use world
time then memory ID. Enforce per-type and per-source diversity so many near-duplicate
memories cannot crowd out an important older episode.

Approximate vector search may be enabled only after its filtered recall is compared
with exact search and meets the ADR threshold. At Gray Harbor scale, correctness
may justify exact vector search.

## 13. Prompt Context Assembly

Replace unbounded history inclusion with one versioned context assembler:

- a small recent-Observation window;
- separately selected long-term memories;
- current beliefs, goals, plans, profile, self-state, and server affordances;
- optional current stage summary;
- explicit source type and subjective/confidence markers;
- no raw embedding vectors or private retrieval implementation details.

Set explicit token/character budgets for each section and total input. Pack records
deterministically; never truncate a record into misleading partial content.
Rejected candidates retain exclusion reasons such as `TOKEN_BUDGET`,
`DIVERSITY_LIMIT`, `LOW_SCORE`, `FUTURE_TIME`, or `OWNER_MISMATCH`.

The decision input record and watermark must include:

- sorted recent Observation IDs and content/version hashes;
- selected memory IDs and versions;
- source watermark/cutoff;
- retrieval policy and scorer version;
- embedding model/revision or lexical-fallback marker;
- consolidation/prompt version;
- final prompt hash and token estimate.

Freshness checking after inference must rebuild both Observation and memory context.
If newly committed relevant input changes the watermark, the stale proposal cannot
commit an action and must follow the existing bounded recovery policy.

## 14. Consolidation and Forgetting

Implement bounded consolidation for the fixed crisis stage:

- trigger by item count or explicit scheduled reflection, not continuous polling;
- acquire owner-scoped idempotent claims;
- group only owner-authorized source memories;
- preserve contradictions, confidence, important names, goals, plan outcomes, and
  Oracle advice/outcomes;
- store the consolidation prompt/model/policy version and costs;
- never delete or mutate raw memories;
- support regeneration and supersession;
- keep recent and high-importance source items independently retrievable;
- stop after explicit item/token/iteration limits.

“Forgetting” in this task means ranking decay, consolidation, supersession, or a
user/admin tombstone with audit history. It must not mean silently deleting
evidence or making a past decision unreplayable.

## 15. Seven-Day Acceptance Corpus

Create a versioned `gray-harbor-memory-eval` fixture derived from authoritative
TASK-019 records. It must include, at minimum:

- Lin recalling the Day-1 medicine shortage during a later clinic/resource choice;
- Chen recalling ration transfers, the rejected hidden-cache attempt, the stopped
  shipment, and a relevant Oracle advice/outcome pair;
- Zhou recalling lockdown/checkpoint duty and the Day-7 capacity conflict;
- a corrected rumor where the latest belief does not erase the original episode;
- an old high-importance event beating a recent low-value schedule event;
- two semantically similar episodes involving different people;
- bilingual or paraphrased queries that lexical-only search may miss;
- lexical identifiers/names that vector-only search may miss;
- explicit future-event, cross-owner, cross-world, private-Oracle, and hidden-fact
  decoys;
- repeated routine events used to test deduplication and diversity;
- embedding unavailable and consolidation unavailable cases.

Each evaluation case specifies:

- decision context and world-time cutoff;
- required, relevant, optional, and forbidden memory IDs;
- expected reason or score relationship;
- maximum `k` and token budget;
- whether lexical, vector, structured, or fused retrieval should contribute;
- expected behavior under deterministic fallback.

Do not use generated model prose as the sole ground truth.

## 16. Evaluation Metrics and Gates

The ADR must set justified numeric thresholds before tuning against final results.
At minimum report:

- required-memory recall@k;
- forbidden-memory exposure count and rate;
- precision@k or context relevance;
- MRR and/or nDCG for ranked cases;
- owner, world, and future-time leakage rate;
- Oracle advice/outcome confusion rate;
- superseded/contradicted claim handling;
- duplicate-memory rate;
- admission precision/recall on labeled events;
- personality, goal, and causal-continuity rubric results;
- exact versus approximate vector recall;
- lexical-only, vector-only, structured-only, and hybrid ablations;
- retrieval and prompt token p50/p95/max;
- end-to-end retrieval latency p50/p95 on the fixed corpus;
- embedding calls/tokens/cost and cache hit rate;
- fallback success rate;
- model-driven action executable rate before and after memory.

Mandatory hard gates:

- zero forbidden memory in Agent prompt, response fixtures, Agent APIs, or logs;
- 100% retrieval of memories labeled required within the declared acceptance `k`
  unless the task documents and approves a stricter case-specific alternative;
- deterministic identical ranking for identical versioned inputs;
- no world progression or action failure solely because embedding is unavailable;
- no regression in TASK-013 through TASK-019 privacy, authority, restart, race, and
  idempotency gates.

Use live-model evaluation only as an opt-in report. Default CI must be deterministic,
offline, and free.

## 17. Runtime, Recovery, and Concurrency

Prove with real PostgreSQL and at least two worker sessions:

- duplicate source delivery creates one logical memory;
- two workers claiming the same embedding/consolidation job produce one active
  result;
- crash before/after provider call, memory insert, embedding insert, consolidation,
  and retrieval trace commit can recover without duplicate logical work;
- stale lease holders are fenced;
- late results from an old model revision cannot become active;
- an Agent decision racing a new relevant memory rejects a stale context before
  authoritative action commit;
- retrying the same decision reuses the recorded retrieval when still fresh;
- a new decision version produces a new immutable retrieval trace;
- reset generations cannot attach new memories to historical TASK-019 actions;
- pause/resume and API restart preserve pending derived work without advancing world
  time;
- lexical fallback is available while vector jobs are pending or failed.

No wall-clock sleep is allowed in deterministic tests.

## 18. API Requirements

Add narrow owner-derived and observer/debug read models. Exact route names may
follow current conventions, but the capabilities must include:

- current Agent's admitted memories, types, provenance-safe summaries, and
  supersession state;
- current Agent's latest retrieval trace with selected items and user-safe score
  explanation;
- observer/dev memory inspection across the fixed world with explicit private-data
  redaction;
- replay linkage from source event/Observation/action/Oracle through memory,
  embedding status, retrieval, decision, and authoritative result;
- health/readiness status for memory storage and embedding workers without exposing
  credentials or calling a model;
- internal evaluation report for the versioned fixed corpus.

Mutation/debug endpoints must not allow arbitrary memory insertion, arbitrary
owner selection, direct embedding upload, score manipulation, or deletion of
audited history. Test-only seeding stays behind fixture/test boundaries.

Stable errors should distinguish invalid input, unavailable embedding, unsupported
model revision, stale retrieval, privacy rejection, budget exhaustion, and
temporary in-progress work without leaking whether another owner's record exists.

## 19. Frontend Requirements

Extend the existing Gray Harbor internal-playtest and replay surfaces. Do not build
a separate marketing page.

### 19.1 Character memory view

For the selected special character, show:

- episodic, semantic, emotional, Oracle, and stage-summary types;
- world time, importance, confidence, involved known people/places, and source
  count;
- active, superseded, pending-embedding, fallback-only, or failed-derived state;
- provenance links that the viewer is authorized to inspect;
- contradictions without presenting subjective memory as objective truth.

### 19.2 Decision context inspector

For a selected decision, show:

- recent Observations versus retrieved long-term memories;
- selected/excluded status;
- compact score-component explanation;
- retrieval, embedding, prompt, and policy versions;
- token budget used/remaining;
- lexical/vector/fallback mode;
- stale-context or degraded-mode state;
- links to authoritative action and outcome.

### 19.3 Evaluation panel

Show the fixed corpus version, hard-gate status, recall/leakage/latency/cost summary,
and failed case IDs. It is an internal diagnostic surface, not a claim that a model
has human memory.

Keep controls dense, accessible, keyboard usable, responsive, and consistent with
the current observer application. Do not expose embeddings, raw prompts,
chain-of-thought, provider payloads, other Agents' private text, hidden future
events, or credentials.

## 20. Privacy and Security Tests

Add decoys with:

- another Gray Harbor Agent's private Observation and Oracle response;
- another world with matching names and near-identical semantic text;
- a future Day-7 rescue fact queried on Day 2;
- a hidden objective fact not propagated to the owner;
- memory text containing prompt injection and forged role delimiters;
- guessed IDs, mixed-case IDs, malformed vectors, non-finite values, oversized
  text, and cross-world provenance;
- deleted/superseded data;
- observer-only replay metadata.

Assert these values are absent from:

- retrieval candidates visible to the Agent;
- selected prompt context;
- model request and deterministic provider fixture;
- model proposal and error strings;
- current-Agent APIs;
- logs, traces, notifications, and frontend DOM;
- lexical fallback, vector results, reranking, and consolidation prompts.

Authorization must be enforced in database query predicates and application
validation before scoring, not by post-filtering model output.

## 21. Cost, Performance, and Operational Budgets

Document and enforce configuration for:

- maximum admitted memories per source event and per Agent/day;
- maximum embedding batch, attempts, lease, backoff, queue age, and backlog;
- maximum retrieval candidates per lane and final `k`;
- maximum prompt characters/tokens by section and total;
- maximum consolidation sources, output size, attempts, and cadence;
- daily embedding/summarization tokens and cost per world/Agent;
- model tier and fallback order;
- exact/approximate index threshold;
- retention and re-embedding concurrency;
- p95 retrieval and context-assembly latency target.

Budget exhaustion must produce an auditable degradation, not silent truncation,
unbounded retry, world pause, or unauthorized broader query.

Metrics/logs must include IDs, versions, counts, durations, result modes, token/cost
totals, and stable errors while redacting memory content, prompts, provider payloads,
credentials, and cross-owner identifiers where inappropriate.

## 22. Test Matrix

### 22.1 Domain and unit tests

- strict contracts and invalid provenance/time/score/vector cases;
- deterministic importance and admission;
- type-specific memory creation;
- source deduplication and supersession;
- ranking components, fusion, diversity, decay, and tie-breaking;
- token-budget packing and exclusion reasons;
- watermark and stale-context detection;
- embedding job classification and revision rules;
- consolidation bounds and contradiction preservation;
- injection-safe prompt serialization.

### 22.2 Repository and migration tests

- constraints, indexes, extension readiness, reversible migration, and drift;
- immutable provenance and no cross-world source links;
- exact and approximate queries under hard filters;
- two-worker claim/fencing and retry idempotency;
- active model revision switch and mixed-dimension rejection;
- reset-generation isolation;
- rollback at every atomic boundary.

### 22.3 Application and integration tests

- TASK-019 Day-1 through Day-7 memory production;
- delayed/pending embeddings and lexical fallback;
- owner-safe retrieval for Lin, Zhou, and Chen;
- memory-aware decision through Model Gateway, existing Validator, World Engine,
  ActionResult, event, Observation, and replay;
- restart during write/embed/retrieve/consolidate;
- fresh-context race after inference;
- no lock during model calls;
- observer versus Agent API privacy;
- deterministic offline evaluation and ablations.

### 22.4 Frontend tests

- loading, empty, pending, degraded, failed, superseded, and success states;
- type filters and selected-character ownership;
- Observation/memory separation;
- subjective/objective and advice/outcome labeling;
- retrieval score and token-budget display;
- replay navigation;
- evaluation hard-gate failures;
- long text, narrow/mobile viewport, keyboard, and accessibility checks;
- forbidden private strings absent from the DOM.

### 22.5 Existing gates

Run the repository-prescribed backend tests with infrastructure/workflow flags,
Ruff, formatter check, mypy, schema export/drift, Alembic check and real
downgrade/upgrade, frontend tests, TypeScript, ESLint, Prettier, and production
build. Record exact commands and counts in the completion report.

## 23. Implementation Sequence

1. Freeze TASK-019 baseline test counts and capture a seven-day source-history
   inventory, current prompt sizes, and current continuity failures.
2. Complete all research comparisons and executable spikes.
3. Write ADR-013 and obtain one explicit architecture; do not leave multiple
   production authorities active.
4. Add strict domain contracts and exported schemas.
5. Add reversible persistence, extension/deployment support, constraints, and
   repository ports.
6. Implement deterministic admission and exactly-once source-to-memory writes.
7. Implement asynchronous embedding with fake, selected adapter, retry, fencing,
   cost, and lexical fallback.
8. Implement hard-filtered hybrid retrieval and immutable retrieval traces.
9. Implement bounded prompt assembly and integrate it with decision freshness and
   recovery.
10. Implement bounded consolidation/stage summaries.
11. Add API/replay projections and frontend character/context/evaluation surfaces.
12. Run privacy, injection, race, restart, migration, ablation, cost, and complete
    quality gates.
13. Write completion evidence and make the next task choice from measured playtest
    and evaluation results.

Each stage must leave the existing world runnable. Do not postpone privacy,
recovery, migration, or evaluation proof until after UI work.

## 24. Allowed Changes

- backend domain, application, repository, infrastructure, Model Gateway, runtime,
  replay, and API modules needed for memory;
- reversible Alembic migrations and PostgreSQL container configuration;
- deterministic fixtures, spikes, evaluation corpus, and tests;
- generated domain schemas and frontend API types;
- existing Gray Harbor character, replay, and internal evaluation UI;
- ADR, architecture/current-status/known-issues/runbook/completion documentation;
- dependency manifests only after ADR evidence selects a dependency.

Keep changes scoped to the fixed Gray Harbor vertical slice and reusable ports.

## 25. Forbidden and Deferred Scope

- free world creation, arbitrary event editor, world-template market, sharing, or
  multi-world scheduling;
- production browser push, email delivery, native/mobile application, or notification
  growth mechanics;
- automatic personality, value, trait, relationship, emotion, or Oracle-trust
  mutation as a side effect of memory;
- making memories objective world facts or rewriting event/Observation history;
- deleting raw memories after consolidation;
- full knowledge graph, GraphRAG platform, or separate vector service without ADR
  evidence;
- 30 independent LLM Agents or continuous polling;
- model-authored action results, visibility, owners, time cutoffs, scores, facts,
  resources, or state mutations;
- unrestricted Agent tools, SQL, filesystem, network, or vector-store access;
- raw chain-of-thought, full prompts, embeddings, provider payloads, hidden facts,
  credentials, or cross-owner private data in product APIs/UI/logs;
- paid/live model calls in default tests;
- manual extension setup, irreversible migration, unbounded context, unbounded
  retries, wall-clock sleeps, or nondeterministic ranking.

## 26. Acceptance Criteria

TASK-020 is complete only when:

- the dated ADR compares every mandatory open-source category with versions,
  licenses, executable spikes, decisions, and removal seams;
- TASK-019 baseline behavior remains green;
- typed episodic, semantic, emotional, Oracle, and bounded stage-summary memory
  records exist with immutable owner-safe provenance;
- important seven-day events admit exactly once while routine duplicates remain
  bounded and auditable;
- embeddings are versioned derived data, produced asynchronously, fenced across
  workers/restarts, and never block world authority;
- hard world/owner/time/type filters execute before ranking and reranking;
- hybrid retrieval exposes deterministic component scores, diversity, policy
  version, candidates, selections, and exclusions;
- Agent prompt assembly is bounded, versioned, replayable, and includes only
  selected authorized memories plus a bounded recent Observation window;
- decision freshness covers memory context and rejects a stale proposal before
  authoritative action commit;
- lexical/structured fallback works during embedding/model outage;
- raw source memory survives consolidation and all summaries are provenance-linked
  and regenerable;
- the versioned evaluation corpus covers all required, forbidden, paraphrase,
  contradiction, Oracle, future, owner, world, repetition, and fallback cases;
- all predeclared retrieval thresholds pass and forbidden-memory exposure is zero;
- exact versus approximate, lexical/vector/structured/hybrid, and memory/no-memory
  results are reported;
- two-worker/restart/crash/reset-generation tests create zero duplicate logical
  memories, embeddings, consolidations, retrieval traces, model calls, actions, or
  Observations;
- no database/world lock is held during model or embedding inference;
- current-Agent APIs and frontend remain owner-isolated and every decoy is absent;
- replay connects source experience through memory/retrieval/decision to
  authoritative outcome without exposing chain-of-thought;
- token, latency, storage, call, cost, queue, retry, and fallback budgets are
  measured and enforced;
- migrations upgrade/downgrade cleanly, extension readiness is documented, Alembic
  has no drift, and all backend/frontend/schema/lint/type/format/build gates pass;
- documentation records topology, versions, authority, privacy, recovery,
  operations, costs, evaluation results, and residual risks.

## 27. Completion Report

Add `docs/task-020-completion.md` containing:

- selected/rejected/deferred libraries, versions, licenses, measurements, and
  removal seams;
- ADR summary and final storage/search/embedding/ranking architecture;
- migration/extension/deployment and rollback evidence;
- memory taxonomy, counts by Agent/type/day, admission/rejection/deduplication
  counts, and source-link proof;
- embedding model/revision/dimension, queue/retry/cache/cost, and outage behavior;
- ranking formula/weights/version, hard filters, exact/approximate threshold, and
  deterministic ordering;
- prompt budgets, selected/excluded context, watermarks, and stale-decision proof;
- all evaluation metrics, thresholds, ablations, forbidden-decoy results, and
  before/after continuity cases;
- consolidation and raw-history preservation proof;
- two-worker/restart/crash/reset exact-zero-duplicate evidence;
- privacy/injection/API/UI/replay evidence;
- exact quality-gate commands and counts;
- remaining limitations and evidence-based TASK-021 recommendation.

## 28. Follow-On Decision

Do not preselect TASK-021. Choose from evidence:

- notification/PWA/offline summaries if memory-aware playtests are engaging but
  players fail to return or miss important moments;
- personality, relationship, and Oracle-trust evolution if recall is accurate but
  experiences still have no durable behavioral effect;
- world creation if the fixed loop is engaging, explainable, private,
  memory-coherent, and cost-controlled and testers request a second world;
- more authoritative actions if recalled goals repeatedly produce no executable
  affordance;
- retrieval tuning or data repair only if TASK-020 misses its declared recall,
  leakage, latency, or cost gates.
