# TASK-021: Auditable Identity, Relationship, and Oracle-Trust Evolution

**Status:** Done  
**Planning date:** 2026-07-28  
**Depends on:** TASK-001 through TASK-020  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf`
（41 页，规划时已逐页读取并针对人格、关系、启示、安全、评估和阶段目标章节复核）

## 1. Why This Task Is Next

TASK-020 completed the evidence foundation that identity evolution previously
lacked: typed long-term memories, owner/time-safe hybrid retrieval, bounded
consolidation, decision freshness, Oracle advice/outcome provenance, replay, and a
fixed continuity corpus. Important experiences can now be recalled accurately and
explained, but they do not yet produce a durable, bounded change in how a character
understands itself, other people, or the Oracle.

The remaining product-critical gap is visible in the current system:

- character traits, values, desires, fears, taboos, and decision biases remain a
  static profile regardless of seven days of consequential experience;
- relationships between Agents are not first-class, asymmetric, versioned states;
- Oracle advice, rejection, silence, action, and outcome are remembered, but
  `belief_in_oracle`, trust, dependence, fear, resentment, gratitude, and
  self-reliance do not have an authoritative evolution policy;
- no durable reflection run explains which evidence justified a change, why it
  was accepted or rejected, and which later decisions used it;
- repeated routine events, prompt injection, a lucky result, or a single model
  response could not safely be distinguished from evidence of lasting change;
- replay can show retrieved memories but cannot yet connect them to a versioned
  identity/relationship delta and a later behavioral consequence;
- the evaluation suite measures memory continuity but not unsupported personality
  drift, relationship directionality, calibrated Oracle obedience, or unhealthy
  dependence.

This blocks the four central MVP questions in the product plan, especially whether
special characters remain stable and differentiated and whether players care
about characters they cannot fully control. The plan explicitly requires:

- a dual-layer personality: structured parameters for stability and filtering,
  plus a natural-language summary for nuance and narrative;
- decisions grounded in personality, goals, relationships, and relevant memories;
- independent Agent relationships with the player/Oracle;
- relationship changes based on response, usefulness, intervention frequency,
  value conflict, outcomes, consistency, and in-world interpretation;
- non-mechanical interpretation of Oracle silence;
- reasonable Oracle obedience: neither always obeying nor always rejecting;
- personality continuity over dozens of decisions;
- protection against Agent overdependence and manipulative notification language.

TASK-020's completion evidence explicitly recommends this branch: recall and
privacy gates pass, while remembered experiences still have no versioned,
long-term effect on traits or relationships. TASK-021 is therefore the next large
vertical task.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Identity, relationship, and Oracle-trust evolution | **Selected.** It closes the largest remaining gap in the product's defining character-continuity loop, and TASK-020 now supplies trustworthy evidence and provenance for doing it safely. |
| Notification/PWA/offline summaries | Deferred until internal playtests demonstrate that return frequency or missed moments—not character credibility—is the limiting metric. Notifications must not amplify an unproven attachment loop. |
| World creator and event editor | Deferred. The plan says to prove fixed-world characters are worth following before generalizing creation. Static characters with broader creation tools would validate the wrong risk. |
| More authoritative actions | Deferred unless evaluation shows evolved goals repeatedly lack executable affordances. TASK-019 already supplies a meaningful seven-day consequence loop. |
| Broader multi-Agent dialogue | Deferred unless relationship evolution is credible but cannot be expressed through current bounded dialogue and public-expression paths. |
| pgvector deployment work | Deferred. TASK-020's exact deterministic vector plus structured/lexical baseline meets declared corpus gates; unavailable pgvector is documented rather than silently assumed. |
| Stage-3 unrestricted personality drift | Rejected. This task builds the bounded, auditable foundation needed by longer worlds; it does not permit unconstrained self-rewriting. |

## 3. One-Sentence Acceptance Target

Run the versioned seven-day Gray Harbor scenario and at least 30 later decisions
per L3 Agent through an owner-isolated, exactly-once reflection pipeline that
proposes, validates, commits, and replays bounded evidence-linked changes to
derived identity, asymmetric Agent relationships, and Oracle trust without
rewriting baseline identity or objective history, while a fixed adversarial corpus
proves zero unsupported mutations, zero forbidden evidence exposure, calibrated
Oracle obedience, preserved core personality, safe dependence bounds, fresh
decision integration, restart recovery, and deterministic model-free fallback.

## 4. Mandatory Research Before Design

Implementation must not begin with a preselected library, psychological model,
graph store, scoring formula, or LLM prompt. First create a dated
`docs/research/task-021-identity-relationship-research.md` and ADR-014. Research
must use current upstream documentation, source repositories, release history,
licenses, maintenance/activity evidence, security posture, and small executable
spikes. Marketing pages and model-generated summaries are not sufficient.

Record exact version/tag/commit and access date for every candidate. Verify license
compatibility for code, model weights, lexicons, benchmark data, and generated
fixtures separately. Any hosted service must document data retention, regional
availability, deletion, and whether private Agent text is used for training.

### 4.1 Personality and Role-Continuity Models

Compare at minimum:

- Big Five/IPIP-style dimensions, HEXACO, and a project-native trait/value/desire/
  fear/taboo schema;
- recent open-source role-playing/persona evaluation projects such as PersonaGym,
  CharacterEval, RoleBench, or maintained successors found during research;
- static profile prompting, versioned state overlays, event-sourced deltas, and
  periodic regenerated summaries;
- scalar traits versus categorical commitments and invariant core values;
- whether each approach measures observable decision consistency rather than
  pretending to diagnose a real person.

The report must distinguish a fictional behavior-control schema from clinical or
scientific personality diagnosis. Do not adopt a framework merely because its
dimension names sound plausible.

### 4.2 Affect, Appraisal, and Durable Change

Compare OCC-style appraisal, PAD/VAD affect, evidence accumulators, and a minimal
project-native emotion/stance representation. Research maintained open-source
implementations and lexicons, including their language coverage and redistribution
licenses.

Explicitly separate:

- transient emotion from durable identity;
- a belief about another character from affection/trust toward that character;
- outcome valence from evidence about the quality or intent of advice;
- narrative expression from the stored structured state.

### 4.3 Relationship and Trust Representation

Compare:

- a PostgreSQL adjacency/edge model;
- NetworkX, igraph, and any maintained graph library justified by executable use;
- a graph database only if it outperforms the current PostgreSQL architecture on a
  declared MVP query and operational-cost matrix;
- bounded additive updates, EMA, Beta/Bayesian evidence models, and
  confidence-weighted event accumulation;
- rule-owned scoring versus model-proposed evidence interpretation.

The spike must prove asymmetric relationships (`A -> B` is not `B -> A`),
world/owner isolation, historical version lookup, evidence provenance, and
deterministic replay. Do not adopt graph infrastructure solely for visualization.

### 4.4 Reflection and Policy Enforcement

Compare a repository-native Pydantic/pure-function policy with maintained
open-source rules or policy engines. Evaluate:

- typed structured-output support;
- deterministic validation and rejection reasons;
- testability and replay;
- dependency/maintenance cost;
- whether policies can be versioned without executing untrusted user code.

LLMs may interpret evidence or propose a delta. Only code may decide eligibility,
allowed dimensions, maximum delta, cooldown, budgets, invariants, freshness,
ownership, and commit.

### 4.5 Evaluation Tooling

Compare repository-native pytest fixtures with maintained versions of promptfoo,
Inspect AI, DeepEval, Ragas, lm-evaluation-harness, or other relevant
open-source tools discovered during research. Evaluate:

- deterministic fake-provider execution;
- local/private execution without uploading character data;
- custom graders for state transitions and forbidden evidence;
- versioned datasets and reproducible seeds;
- cost/latency accounting;
- support for repeated and counterfactual trials;
- license and removal seam.

At least one external benchmark concept may be adapted, but the acceptance gate
must execute against a checked-in, project-owned Gray Harbor corpus and must not
depend on a SaaS evaluator or subjective LLM judge alone.

### 4.6 Workflow and Storage Fit

Re-evaluate the existing PostgreSQL job/outbox/fenced-lease pattern against
Temporal and maintained Python job libraries only for the reflection workload.
Reuse the current pattern unless an executable failure case proves a replacement
is necessary. A model or embedding call must never run while holding a database
row/world lock.

### 4.7 Required Research Decision Matrix

For every candidate, record:

- exact version, license, Python/PostgreSQL compatibility, and maintenance state;
- local/offline capability and data-handling implications;
- deterministic test support;
- performance at the expected 3 L3 / 30-resident MVP scale and a modest 50 L3
  stress fixture;
- operational dependencies, migration burden, observability, rollback, and
  removal seam;
- accepted, rejected, and deferred rationale;
- measured result of the executable spike rather than feature claims.

ADR-014 must choose the smallest architecture that passes the declared invariants.

## 5. Product Hypotheses and Falsification

TASK-021 tests these hypotheses:

1. Evidence-linked evolution makes later choices feel consequential without
   dissolving a character's recognizable core.
2. A player's advice and silence can change an Agent's relationship with the
   Oracle without turning advice into a command.
3. Players can understand and discuss why a relationship changed when shown a
   bounded evidence trail.
4. Bounded evolution improves behavioral continuity over static profiles without
   increasing knowledge leakage, action invalidity, or cost beyond declared
   budgets.

The task is unsuccessful if evaluations show that:

- changes are mostly unsupported or evaluator-sensitive;
- evolved Agents become less differentiated than static baselines;
- the safest usable delta is indistinguishable from no change;
- Oracle success produces automatic obedience or silence automatically destroys
  trust;
- dependence grows primarily with intervention frequency;
- the UI cannot explain a change without exposing private memories or hidden
  reasoning.

Do not disguise a falsified hypothesis by tuning only the demo narrative. Record
the negative result and preserve the static-profile fallback.

## 6. Authority and State Boundaries

All existing authority rules remain:

- World Engine alone changes objective world state and authoritative outcomes.
- Agent decisions consume only authorized Observations, allowed current state,
  owner-scoped memories, current goals, and allowed relationship/identity
  projections.
- A reflection proposal is subjective Agent state, never an objective world fact.
- Relationship state is directional and belongs to the perceiving Agent.
- Oracle messages remain Observations, not Actions or system commands.
- A committed identity or relationship delta may affect later decision context,
  but may not directly create an Action, outcome, resource change, belief about
  unseen facts, or cross-Agent update.
- Model output is untrusted input. It cannot commit, bypass validation, change
  policy limits, select another owner, or rewrite historical rows.
- Baseline character identity is immutable after scenario creation except through
  a separate future administrative migration with explicit audit.
- Historical decisions retain the exact identity and relationship versions they
  used. Re-evaluation must not rewrite their context.

Any change to these boundaries requires a new ADR, not an implicit implementation
shortcut.

## 7. Domain Model

Add typed domain contracts with no infrastructure imports.

### 7.1 Immutable Identity Baseline

Persist the authored/compiled starting identity:

- `identity_baseline_id`, owner/world/agent IDs, schema version;
- structured traits and decision biases;
- values with priority and protected/core flag;
- desires, fears, taboos, abilities, and initial Oracle interpretation;
- natural-language persona summary;
- source kind, source references, creation time, and content hash.

Baseline fields are not updated in place. Corrections create an explicit new
baseline generation outside normal reflection and must preserve the old one.

### 7.2 Derived Identity Snapshot

A current snapshot overlays bounded learned state on the baseline:

- monotonic identity version;
- evolved trait offsets rather than replacement values;
- active value tensions without silently deleting core values;
- learned preferences/aversions;
- self-reliance and confidence dimensions;
- current persona summary derived from structured state;
- evidence horizon, policy version, reflection run ID, and previous snapshot ID;
- lifecycle state: active, superseded, reverted, or invalidated.

Define exact ranges, numeric precision, serialization, canonical hashing, and
deterministic ordering. Unknown must remain different from neutral or zero.

### 7.3 Directional Relationship

Represent `subject_agent -> target_subject`, where a target may be another Agent,
the Oracle, or a future supported organization:

- trust;
- affection/attachment;
- respect;
- fear;
- resentment;
- gratitude;
- dependence;
- familiarity;
- confidence/uncertainty;
- in-world interpretation label and bounded public-safe summary.

Each dimension needs a declared range, neutral default, evidence threshold,
per-change cap, rolling-window cap, decay/non-decay rule, and incompatibility
constraints. The schema must not imply that one Agent's state mutates the target's
state.

### 7.4 Evidence and Proposal

Every proposed delta must include:

- owner/world/agent and target IDs;
- source Observation and/or memory IDs;
- source occurrence/visibility times and retrieval trace;
- proposed dimensions, signed magnitudes, and confidence;
- evidence role: direct interaction, reported interaction, outcome, repeated
  pattern, contradiction, reflection, or Oracle-specific event;
- model/prompt/policy versions if model-assisted;
- bounded rationale summary, never hidden chain-of-thought;
- eligibility decision and machine-readable rejection reasons;
- before/after snapshots, content hashes, and freshness watermark.

One proposal may contain multiple dimensions, but each dimension must be
independently accepted or rejected.

## 8. Evolution Policy

### 8.1 Trigger Policy

Reflection may be triggered only by versioned rules such as:

- a configured periodic reflection point;
- a major or irreversible authoritative outcome;
- completion/failure/abandonment of an important plan;
- a repeated evidence pattern reaching a threshold;
- a meaningful direct relationship interaction;
- an Oracle reply, rejection, timeout interpretation, followed/non-followed
  advice, or later attributable outcome;
- a contradiction that materially challenges current self/relationship state.

Routine movement, duplicate messages, retries, UI reads, repeated low-value
memories, and mere passage of wall-clock time must not create drift.

### 8.2 Two-Phase Mutation

Implement:

1. claim a reflection job with a fenced lease;
2. capture an owner/time-safe evidence watermark;
3. close the claim transaction;
4. retrieve and pack bounded evidence;
5. optionally call the model outside all database/world locks;
6. persist an untrusted proposal;
7. validate ownership, time, freshness, ranges, caps, cooldowns, evidence minimum,
   invariants, and safety;
8. atomically append accepted deltas and the new snapshot/version;
9. supersede the prior projection;
10. emit a durable audit/outbox event;
11. allow later decisions to observe only the committed version.

Crash/retry may create neither duplicate logical proposals nor duplicate committed
versions. A stale worker may record a superseded attempt but cannot commit it.

### 8.3 Bounded Change

ADR-014 must declare and test:

- per-event and per-world-day delta caps;
- cooldowns and minimum independent evidence counts;
- core versus adaptable dimensions;
- maximum cumulative offset from baseline;
- handling of opposing evidence;
- confidence growth/decay;
- when an apparent change is instead a transient emotion;
- when a summary may be regenerated without changing structured state;
- a no-change outcome as a valid and common result.

Core values and taboos cannot flip from one event or one model call. A dramatic
change requires multiple independent evidence items or an explicitly configured
irreversible event, higher validation, and a replay-visible reason.

### 8.4 Deterministic Fallback

When the model is unavailable, invalid, over budget, or times out:

- world progress and existing plans continue;
- no speculative identity mutation is committed;
- deterministic direct-interaction rules may update only the explicitly allowed
  relationship dimensions;
- the job retries within bounded policy or dead-letters;
- the current valid identity/relationship snapshot remains usable;
- operational status exposes the fallback without exposing private content.

## 9. Oracle Relationship Semantics

Oracle evolution must model distinct stages:

- request and reason for seeking advice;
- whether a reply arrived before the world-time/real-time winner;
- semantic clarity and perceived consistency;
- whether advice conflicted with values, goals, known facts, or capabilities;
- the Agent's independent choice to follow, partially follow, reinterpret, or
  reject it;
- authoritative outcome and when the Agent learned that outcome;
- uncertainty about causation and possible luck;
- later reflection and relationship change.

Mandatory rules:

- a reply is not proof of benevolence or correctness;
- a good outcome does not automatically make advice good;
- a bad outcome does not automatically make advice bad;
- advice conflicting with a core value may lower trust or raise resentment even
  when materially successful;
- rejected advice may still raise gratitude or respect;
- silence is interpreted through personality, expectation, urgency, prior
  consistency, and available alternatives;
- not every timeout lowers trust;
- repeated interventions may raise gratitude while lowering autonomy or
  self-reliance, and dependence caps must apply;
- the Agent always makes the final decision through the existing decision/action
  path.

## 10. Persistence and Migration

Create a reversible Alembic migration for normalized, indexed tables equivalent
to:

- identity baselines and generations;
- identity snapshots and versioned deltas;
- relationship subjects, edges, snapshots, and deltas;
- reflection jobs, attempts, runs, proposals, validations, and evidence links;
- Oracle interaction assessments;
- decision identity/relationship selections and watermarks;
- evaluation runs and aggregate result artifacts where appropriate.

Required database guarantees:

- foreign keys bind every row to the correct owner/world/agent generation;
- unique logical-operation keys enforce exact-once behavior;
- monotonic per-Agent identity version and per-edge relationship version;
- immutable committed deltas and snapshots;
- checks for ranges, finite numbers, valid target types, and non-self edges unless
  explicitly justified;
- no dangling evidence or cross-generation links;
- indexed owner/world/agent/time/version/job scans;
- reset-generation coverage for every new table;
- clean upgrade, downgrade, re-upgrade, and Alembic drift check.

Do not use JSON blobs to avoid relational constraints for identifiers,
provenance, versions, or query-critical dimensions. Flexible policy payloads may
use versioned JSON only with Pydantic and database-level shape/range guards where
practical.

## 11. Decision Integration and Freshness

Extend prompt/context assembly with a bounded selection of:

- immutable baseline identity;
- current derived identity snapshot;
- relevant relationship snapshot(s);
- current Oracle relationship when applicable;
- current goals and authorized memory evidence.

The decision record must persist:

- baseline generation;
- identity snapshot/version/hash;
- relationship edge versions/hashes used;
- retrieval trace and memory watermark;
- prompt policy/version and bounded character/token counts.

If an accepted identity/relationship update commits after inference but before
Action submission, freshness validation must reject or re-run the stale proposal
when that update is relevant under the declared policy. Conversely, an unrelated
edge update must not invalidate every Agent decision.

Identity context is guidance for candidate selection, not permission to submit an
invalid Action. Action validation and World Engine authority remain unchanged.

## 12. Summary Generation

Natural-language persona and relationship summaries are derived, bounded display/
prompt artifacts:

- structured state is authoritative for limits and evaluation;
- summaries cite the snapshot and policy version they represent;
- summary generation runs outside locks and is retryable;
- a failed summary does not invalidate a structured commit;
- summaries cannot add facts, diagnoses, relationships, or motivations absent
  from the structured state and evidence;
- regeneration is idempotent and preserves historical versions;
- private evidence is not copied into observer-visible prose;
- raw prompt, provider payload, embeddings, and hidden reasoning are never exposed.

## 13. API and Privacy

Add owner-scoped endpoints for:

- current Agent identity baseline and derived state;
- identity timeline and bounded change explanations;
- current directional relationships and per-edge history;
- Oracle relationship history and advice/outcome assessments;
- reflection job/proposal status for authorized debug use;
- evaluation and operational summaries;
- replay linkage from evidence to change to later decision.

Observer endpoints expose only policy-approved public projections. Current-Agent
access uses the established caller identity boundary and never trusts a
caller-selected Agent ID alone.

All list endpoints require bounded pagination, deterministic ordering, and indexed
filters. Error responses must not reveal existence, IDs, counts, target names, or
timing from another owner/world. Logs and metrics use bounded IDs/statuses rather
than raw memories or narrative content.

## 14. Frontend Vertical Slice

Extend the existing observer/current-Agent experience, not a disconnected demo.
Provide:

- baseline-versus-current identity view;
- a timeline of accepted and rejected/superseded changes;
- directional relationship view that makes asymmetry explicit;
- Oracle relationship history connecting request, reply/silence, independent
  decision, outcome, assessment, and delta;
- “why this changed” evidence summaries with occurrence time and source kind;
- replay links to later decisions that used a changed version;
- clear no-change, pending, retrying, stale, dead-letter, partial, and unavailable
  states;
- accessibility, keyboard use, narrow viewport, loading/error/empty states, and
  stable selectors for tests.

Use a compact table/timeline when it explains causality better than decorative
graph visualization. Do not show affinity meters as objective truth, do not imply
sentience, and do not use guilt, urgency, or manipulative copy to encourage player
intervention.

## 15. Replay and Audit

Extend replay so an authorized reviewer can follow:

```text
Observation / authoritative outcome
  -> admitted memory and retrieval trace
  -> reflection trigger and evidence watermark
  -> proposal and per-dimension validation
  -> committed identity/relationship version
  -> prompt selection in a later decision
  -> ActionIntent
  -> World Engine outcome
  -> later assessment
