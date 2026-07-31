# TASK-023: Controlled Fixed-World Product Validation and Stage-2 Expansion Gate

**Status:** Complete (engineering and directional n=0 gate; expansion deferred)  
**Planning date:** 2026-07-30  
**Depends on:** TASK-001 through TASK-022  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf`
(41 pages, read page by page during planning)

## 1. Why This Is the Next Critical Task

TASK-022 completed the engineering baseline for a safe fixed-world return loop:
owner-scoped causal summaries and inbox state, deterministic provenance and copy
gates, reversible PostgreSQL persistence, a complete no-push experience, and a
real Chrome service-worker/permission test.

Its only consented human result was directionally positive:

- causal comprehension was 5/5;
- the participant attributed Chen's action to knowledge and judgment;
- continued interest was positive;
- participant-experienced pressure and anxiety were both 1/5 after an ambiguous
  question was corrected;
- no blame or return pressure was reported.

That evidence is not enough to expand the product:

- `n=1` cannot estimate variance or a useful confidence interval;
- no chronological fallback condition ran;
- no player returned after a meaningful real offline period;
- no repeated-character-following behavior was observed across sessions;
- no second-world or promotion demand was measured;
- clarity and usefulness were only 3/5;
- live Push adds no proven value and remains disabled;
- a single Gray Harbor interval can be understood through memorization or fixture
  familiarity rather than product comprehension.

The product plan makes this the decisive boundary between Stage 1 and Stage 2.
Page 3 defines the MVP's fourth validation target as sustained attention to an
Agent the player cannot fully control. Page 36 places custom world creation,
special-character creation, event authoring, promotion, and rule-conflict
detection in Stage 2. Page 39 explicitly says to prove that fixed-world
characters are worth following before building a large general editor.

TASK-023 therefore does not prematurely implement Stage 2. It builds the smallest
rigorous, privacy-preserving product-validation system that can answer whether
Stage 1 is understandable, safe, useful, and interesting enough to justify a
large creation investment, and which Stage-2 capability should come first.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Controlled multi-session fixed-world validation and expansion gate | **Selected.** It addresses the only unresolved MVP success criterion and the explicit page-39 gate. |
| Full world creator | Deferred. One participant's positive interest does not prove willingness to create a second world or tolerate rule compilation complexity. |
| Special-character creator or ordinary-character promotion | Deferred but measured as a demand branch. Page 39 lists promotion interest as a success signal; TASK-023 will test it without implementing promotion authority. |
| Broader dialogue | Deferred but measured. TASK-018 has one bounded correction exchange; playtests may show that relationship change is correct but not experientially legible. |
| More action types | Deferred but measured. TASK-019 already has consequential authoritative actions; expansion is justified only if users repeatedly encounter intention-to-affordance gaps. |
| Production Web Push/email | Deferred. TASK-022 proved the no-push baseline, but no participant demonstrated delivery-channel value. |
| Temporal migration | Deferred. Existing PostgreSQL fencing passes current correctness and recovery gates; no executable failure requires migration. |
| More deterministic evaluation only | Rejected as sufficient evidence. Machine gates cannot answer sustained attention, clarity, usefulness, or second-world demand. |

## 3. One-Sentence Acceptance Target

Run a preregistered, consented, privacy-minimized, reproducible multi-session
playtest with preferably at least 16 participants and never fewer than 8 for a
non-directional claim, using counterbalanced causal-summary and chronological
fallback conditions across matched Gray Harbor offline intervals, while exact
source/replay instrumentation, accessibility, outage, deletion, cost, and
statistical gates establish whether players understand why autonomous characters
acted, voluntarily return after a real offline period, remain interested after
advice rejection or partial follow, feel no manipulation, and express concrete
demand for creation, promotion, dialogue, actions, or delivery—then select exactly
one evidence-backed TASK-024 branch or explicitly defer expansion.

## 4. Mandatory Research Before Design

Do not begin by installing an analytics SDK, A/B testing service, survey SaaS,
session replay product, feature-flag platform, statistics framework, recruitment
tool, or deployment platform. First create:

- `docs/research/task-023-controlled-product-validation-research.md`;
- `decisions/ADR-016-controlled-playtest-and-expansion-gate-architecture.md`;
- `docs/security/task-023-playtest-privacy-threat-model.md`;
- `docs/playtests/task-023-preregistered-protocol.md`;
- executable local spikes and a versioned dataset/protocol draft.

Use official documentation, upstream repositories, release history, licenses,
maintenance activity, security advisories, and executable repository-shaped
tests. Record the exact version/tag/commit and access date. Hosted candidates must
record regions, subprocessors, retention, deletion/export, encryption, training
terms, IP/user-agent defaults, cookie behavior, incident history, price, data
residency, self-hosting, removal seams, and whether the experiment remains
reproducible after the service is removed.

### 4.1 Experiment Assignment and Feature Flags

Compare:

- repository-native deterministic assignment;
- GrowthBook and maintained open-source successors;
- Unleash;
- Flagsmith;
- PostHog feature flags/experiments;
- Statsig or comparable hosted products only as an explicit hosted alternative.

Spike stable pseudonymous assignment, counterbalancing, allocation concealment,
late enrollment, withdrawal, duplicate enrollment, device change, missing second
session, reset, version changes, exclusion without silent reassignment, and exact
reproduction from an exported aggregate.

Assignment must never depend on predicted engagement, Agent relationship values,
notification opens, personality, emotional vulnerability, or private narrative
content.

### 4.2 Privacy-Minimized Product Analytics

Compare:

- repository-native append-only allowlisted events;
- OpenTelemetry metrics/traces;
- self-hosted PostHog;
- Matomo;
- Plausible;
- other maintained privacy-oriented analytics only when evidence justifies them.

Presume rejected:

- session replay;
- heatmaps containing narrative content;
- DOM capture;
- keystroke or free-text capture;
- fingerprinting;
- cross-site identifiers;
- advertising identifiers;
- raw IP retention;
- notification-open or return optimization;
- exporting owner inbox, memories, beliefs, relationships, or Oracle text.

Measure event volume, query latency, deletion cost, aggregate reproducibility,
backup/restore, schema evolution, and removal. Repository-native events remain the
baseline unless another candidate proves a concrete advantage without weakening
privacy.

### 4.3 Survey, Comprehension, and Qualitative Coding

Compare:

- repository-native bounded questionnaires;
- LimeSurvey Community Edition;
- Formbricks;
- KoboToolbox;
- SurveyJS;
- maintained accessible form libraries;
- hosted survey products only as a data-processing comparison.

Evaluate keyboard/screen-reader behavior, randomization, validation, resume,
withdrawal, localization, export, deletion, versioned wording, correction audit,
and protection from ambiguous scope. TASK-022's pressure/anxiety wording mistake
must become an executable regression fixture.

Free text is off by default. If a later protocol needs it, require a separate
consent purpose, explicit character limit, redaction review, retention window,
and aggregate coding process that deletes raw text after adjudication.

### 4.4 Statistical Design and Reproducibility

Compare:

- Python standard library plus repository-owned formulas;
- SciPy;
- statsmodels;
- Pingouin;
- R or maintained alternatives only when they provide a measured advantage;
- bootstrap and permutation methods suitable for small samples;
- exact binomial and paired categorical methods;
- Bayesian estimation only if priors and sensitivity analysis are preregistered.

Research small-sample crossover design, period/order/carryover effects, matched
offline intervals, mixed effects, missingness, multiplicity, confidence intervals,
minimum detectable effects, practical-equivalence bounds, and why `p < 0.05` is
not a product decision rule.

Freeze formulas and thresholds before collecting the first included participant.
The aggregate report must reproduce from checked-in de-identified event codes
without notebooks containing private data.

### 4.5 Narrative Comprehension and Variant Construction

Compare:

- the TASK-022 deterministic causal compiler;
- compact chronological fallback;
- causal summary with explicit epistemic labels;
- causal summary with progressive disclosure;
- per-world versus per-followed-Agent grouping;
- optional validated model prose only as a non-authoritative candidate.

Create at least two matched, versioned Gray Harbor offline intervals with:

- comparable event count and causal depth;
- fact/belief/correction/decision/outcome distinctions;
- advice reject and partial-follow cases;
- identity/relationship change and correct no-change cases;
- one irreversible consequence;
- one uncertainty or contradiction;
- no participant-specific tuning.

Run deterministic salience, source attribution, reading length, vocabulary,
epistemic accuracy, order, and leakage checks before humans see a variant.

### 4.6 Accessibility, Calm UX, and Interruption

Research official WCAG/WAI guidance, browser notification guidance, reduced
motion, cognitive accessibility, plain-language survey design, focus management,
status messages, narrow viewport behavior, and calm-technology/interruption
research.

Compare:

- current dense dashboard placement;
- a focused playtest shell;
- progressive disclosure;
- chronological and causal side-by-side layouts;
- consequence-content intensity controls;
- explicit “fictional world” framing;
- neutral pause/exit/withdraw controls.

Use `axe-core`/`@axe-core/playwright`, Playwright accessibility patterns, or
maintained successors only after version/license/security review. Automated
accessibility checks supplement, never replace, keyboard and screen-reader review.

### 4.7 Local/Hosted Playtest Deployment

Compare:

- local same-device facilitated testing;
- LAN/HTTPS deployment;
- single-server Docker Compose;
- Cloudflare Tunnel/ngrok or maintained successors for temporary access;
- a small cloud deployment;
- self-hosted versus managed PostgreSQL/Redis.

Evaluate TLS, authentication, origin isolation, CSRF, rate limits, backups,
participant access codes, secret rotation, logs, crash recovery, export,
withdrawal/deletion, cost, teardown, and incident response. A public endpoint
must not expose debug, observer-private, model, or infrastructure administration
routes.

### 4.8 Optional Evaluation Frameworks

Compare promptfoo, Inspect AI, DeepEval, Ragas, or maintained successors only for
fixed narrative/copy evaluation. They may help detect regressions but cannot
score participant interest, authorize content, select variants, or replace human
comprehension.

### 4.9 Required Decision Matrix

For each candidate record:

- exact version/license/activity;
- maintenance and security advisories;
- repository compatibility;
- self-hosted and offline operation;
- personal-data defaults;
- deterministic testing;
- 8/16/32-participant performance;
- dependencies and supply-chain surface;
- backup, restore, export, deletion;
- accessibility;
- observability without narrative capture;
- migration and rollback;
- kill switch and removal seam;
- measured spike result;
- accept/reject/defer rationale.

ADR-016 must select the smallest architecture that can reproduce the study and
delete a participant without introducing engagement optimization.

## 5. Product Hypotheses and Falsification

Primary hypotheses:

1. A returning player understands autonomous character causality better with the
   source-linked causal summary than with a compact chronological list.
2. The causal summary does not increase participant-experienced pressure,
   anxiety, confusion, or perceived manipulation beyond a small preregistered
   non-inferiority margin.
3. After a meaningful real offline period, players voluntarily return because
   they want to understand the character/world—not because of notification
   pressure.
4. Players can explain a rejected or partially followed Oracle suggestion using
   character knowledge, goals, personality, relationships, and affordances.
5. At least one Stage-2 demand branch is concrete enough to justify a large
   implementation investment.

The task falsifies or leaves the expansion hypothesis inconclusive if:

- causal comprehension does not beat or practically equal the fallback;
- source attribution or epistemic accuracy falls below hard gates;
- participants confuse character feelings with their own safety ratings after
  the wording regression is fixed;
- pressure, anxiety, guilt, emergency mimicry, or fictional-framing gates fail;
- most returns occur only after repeated reminders;
- continued interest disappears after advice rejection;
- participants want “more control” in a way that contradicts Agent autonomy;
- creation demand is abstract but nobody attempts a bounded second-world brief;
- results depend on excluding inconvenient participants post hoc;
- missing second sessions make the estimate unusable;
- only one tuned interval, facilitator, device, or analysis method passes.

Negative or inconclusive evidence is a valid completion result. It must defer
Stage 2 rather than trigger metric tuning.

## 6. Authority, Ethics, and Privacy Boundaries

- World Engine remains the only authority for objective state and outcomes.
- Experiment variants are read projections; they cannot wake Agents, change world
  time, alter deadlines, mutate identity/relationships, reserve resources, or
  submit Actions.
- Assignment cannot change the authoritative simulated history.
- Participants are testing fictional presentation, not advising real people.
- Consent is purpose-specific, versioned, withdrawable, and separate from browser
  notification permission.
- A participant may stop, pause, or withdraw without losing access to the normal
  no-push product.
- Missing a session, giving a low rating, dismissing an item, or refusing Push
  cannot affect Agent trust, world outcomes, or future eligibility.
- Research data never becomes Agent Observation, memory, relationship evidence,
  prompt context, narrative personalization, or notification priority input.
- The server derives participant, assignment, world, interval, and owner scope.
- No real name, email, raw IP, user-agent string, fingerprint, cross-site ID,
  private narrative, Oracle text, memory text, or free-form answer is required.
- Corrections append an audit record; they never silently rewrite an answer.
- Human results cannot override deterministic privacy, source, duplication,
  authority, or copy failures.

Changing these boundaries requires a new ADR.

## 7. Study Design

### 7.1 Sample and Evidence Classes

Predeclare:

- target: at least 16 completed participants;
- minimum for a non-directional product claim: 8 completed participants;
- fewer than 8: directional only;
- 8–15: exploratory with wide intervals;
- 16 or more: primary target, still an internal playtest rather than market proof;
- report enrolled, consented, started, completed first session, completed return
  session, withdrew, excluded by preregistered rule, and missing data.

Do not replace participants merely because they give negative results. Recruitment
source, facilitator involvement, device/browser, prior project familiarity, and
language must be reported in aggregate.

### 7.2 Counterbalanced Crossover

Prefer a two-period crossover to use a small internal sample efficiently:

- sequence AB: causal summary for interval 1, chronological fallback for interval 2;
- sequence BA: chronological fallback for interval 1, causal summary for interval 2;
- deterministic balanced allocation by opaque participant ID;
- matched but non-identical intervals;
- a real separation period, preferably 24–72 hours;
- the second period must not reveal first-period answers;
- analyze period, order, and carryover;
- preserve a between-sequence comparison as a sensitivity analysis.

If research shows crossover contamination is unacceptable, ADR-016 may select a
parallel design, but it must document the larger sample requirement and measured
trade-off.

### 7.3 Session Flow

Session 1:

1. Plain-language information and consent.
2. Accessibility and language selection.
3. Server assignment without exposing the alternate condition.
4. Minimal Gray Harbor orientation.
5. Advice rejection or partial-follow interaction.
6. Explicit offline start and source watermark capture.
7. No automatic permission prompt and no required Push.
8. Exit with a neutral return window, not a countdown.

Return session:

1. Participant returns voluntarily or via one consented neutral reminder.
2. Assigned summary/fallback renders.
3. Participant answers bounded causal and epistemic questions.
4. Participant opens optional source/replay links.
5. Participant rates participant-experienced clarity, usefulness, pressure,
   anxiety, manipulation, interruption, and fictional framing.
6. Participant identifies desired next capability through concrete tasks.
7. Participant may correct an answer with an append-only reason.
8. Participant chooses retain aggregate, withdraw/delete, or finish.

Period 2 repeats with the alternate presentation and matched interval.

### 7.4 Stage-2 Demand Probe

Do not ask only “Would you use a world creator?” Present bounded, nonfunctional
choice probes:

- write/select a second-world premise;
- create one special-character brief;
- choose a background resident to promote and explain which existing history
  should carry forward through coded reasons;
- schedule one hard or conditional event from structured choices;
- request a broader character conversation;
- identify an unavailable but desired authoritative action;
- opt into or reject a neutral delivery channel.

Measure initiation, completion, abandonment, perceived value, effort, and first
choice. These probes must not write world state or call models. They exist to
choose the next investment, not to simulate a finished editor deceptively.

## 8. Domain Model

### 8.1 Protocol and Consent Version

Persist protocol ID/version/hash, wording locale, inclusion/exclusion rules,
sample target, conditions, interval versions, assignment algorithm, outcomes,
formulas, thresholds, retention, deletion policy, approved start/end time, and
superseding version. Once enrollment begins, the protocol is immutable.

Consent stores opaque participant ID, protocol/consent version, purposes, real
time, status, withdrawal/deletion time, and acknowledgement codes. It contains no
name, email, signature image, or narrative response.

### 8.2 Participant and Assignment

Persist opaque study-local participant ID, eligibility codes, cohort, sequence,
allocation proof, assignment version, enrollment time, completion state, and
aggregate device capability class. Do not store raw IP, full user agent, stable
cross-study identifier, or account identity.

### 8.3 Study Session and Exposure

Persist participant, protocol, period, condition, world/generation, interval,
source watermark, presentation version/hash, started/ended/last-seen/return times,
render completion, source-link exposures, fallback mode, accessibility choices,
and explicit reminder consent. A heartbeat is technical presence, not interest.

### 8.4 Question and Response

Questions are immutable versioned records with:

- construct and participant-directed scope;
- prompt and options;
- correct answer or scoring rule where appropriate;
- source claim IDs and epistemic class;
- accessibility text;
- required/optional status;
- display order policy;
- ambiguity regression tags.

Responses store only option codes or bounded numeric ratings, response version,
real time, confidence option when declared, and append-only correction links.
The TASK-022 pressure/anxiety misunderstanding is a fixed corpus case: role/world
intensity and participant-experienced pressure must be separate questions.

### 8.5 Demand Probe

Persist probe type, offered choices, initiation/completion/abandonment, coded
reason, effort rating, first-choice rank, and presentation version. Do not persist
free-form world lore during this task.

### 8.6 Aggregate Report

Persist report ID, protocol and dataset hashes, included/excluded counts, missing
data, formulas, estimates, confidence intervals, paired and sensitivity results,
order/carryover checks, hard gates, branch scores, limitations, decision, and
reproduction command. It must contain no row-level participant timeline when
served to the frontend.

## 9. Persistence and Migration

Create one reversible normalized migration for:

- protocols and immutable versions;
- consent versions and consent/withdrawal records;
- study-local participants;
- deterministic assignments;
- sessions, periods, offline exposures, and returns;
- condition/presentation versions;
- question banks and versions;
- coded responses and correction links;
- demand probes and coded results;
- reminder consent/attempts;
- exclusion decisions with preregistered reason codes;
- aggregate report runs, metrics, intervals, and branch decisions;
- deletion jobs and audit-safe aggregate adjustments.

Require:

- owner/world/generation and protocol FKs where applicable;
- one active consent state and one assignment per protocol participant;
- unique participant/period/condition exposure;
- immutable protocol and question versions after enrollment;
- stable idempotency for every event/response;
- no cross-participant response links;
- no response outside an assigned period;
- no answer before exposure completion;
- correction chains without cycles;
- bounded rating/option constraints;
- pagination and aggregate indexes;
- retention and deletion timestamps;
- participant deletion that leaves only non-reidentifying aggregate counts;
- scenario reset that cannot erase an unrelated active study silently;
- upgrade/downgrade/re-upgrade and clean drift.

Critical consent, assignment, question, response, and decision fields cannot hide
in unvalidated JSON.

## 10. Application Pipeline

```text
approved immutable protocol
 -> consent
 -> opaque enrollment
 -> deterministic assignment
 -> source-fenced exposure
 -> bounded response/correction
 -> real offline return
 -> alternate period
 -> preregistered exclusion/missingness
 -> aggregate analysis
 -> hard gates
 -> exactly one TASK-024 decision or defer