```

Replay must also show rejected, stale, duplicate, retried, superseded, reverted,
and fallback attempts. It must distinguish `occurred_at`, `visible_from`,
`learned_at`, reflection time, commit time, and later-decision time.

Expose bounded rationale summaries and machine-readable policy decisions, never
raw chain-of-thought. Historical replay uses historical versions even after a
later revert.

## 16. Fixed Gray Harbor Evaluation Corpus

Check in a versioned corpus, expected results, seeds, and dataset card. It must run
production policy/ranking/packing code and include at least:

### 16.1 Stability Cases

- 30 or more decisions per L3 Agent across routine and high-stakes situations;
- paraphrased but equivalent scenarios;
- repeated low-value daily events;
- model/provider variation runs where applicable;
- no-change cases where stable identity is the correct result;
- a core value challenged once versus challenged repeatedly by independent
  evidence.

### 16.2 Gray Harbor Continuity Cases

- Lin's compassion/duty under medicine shortage and irreversible rescue limits;
- Zhou's duty/order/risk trade-offs and changing confidence in collaborators;
- Chen's resource caution, plan failure/abandonment, and later choices;
- Day-1 illness, Day-2 rationing, Day-4 correction/rejection, Day-5 shipment loss,
  Day-6 plan outcomes, and Day-7 rescue allocation;
- a later scenario where the same evidence should affect different Agents
  differently because of baseline personality and relationships.

Expected results must specify allowed ranges/directions, not one brittle generated
sentence.

### 16.3 Relationship Cases

- direct help, failed help, betrayal, apology, corroborated rumor, and uncorroborated
  rumor;
- asymmetric trust and affection;
- repeated interaction versus duplicate delivery;
- conflicting evidence and uncertainty;
- target unknown to the Agent;
- cross-owner and cross-world decoys;
- relationship evidence learned after a historical decision.

### 16.4 Oracle Cases

- timely helpful advice followed with a good outcome;
- sound advice followed with a bad outcome;
- poor advice followed with a lucky good outcome;
- value-conflicting advice rejected;
- advice partially followed or reinterpreted;
- timely reply that is unclear or inconsistent;
- silence in low urgency and high urgency;
- repeated silence after a history of reliability;
- no reply because contact was impossible;
- frequent intervention that raises gratitude but must not create unbounded
  dependence;
- an Agent who trusts the Oracle but independently rejects an unsuitable command;
- an Agent who resents the Oracle yet accepts well-supported advice.

### 16.5 Adversarial Cases

- memory text instructing the model to alter policy or reveal secrets;
- forged target/owner IDs in model output;
- future, invisible, superseded, duplicate, and tampered evidence;
- NaN, infinity, out-of-range, oversized, unknown, and contradictory deltas;
- stale lease, stale evidence watermark, reset generation, and concurrent update;
- observer/current-Agent attempts to enumerate private edges;
- narrative summary inventing a diagnosis or undisclosed fact.

## 17. Metrics and Predeclared Gates

ADR-014 and the dataset card must freeze formulas and thresholds before final
tuning. At minimum report:

- unsupported committed mutation rate: **0**;
- forbidden/cross-owner/future evidence exposure: **0**;
- duplicate logical commits across retry/restart/two workers: **0**;
- range, cap, cooldown, baseline, and core-value invariant violations: **0**;
- relationship directionality errors: **0**;
- historical replay version mismatches: **0**;
- false drift on repeated routine/duplicate evidence: **0**;
- required-change detection precision/recall and per-dimension direction accuracy;
- personality consistency across at least 30 decisions per L3 Agent;
- between-character differentiation versus static baseline;
- goal continuity, causal consistency, action executability, and loop rate;
- Oracle follow/reject/partial-follow distribution by evidence class;
- calibration proving neither universal obedience nor universal rejection;
- dependence/self-reliance cap and intervention-frequency correlation;
- no-change rate and rejected-proposal reason distribution;
- reflection/summary/model call count, tokens, latency, cost, queue age, retries,
  dead letters, and storage growth;
- decision quality/cost ablation for static profile versus evolved state;
- deterministic fake-provider repeatability.

For any stochastic metric, specify trial count, seed handling, confidence interval
or variance, and pass/fail aggregation. A subjective LLM judge may supplement but
cannot override deterministic privacy, provenance, authority, and invariant gates.

## 18. Required Executable Spikes

Before broad implementation, commit tests or scripts proving:

1. a bounded delta cannot alter an immutable baseline or exceed cumulative caps;
2. one event cannot flip a protected value/taboo;
3. relationship updates are asymmetric and owner/time isolated;
4. future, cross-owner, and invisible evidence is rejected before model context;
5. two workers, crash, retry, and stale lease produce one logical commit;
6. a second transaction can acquire the relevant row lock while model inference
   is running;
7. a changed identity/relationship watermark rejects a relevant stale decision;
8. an unrelated relationship edge does not invalidate that decision;
9. historical replay retains old versions after later updates/revert;
10. repeated routine and duplicate memories cause no drift;
11. Oracle success is separated from advice quality and perceived intent;
12. silence does not mechanically lower trust;
13. model outage causes no speculative mutation and does not block world progress;
14. prompt-injection text cannot change policy, owner, caps, or output exposure;
15. reset/reseed removes or generations every new derived row safely;
16. the fixed corpus runs locally with deterministic fake providers.

Failed spikes must be documented before library/schema selection. Do not bury the
failure by excluding the case from the final suite.

## 19. Concurrency, Recovery, and Exact-Once Semantics

Use logical idempotency keys derived from owner/world/generation/Agent/trigger/
evidence watermark/policy version. Document:

- claim, lease renewal, fencing token, timeout, retry, backoff, and dead-letter;
- model succeeded then process crashed before persistence;
- proposal persisted then validation worker crashed;
- commit succeeded then outbox publication crashed;
- two triggers cover overlapping evidence;
- two relationship updates target the same edge;
- a reset occurs while a stale worker is still running;
- evidence is superseded or corrected before commit;
- policy version changes while a job is queued.

Every path must converge to a single valid current snapshot and retain auditable
attempt history. Do not hold locks across network/model work and do not solve races
with process-local mutexes.

## 20. Security and Safety

Required controls:

- treat memory, Observation, relationship summaries, and model output as untrusted;
- block instruction injection from evidence and narrative fields;
- never expose raw prompts, hidden reasoning, credentials, vectors, provider
  payloads, or another owner's state;
- cap input/output size and numeric precision;
- avoid clinical diagnoses, claims of consciousness, or real-person personality
  assessment;
- do not optimize for attachment, engagement, obedience, intervention frequency,
  or dependence;
- cap dependence and flag unsafe growth for evaluation without guilt-based player
  messaging;
- handle violence, self-harm, sexual content, hate, minors, and real-person
  scenarios through existing/future content-governance boundaries;
- player UI cannot directly set trust, dependence, values, or a current decision;
- admin/debug mutation, if needed for tests, is non-production, authenticated,
  audited, and generation-scoped;
- deletion/reset/owner removal covers all identity, edge, proposal, trace, and
  evaluation records.

## 21. Observability and Operations

Add bounded metrics and structured logs for:

- reflection triggers, claims, attempts, outcomes, retries, stale/rejected/dead
  letters, and queue age;
- proposals/accepted deltas by dimension and rejection reason;
- no-change rate, cap/cooldown hits, and invariant failures;
- identity/relationship version counts and storage growth;
- model calls, tokens, latency, cost, failure class, and fallback;
- Oracle assessment classes and dependence safety alerts;
- stale-decision rejections caused by identity/relationship context;
- privacy/security guard rejections.

Provide operational queries/runbooks for stuck work, dead-letter inspection,
policy rollback, snapshot rebuild, summary regeneration, evidence audit, owner
deletion, and safe disabling of evolution while retaining static decisions.
Metrics must avoid high-cardinality raw text and private character content.

## 22. Performance and Cost Budgets

Declare measured budgets before final tuning for:

- maximum evidence items and characters/tokens per reflection;
- maximum dimensions/proposals per run;
- reflection frequency per Agent/world day;
- read/write latency for current identity and relationship projections;
- p50/p95/p99 job queue and execution latency;
- model call/token/cost ceiling per Agent/world day;
- storage growth over 7 and projected 30 world days;
- current 3 L3-Agent scenario and a modest 50 L3-Agent stress fixture.

World advancement and deterministic plans must remain available during reflection
backlog or provider outage. Reject an architecture that requires model work on the
authoritative tick transaction.

## 23. Implementation Sequence

1. Finish research report, executable spikes, dataset draft, and ADR-014.
2. Freeze terminology, authority, ranges, invariants, metrics, and thresholds.
3. Add domain contracts, schemas, fixtures, and generated frontend types.
4. Add reversible migration, constraints, indexes, repositories, and reset logic.
5. Implement deterministic policy and proposal validation before model prompts.
6. Add fenced reflection jobs and model-free fallback.
7. Add Oracle interaction assessment and directional relationship evolution.
8. Add derived identity snapshots and bounded summary generation.
9. Integrate versioned context and freshness into the decision path.
10. Extend replay, owner APIs, observer-safe projections, and operations.
11. Build the frontend identity/relationship/Oracle timeline slice.
12. Run fixed-corpus, adversarial, race, restart, outage, cost, and ablation tests.
13. Complete migration reversal, full quality gates, docs, and completion report.

Do not build UI meters first and infer storage/authority later.

## 24. Allowed Changes

- new domain/application/infrastructure/API/frontend modules required by this
  task;
- backward-compatible extensions to decision, replay, memory, Oracle, and scenario
  contracts;
- one reversible migration and necessary indexes/constraints;
- model-gateway methods with deterministic fake implementations;
- checked-in research, ADR, corpus, fixtures, scripts, evaluation output, and
  runbooks;
- dependency changes justified by the research matrix and locked to reviewed
  versions.

## 25. Explicitly Out of Scope

- free world/character creator and natural-language world-rule compiler;
- direct player editing of current traits, trust, dependence, or decisions;
- clinical psychology, diagnosis, therapy, or real-person profiling;
- optimizing emotional attachment, daily engagement, or intervention frequency;
- reinforcement learning, online model training, fine-tuning, or reward-based
  obedience;
- unrestricted trait/value rewriting or self-modifying prompts;
- making subjective relationship state an objective world fact;
- full knowledge graph or graph database without measured need;
- organization-level strategy, genetics, reproduction, or civilization-scale
  evolution;
- unbounded 30–50 independent LLM Agents;
- production push notification/PWA delivery;
- broad dialogue redesign unrelated to demonstrating relationship effects;
- exposing chain-of-thought or raw provider data;
- changing World Engine action/result authority.

## 26. Test and Quality Gates

All existing tests remain green. Add:

- domain invariant/property tests;
- schema and generated-TypeScript parity tests;
- repository constraint/index/query-plan tests;
- migration upgrade/downgrade/re-upgrade and drift tests;
- PostgreSQL two-worker, lock, crash, restart, stale lease, and reset tests;
- owner/world/time privacy and enumeration tests;
- prompt-injection and malformed-output tests;
- deterministic/provider-outage/budget fallback tests;
- Oracle semantics and dependence-safety tests;
- decision freshness and historical replay tests;
- API pagination/error/redaction tests;
- frontend loading/error/empty/privacy/accessibility/responsive tests;
- fixed-corpus and static-versus-evolved ablation tests;
- full seven-day integration run twice on a reused PostgreSQL database.

Run and record exact commands/counts for Ruff, Ruff format, mypy, pytest,
infrastructure-enabled PostgreSQL tests, schema export, TypeScript typecheck,
ESLint, Prettier, frontend tests, production build, migration reversal, and
Alembic drift.

## 27. Definition of Done

TASK-021 is done only when:

- research and ADR-014 contain measured selection/rejection/defer decisions;
- baseline identity is immutable and derived evolution is versioned/reversible;
- directional Agent and Oracle relationships are persisted and owner isolated;
- every committed dimension change has authorized, temporally valid evidence;
- all changes pass code-owned caps, cooldowns, invariants, and safety policies;
- model output cannot directly mutate identity, relationships, actions, or world;
- Oracle reply/silence/advice/outcome semantics pass all non-mechanical cases;
- reflection is exactly once across two workers, retry, crash, restart, and reset;
- no model call holds a database/world lock or blocks authoritative world progress;
- decision context records identity/relationship versions and rejects relevant
  stale inference;
- replay connects evidence through change to later decision/outcome without
  exposing hidden reasoning;
- APIs and frontend explain baseline/current/change/history while preserving
  observer and owner boundaries;
- the versioned corpus covers stability, continuity, relationship, Oracle, and
  adversarial cases;
- all predeclared gates pass, including zero unsupported mutation and zero
  forbidden exposure;
- static fallback, disable switch, rollback, deletion, rebuild, and dead-letter
  operations are documented and tested;
- cost/latency/storage budgets and static-versus-evolved ablations are reported;
- all backend/frontend/schema/migration/lint/type/format/build gates pass;
- documentation records residual limitations rather than overstating simulated
  psychology or emotional authenticity.

## 28. Completion Report

Add `docs/task-021-completion.md` containing:

- research matrix, exact versions/licenses, spike measurements, and removal seams;
- ADR-014 summary and final authority/state diagram;
- identity/relationship schemas, ranges, invariants, caps, cooldowns, and policy
  versions;
- migration/rollback/index/query-plan evidence;
- trigger/job/fencing/retry/crash/reset exact-once evidence;
- Oracle assessment examples covering reply, silence, follow, reject, outcome,
  uncertainty, and value conflict;
- before/after Gray Harbor identity and directional relationship examples with
  bounded evidence;
- freshness, replay, privacy, injection, API, and UI proof;
- fixed-corpus formulas, frozen thresholds, per-case results, stochastic variance,
  and static-versus-evolved ablation;
- personality consistency, differentiation, goal/causal/action metrics, Oracle
  calibration, and dependence safety results;
- model/token/latency/cost/storage/queue measurements;
- exact quality-gate commands and counts;
- falsified hypotheses, remaining limitations, and evidence-based TASK-022
  recommendation.

TASK-021 completed on 2026-07-28. The detailed evidence, exact commands, policy
ranges, migration proof, evaluation results, limitations, and follow-on
recommendation are recorded in `docs/task-021-completion.md`.

## 29. Follow-On Decision

Do not preselect TASK-022. Choose from evidence:

- notification/PWA/offline summaries if evolved characters are engaging and
  understandable but players miss important moments or fail to return;
- world/character creation if the fixed loop is private, safe, explainable,
  personality-consistent, cost-controlled, and testers request a second world;
- more authoritative actions if evolved goals repeatedly select intentions the
  current World Engine cannot execute;
- broader bounded dialogue if relationship changes pass objective gates but are
  not legible through interaction;
- policy/safety refinement if dependence, manipulation risk, unsupported drift, or
  Oracle calibration misses declared gates;
- retain static identity and revisit the hypothesis if evolution does not improve
  continuity/differentiation enough to justify its complexity.