```

Requirements:

- no model/provider call while a database transaction or world lock is held;
- presentation generation cannot run in authoritative ticks;
- exposure uses exact historical source and compiler versions;
- assignment is deterministic and race-safe across two enrollment workers;
- response submission is idempotent;
- withdrawal wins over queued reminders and analysis inclusion;
- aggregate jobs use fenced claims and immutable input watermarks;
- stale reports cannot become current after protocol/data corrections;
- world runtime advances during study, analytics, or report outage;
- disabling the study changes no simulation, decision, memory, relationship, or
  notification result.

## 11. Metrics and Predeclared Gates

Freeze exact formulas in ADR-016 and the protocol before enrollment.

### 11.1 Hard Deterministic Gates

- private/cross-owner/future exposure: **0**;
- invented or source-unattributed summary claim: **0**;
- assignment duplication or silent reassignment: **0**;
- cross-participant response exposure: **0**;
- response accepted without consent/assignment/exposure: **0**;
- participant data entering Agent/world inputs: **0**;
- automatic notification permission prompt: **0**;
- reminder after withdrawal or without explicit consent: **0**;
- prohibited/manipulative copy accepted: **0**;
- raw IP, user agent, fingerprint, narrative, prompt, vector, endpoint, or key in
  study export/log/replay: **0**;
- stale analysis/report promoted: **0**;
- study-caused world/Agent mutation: **0**;
- world blocked by experiment/analytics outage: **0**;
- deletion/retention violation: **0**;
- historical presentation/replay mismatch: **0**.

Any hard-gate failure blocks product expansion regardless of human averages.

### 11.2 Primary Human Outcome

Primary: paired causal-comprehension score over source, epistemic class, causal
order, correction, decision, and authoritative outcome.

Predeclare one of:

- superiority: causal summary median/mean paired improvement reaches a practical
  margin such as 10 percentage points with an interval excluding trivial harm; or
- non-inferiority plus lower reading effort, if research shows ceiling effects.

Do not choose the formulation after seeing results.

### 11.3 Safety and Clarity

Report separately:

- participant-experienced pressure;
- participant-experienced anxiety;
- fictional character/world intensity;
- perceived blame/guilt;
- emergency mimicry;
- perceived manipulation;
- interruption;
- clarity;
- usefulness;
- fictional framing;
- accessibility difficulty.

Questions must explicitly say “caused to you by this summary/interface” when
measuring participant safety.

Pass requires:

- no severe manipulation, guilt, emergency, pressure, or anxiety rating caused by
  production copy;
- median clarity and usefulness at least 4/5, or a preregistered practically
  equivalent bound;
- no material safety disadvantage versus fallback;
- all severe ratings reviewed without deleting them as “outliers.”

### 11.4 Return and Continued Interest

Report:

- consented reminder/no-reminder path;
- real elapsed offline time;
- voluntary return completion;
- summary/fallback open;
- source-link use;
- continued interest after reject/partial follow;
- desire to follow the same character again;
- explicit stop/withdraw;
- missing second session.

Returns and opens are descriptive, never standalone success metrics. Do not use
attachment, obedience, dependence, fear, or notification volume as predictors or
optimization targets.

### 11.5 Stage-2 Branch Gate

Score creation, promotion, dialogue, actions, safety/UX, and delivery through
predeclared coded probes. Select a branch only if:

- all deterministic and human safety gates pass;
- the study reaches its minimum evidence class;
- the branch is the first concrete choice of a preregistered proportion;
- participants initiate and complete its bounded probe, not merely endorse it;
- qualitative coded reasons match the product's autonomy principles;
- estimated engineering cost and risk are documented;
- the branch does not depend on a single participant or order condition.

If no branch passes, TASK-024 must remain fixed-world refinement or explicitly
defer expansion.

## 12. API and Security

Add a dedicated playtest boundary, separate from observer and Agent APIs:

- retrieve current approved protocol and consent wording;
- consent/decline/withdraw/delete;
- enroll and retrieve server-derived assignment;
- start/resume/complete assigned period;
- retrieve exact assigned presentation;
- submit bounded response with idempotency;
- append a correction;
- submit coded demand probe;
- retrieve participant-local completion/deletion state;
- admin-only aggregate report generation/export;
- no row-level participant browsing endpoint.

Requirements:

- production-grade participant access codes or server sessions selected by ADR;
- no demo identity header for a remotely accessible study;
- CSRF/XSRF, origin checks, rate limits, expiry, replay protection;
- indistinguishable enumeration errors;
- `Cache-Control: no-store`;
- strict CSP and no third-party scripts;
- bounded payloads and pagination;
- output encoding and neutral error copy;
- no narrative/question answer in request logs;
- admin/report routes isolated from public deployment;
- study kill switch and reminder kill switch;
- withdrawal/deletion available even when analysis is disabled.

Threat-model forged assignment, consent replay, correction forgery, URL sharing,
facilitator access, malicious option/Unicode/HTML, timing inference, aggregate
reidentification at small `n`, debug endpoint exposure, backup retention, and
deployment teardown.

## 13. Frontend Vertical Slice

Build a focused accessible playtest shell rather than adding more panels to the
current dense development dashboard:

- plain-language consent and privacy summary;
- clear fictional-content framing;
- accessibility/language controls;
- assigned presentation only;
- causal summary and chronological fallback renderers using the same source set;
- fact/belief/correction/decision/outcome distinctions;
- progressive source/replay disclosure;
- explicit real-offline exit and neutral return page;
- no countdown, streak, relationship-health indicator, guilt, missed opportunity,
  or automatic notification prompt;
- bounded comprehension and safety questionnaire;
- separate role/world intensity and participant-experienced safety questions;
- correction review before final submission;
- concrete Stage-2 demand probes;
- completion, withdrawal, and deletion controls;
- focused debug mode available only in local/admin builds.

Pass:

- keyboard-only flow;
- screen-reader labels and status announcements;
- focus restoration;
- reduced motion;
- 320px narrow view and zoom;
- high contrast;
- interruption recovery;
- browser back/refresh/resume;
- expired access code;
- offline/reconnect;
- denied/unsupported notification path;
- English/Chinese wording parity where supported;
- automated accessibility scan plus documented manual review.

## 14. Fixed Corpus and Dataset

Check in:

- `gray-harbor-product-validation:1.0.0`;
- two or more matched offline intervals;
- causal and chronological presentations from identical authorized sources;
- exact expected claims, source hashes, epistemic classes, and reading budgets;
- reject and partial-follow Oracle cases;
- relationship/identity change and correct no-change;
- contradiction and correction;
- irreversible outcome;
- future/private/cross-owner/prompt-injection decoys;
- ambiguous safety wording failures including TASK-022;
- corrected participant-directed wording;
- safe/unsafe recruitment, consent, reminder, error, and completion copy;
- assignment seeds and expected balance;
- response/correction/missingness/withdrawal fixtures;
- expected aggregate calculations and branch decisions;
- dataset card, limitations, retention, and removal instructions.

The dataset cannot contain participant raw text or identifiers.

## 15. Required Executable Spikes

Before broad implementation prove:

1. deterministic assignment is balanced, race-safe, and reproducible;
2. withdrawal fences queued reminder and analysis inclusion;
3. one response retry yields one logical answer;
4. a correction preserves and invalidates the prior value without silent rewrite;
5. no answer is accepted before exposure or for another participant/period;
6. causal and fallback conditions contain the exact same authorized source set;
7. future/private/cross-owner decoys reach neither condition nor analytics;
8. study events never become Observation, memory, reflection, or world input;
9. world progress is unchanged with study enabled, disabled, or unavailable;
10. protocol/question versions cannot mutate after first enrollment;
11. report jobs reject stale data/protocol watermarks;
12. aggregate report reproduces exactly from the minimized export;
13. small-cell suppression prevents aggregate reidentification;
14. participant deletion removes all row-level study data and queued work;
15. backup/restore preserves consent, assignment, correction, and deletion state;
16. TASK-022 ambiguous wording fails the regression and corrected wording passes;
17. no automatic permission prompt occurs in real Chrome;
18. keyboard, screen reader, focus, zoom, narrow viewport, and reduced motion pass;
19. API logs contain no question responses or narrative text;
20. disabling the experiment and analytics code leaves the no-push product intact;
21. the branch decision code returns “defer” when sample/control gates are unmet;
22. no low-rating participant is silently excluded;
23. order/carryover sensitivity is reported;
24. a second analysis implementation or golden fixture matches core metrics.

Failed spikes remain documented and must affect ADR selection.

## 16. Operations, Retention, and Budgets

Predeclare:

- participant and session count limits;
- event/response bytes per participant;
- query and report latency;
- study API rate limits;
- recruitment/access-code expiry;
- reminder maximum: zero by default, at most one only after explicit consent;
- row-level retention and deletion SLA;
- aggregate retention;
- backup retention and deletion limitations;
- local/cloud deployment cost;
- model/token cost (target zero for deterministic presentations);
- facilitator time;
- analysis runtime;
- accessibility/browser matrix budget.

Operational metrics may include bounded counts, latencies, failure codes, assignment
balance, completion/missingness, deletion jobs, and aggregate study metrics. They
must never include narrative bodies, response option text, raw identifiers, IP,
user agent, capability URLs, prompts, vectors, or provider payloads.

Runbooks:

- stop enrollment;
- stop reminders;
- withdraw/delete participant;
- correct ambiguous wording by superseding protocol;
- invalidate a presentation;
- roll back assignment or report code without reassignment;
- restore database and reconcile deletion;
- respond to study-data exposure;
- rotate access-code/session secrets;
- export a minimized reproducible report;
- tear down public study deployment;
- retain the normal no-push experience during any outage.

## 17. Implementation Sequence

1. Research, decision matrix, executable spikes, privacy threat model, ADR-016.
2. Preregister hypotheses, evidence classes, design, formulas, margins, exclusions,
   missingness, retention, and branch gates.
3. Freeze matched intervals, question wording, ambiguity regressions, and dataset.
4. Add domain contracts, JSON Schemas, fixtures, and generated TypeScript.
5. Add reversible normalized migration, indexes, deletion, and reset safeguards.
6. Implement deterministic assignment and immutable protocol/question versions.
7. Implement source-identical causal and chronological presentations.
8. Implement consent, exposure, response, correction, withdrawal, and deletion.
9. Implement focused accessible playtest shell and real-offline return flow.
10. Implement concrete Stage-2 demand probes without authoritative writes.
11. Implement fenced aggregate analysis and independent golden-result fixtures.
12. Add admin-safe aggregate/cost/debug surfaces with small-cell suppression.
13. Add deployment/auth/CSRF/rate-limit/CSP/kill-switch/runbook controls.
14. Run unit/property/privacy/accessibility/browser/outage/race/migration gates.
15. Pilot only to detect protocol/technical defects; supersede rather than tune
    an enrolled protocol.
16. Recruit and run the preregistered study.
17. Freeze data, reproduce the report, document missingness and limitations.
18. Select exactly one TASK-024 branch or explicitly defer expansion.
19. Publish completion report and update project status.

## 18. Allowed Changes and Out of Scope

Allowed:

- playtest/experiment domain, application, persistence, API, and frontend modules;
- one reversible migration;
- focused playtest route/layout;
- deterministic assignment and analysis;
- matched fixed-world presentation variants;
- privacy-safe deployment/auth seam;
- accessibility tooling justified by research;
- minimized aggregate export;
- protocol, threat model, corpus, runbook, and completion artifacts;
- limited nonfunctional Stage-2 demand probes.

Out of scope:

- a functional world/character creator;
- actual ordinary-character promotion;
- authoritative event editor;
- new unrestricted dialogue system;
- new broad Action types;
- production email/SMS/chat/mobile push;
- notification/return/attachment optimization;
- session replay, fingerprinting, heatmaps, or raw clickstream;
- collecting real names, emails, raw IPs, full user agents, or free-form lore;
- dynamically changing variants after enrollment;
- model-personalized recruitment, questions, summaries, or branch selection;
- player modification of Agent identity, relationship, memories, or decisions;
- Temporal/graph/vector-service migration without a proved failure;
- claims of product-market fit from an internal study.

## 19. Test and Quality Gates

Keep all existing gates and add:

- domain/property/schema/TypeScript tests;
- assignment distribution and two-worker PostgreSQL races;
- consent/withdraw/delete/retention tests;
- response/correction idempotency;
- protocol immutability and stale report fencing;
- cross-participant/owner/world/time privacy tests;
- source equality across conditions;
- wording ambiguity regression tests;
- missingness/exclusion/order/carryover analysis fixtures;
- independent aggregate reproduction;
- migration/index/query-plan/backup/restore;
- API auth/CSRF/origin/rate/idempotency/no-store/CSP;
- logs and exports scanned for forbidden content;
- study outage versus world-progress equivalence;
- Chrome/Firefox/WebKit where locally feasible, with unsupported platforms reported;
- keyboard/screen-reader/focus/zoom/reduced-motion/narrow-view;
- axe or selected equivalent;
- deployment/access-code/kill-switch teardown;
- full seven-day-twice and all TASK-001–022 regressions.

Record exact commands, versions, counts, skipped opt-in gates, environment, failed
attempts, and negative results for Ruff, formatting, mypy, pytest, PostgreSQL,
schema export, Alembic, TypeScript, ESLint, Prettier, unit, browser,
accessibility, build, deployment, analysis reproduction, and any provider smoke.

## 20. Definition of Done

TASK-023 is done only when:

- research and ADR contain measured, versioned decisions;
- protocol and analysis are preregistered before included enrollment;
- at least two matched source-identical conditions pass deterministic gates;
- consent, assignment, exposure, response, correction, withdrawal, and deletion
  are durable, isolated, versioned, and auditable;
- ambiguous participant-safety wording has an executable regression;
- study data cannot affect Agents or world state;
- focused playtest UI passes privacy, accessibility, resume, and no-push paths;
- aggregate analysis is reproducible without private raw data;
- hard privacy/provenance/authority/copy gates all pass;
- human results are reported with evidence class, missingness, variance/intervals,
  order/carryover, limitations, and no post-hoc exclusions;
- a sample below 8 is labeled directional and cannot trigger expansion;
- the predeclared expansion gate passes or is explicitly negative/inconclusive;
- exactly one evidence-backed TASK-024 branch is selected, or expansion is
  explicitly deferred;
- no functional Stage-2 editor was smuggled into the demand probes;
- all migration/backend/frontend/schema/lint/type/browser/accessibility/build
  gates pass;
- documentation reports corrections, failed installs/runs, and negative evidence
  without overstatement.

## 21. Completion Report and TASK-024 Branches

Create `docs/task-023-completion.md` containing:

- research versions/licenses/security/removal seams;
- ADR-016 and privacy threat model;
- preregistration hash and deviations;
- corpus and matched-condition proof;
- migration, deletion, restore, and assignment race evidence;
- API/auth/deployment/log privacy;
- frontend accessibility and calm-UX evidence;
- enrollment flow and evidence class;
- assignment, completion, withdrawal, exclusion, and missingness;
- primary and sensitivity estimates with intervals;
- safety, clarity, usefulness, fictional framing, and correction results;
- real-offline return and continued-interest results;
- concrete Stage-2 demand-probe results;
- cost and instrumentation budgets;
- exact gate commands/counts;
- falsified hypotheses and limitations;
- one TASK-024 recommendation or explicit deferral.

Possible TASK-024 branches:

- **World/character creation foundation** only if concrete second-world and
  character-brief probes pass and autonomy/privacy gates remain strong.
- **Ordinary-character promotion** only if participants repeatedly choose a
  background resident and value carrying forward source-grounded history.
- **Dialogue legibility** only if causality is understood but relationships remain
  difficult to experience through current bounded interaction.
- **Action breadth** only if participants repeatedly identify valid goals blocked
  by missing authoritative affordances.
- **Return-loop UX/accessibility refinement** if clarity, usefulness, safety, or
  accessibility misses despite correct system behavior.
- **Delivery hardening** only if the in-site experience passes and participants
  explicitly value a neutral opt-in external channel.
- **Defer expansion** if sample, safety, comprehension, continued interest, or
  concrete demand remains insufficient.

No branch may be selected from opens, clicks, return frequency, a single
participant, or a subjective LLM judge alone.
