# TASK-024: Production-Safe Pilot Operations, Real Multi-Session Evidence, and Expansion Decision

**Status:** In progress (staging implemented; real participant gate open)  
**Planning date:** 2026-07-31  
**Depends on:** TASK-001 through TASK-023  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf`
(41 pages, read page by page during planning)

## 1. Why This Is the Next Critical Task

TASK-023 completed the machinery for a privacy-minimized controlled study:
frozen protocol and question wording, deterministic AB/BA allocation, two
source-fenced Gray Harbor conditions, bounded responses and corrections,
withdrawal/deletion, small-cell suppression, PostgreSQL persistence, a focused
playtest route, a real Chrome calm/no-push gate, and reproducible analysis rules.

It did **not** produce product evidence. Its included human sample is `n=0`.
Accordingly:

- causal-summary benefit has not been estimated;
- no participant completed both periods after a real offline interval;
- no order or carryover effect can be estimated;
- safety, clarity, usefulness, and fictional framing have no TASK-023 human data;
- continued interest after reject/partial-follow has not been demonstrated;
- no concrete creation, promotion, dialogue, action, return-loop, or delivery
  demand branch passed;
- Stage 2 remains correctly deferred.

The product plan makes this the decisive product risk. Page 3 names sustained
attention to an Agent the player cannot fully control as one of four MVP
validation targets. Page 36 places world creation, character creation, event
authoring, promotion, and conflict detection in Stage 2. Page 39 explicitly says
to prove fixed-world characters are worth following before building a large
general editor.

The next task must therefore turn the already-built study into a safe, observable,
recoverable pilot operation and collect the missing real multi-session evidence.
It must not disguise more engineering fixtures as human validation, lower the
sample gate, or choose a Stage-2 feature from `n=0`.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Operate the frozen controlled study with production-safe pilot infrastructure and real participants | **Selected.** It closes the explicit page-39 product gate and the only missing MVP validation target. |
| World/character creator | Rejected now. Page 39 forbids building the large editor before fixed-world following is proved. |
| Ordinary-character promotion | Deferred. TASK-023 has no completed promotion probe. |
| Broader dialogue | Deferred. No human evidence shows causality is understood but relationship experience is insufficient. |
| More authoritative actions | Deferred. No participant has identified a repeated, valid affordance gap. |
| External Push/email | Deferred. In-site/no-push works, and no TASK-023 participant valued an external channel. |
| Temporal migration | Deferred. PostgreSQL fencing passes current correctness gates; no production failure justifies migration. |
| More deterministic evaluation | Rejected as the main task. Machine tests cannot establish voluntary return or sustained attention. |

## 3. One-Sentence Acceptance Target

Deploy and operate the frozen `gray-harbor-product-validation:1.0.0` crossover
study through a production-safe, privacy-minimized pilot; enroll only consented
participants; obtain preferably at least 16 and never fewer than 8 completed
two-period participants for any non-directional product conclusion; reproduce the
preregistered report with safety, missingness, order/carryover, deletion, outage,
cost, accessibility, and incident evidence; then select exactly one justified
TASK-025 branch or explicitly defer expansion again.

## 4. Non-Negotiable Evidence Rule

TASK-024 cannot be marked complete merely because deployment and test automation
work. Completion requires one of:

1. at least 8 real completed participants and a frozen reproducible report; or
2. a documented, externally caused inability to recruit/operate after the
   preregistered recruitment window, with no product conclusion and an explicit
   blocked/defer decision approved by the product owner.

Synthetic participants, team-written answer fixtures, browser automation,
facilitator guesses, LLM judges, and copied TASK-022 results are not human
evidence. Pilot defect-detection sessions must be labeled pilot and excluded from
the confirmatory dataset before their answers are inspected.

## 5. Mandatory Research Before Deployment Design

Before opening enrollment, create:

- `docs/research/task-024-pilot-operations-and-study-execution-research.md`;
- `decisions/ADR-017-production-pilot-deployment-and-operations.md`;
- `docs/security/task-024-public-pilot-threat-model.md`;
- `docs/operations/task-024-pilot-runbook.md`;
- `docs/playtests/task-024-recruitment-facilitation-and-analysis-plan.md`;
- executable deployment, restore, deletion, accessibility, and incident spikes.

Research must use official documentation, upstream repositories, release
histories, licenses, maintenance activity, security advisories, and executable
repository-shaped tests. Record exact version/tag/commit and access date. Do not
install a platform before its data and removal behavior is documented.

### 5.1 TLS, Reverse Proxy, and Deployment

Compare at minimum:

- Caddy;
- nginx;
- Traefik;
- Cloudflare Tunnel;
- Tailscale Funnel or Serve;
- ngrok;
- a direct small-cloud HTTPS deployment;
- local/LAN facilitated operation.

Measure:

- automatic certificate issuance and renewal;
- origin isolation and trusted proxy behavior;
- forwarded-IP/header handling without IP retention;
- request/body log defaults and redaction;
- WebSocket/SSE compatibility even though the study does not require them;
- rate limiting and connection limits;
- container health checks and zero/low-downtime restart;
- public debug/admin route isolation;
- reproducible teardown;
- monthly and one-pilot cost;
- vendor regions, subprocessors, retention, training terms, incident history,
  data residency, and removal seam.

### 5.2 Participant Authentication and Access Codes

Compare:

- the repository-native opaque access-code/session boundary;
- signed, expiring, single-study cookies;
- Authentik;
- Keycloak;
- Ory Kratos/Hydra only if its scope is justified;
- Supabase/Auth0/Clerk only as hosted data-processing comparisons.

The selected design must not require real names, email addresses, social login,
phone numbers, cross-study identifiers, fingerprints, or account creation.
Evaluate code issuance, expiry, one-time activation, resume on another device,
sharing/replay, brute force, enumeration, facilitator visibility, secret rotation,
session revocation, deletion, backup residue, and emergency shutdown.

### 5.3 Secrets, Configuration, and Supply Chain

Compare:

- environment files with deployment-level secret injection;
- Docker secrets;
- SOPS plus age;
- Bitwarden Secrets Manager or comparable hosted option;
- Vault only if measured complexity is justified.

Research Dependabot/Renovate, `pip-audit`, OSV-Scanner, npm audit, Trivy/Grype,
Syft/CycloneDX, Sigstore/Cosign, pinned container digests, lockfiles, provenance,
and SBOM generation. Select the smallest set that detects actionable risk without
uploading private source or secrets.

### 5.4 Backup, Restore, and Participant Deletion

Compare:

- `pg_dump`/`pg_restore`;
- pgBackRest;
- WAL-G;
- managed PostgreSQL backups;
- restic/Borg for encrypted deployment artifacts.

Spike:

- point-in-time assumptions;
- encrypted backup creation;
- restore to an isolated database;
- deletion reconciliation after restoring an older backup;
- backup retention expiry;
- key loss/rotation;
- protocol, assignment, correction-chain, withdrawal, and aggregate integrity;
- proof that a deleted participant does not silently reappear in the active
  study after restore.

### 5.5 Monitoring and Incident Response

Compare:

- repository-native bounded health/counter logs;
- OpenTelemetry;
- Prometheus and Grafana;
- Loki;
- self-hosted Sentry/GlitchTip;
- Better Stack, Datadog, or comparable hosted services only as explicit hosted
  alternatives.

No monitoring system may receive:

- access codes or hashes;
- consent acknowledgements tied to row-level identity;
- question prompts or answers;
- narrative bodies or source claims;
- Oracle text, memories, prompts, vectors, Push endpoints, IPs, or full user
  agents.

Evaluate bounded error codes, latency histograms, health, disk/database capacity,
backup age, deletion SLA, enrollment balance, missing sessions, alert routing,
retention, export, deletion, cost, and removal.

### 5.6 Accessibility and Cross-Browser Operation

Research and compare:

- `@axe-core/playwright`;
- Pa11y;
- Lighthouse accessibility checks;
- Accessibility Insights;
- NVDA and Windows Narrator procedures;
- VoiceOver procedures when a macOS device is available;
- Chrome, Firefox, Edge, Safari/WebKit support.

Automated scanning supplements manual keyboard, zoom/reflow, high-contrast,
reduced-motion, cognitive-load, status-message, focus-restoration, and
screen-reader review. Record unsupported hardware rather than claiming coverage.

### 5.7 Recruitment, Scheduling, and Facilitation

Compare privacy and bias implications of:

- direct internal recruitment;
- community recruitment;
- Prolific or comparable participant platforms;
- calendar/survey SaaS;
- repository-issued codes with facilitator scheduling.

Record recruitment source, compensation, language, prior project familiarity,
facilitator contact, device/browser class, no-show handling, reminder policy,
withdrawal path, support boundaries, coercion risk, and data-processing terms.

The study application must not collect scheduling contact data. If contact is
needed, keep it in a separate system and deletion purpose with no join key
exported into the analysis dataset.

### 5.8 Statistical and Independent Review

Recheck the frozen formulas against current official SciPy/statsmodels/R
documentation and small-sample crossover references. Compare the repository
implementation with an independent second implementation or golden R/Python
script.

Do not change primary outcome, practical margin, safety thresholds, exclusions,
missingness rules, branch threshold, or small-cell threshold after seeing included
answers. Any necessary defect correction supersedes the protocol and restarts
confirmatory enrollment.

### 5.9 Required Decision Matrix

For every candidate record:

- exact version/license/activity;
- release and security-advisory history;
- self-host/offline support;
- personal-data defaults;
- cookies, IP/user-agent and request-log behavior;
- encryption and secret handling;
- deterministic local testing;
- accessibility;
- deployment and rollback;
- backup, restore, deletion and teardown;
- 8/16/32-participant performance;
- one-pilot and monthly cost;
- supply-chain surface;
- kill switch and removal seam;
- measured spike result;
- accept/reject/defer rationale.

ADR-017 must select the smallest production pilot architecture, not a premature
general production platform.

## 6. Authority, Ethics, and Product Boundaries

- World Engine remains the only authority for objective state and outcomes.
- Study conditions are read projections; they cannot wake Agents, advance time,
  submit Actions, reserve resources, or change identity/relationships.
- Participant answers never enter Observation, memory, reflection, prompt
  context, notification priority, or model training.
- Recruitment and compensation cannot depend on ratings, completion sentiment,
  Push permission, or choosing an expansion branch.
- One neutral reminder is allowed only after separate explicit consent.
- No guilt, streak, countdown, missed-opportunity, fake urgency, relationship
  health, or emergency mimicry is permitted.
- Participants may pause, stop, withdraw, or delete without explanation.
- No facilitator may edit an included answer. Corrections are participant-owned,
  append-only, and preserve the invalidated value.
- Low ratings, refusal, missed session, device difficulty, or negative feedback
  are not exclusion reasons.
- The study is about fictional presentation, not mental-health evaluation or
  advice to real people.
- External Push, email, or SMS is not enabled merely to improve completion.

Changing these boundaries requires a new ADR and a superseding protocol.

## 7. Study Operations Design

### 7.1 Evidence Classes

- target: at least 16 completed two-period participants;
- minimum for any non-directional product conclusion: 8;
- 0–7 completed: directional only, expansion automatically deferred;
- 8–15: exploratory, wide intervals, branch selection allowed only if every
  preregistered safety and concrete-demand rule passes;
- 16 or more: primary internal target, still not market proof.

Report invited, codes issued, activated, consented, period-1 exposed, period-1
completed, returned, period-2 exposed, completed, withdrew, deleted, excluded by
predeclared code, missing, and unreachable after the single consented reminder.

### 7.2 Recruitment Freeze

Before the first included participant:

- publish recruitment wording and compensation;
- publish inclusion/exclusion codes;
- freeze protocol/dataset/application container hashes;
- freeze study start/end and maximum sample;
- freeze reminder timing;
- freeze facilitator script;
- freeze browser support statement;
- freeze analysis command and expected empty-report result;
- create encrypted backup and prove restore;
- generate an incident contact and stop-enrollment procedure.

Do not continue recruiting after the maximum sample merely to change the result.

### 7.3 Participant Journey

1. Receive a random, expiring access code separately from the study application.
2. Read plain-language information, fictional framing, privacy, compensation,
   support, withdrawal, and deletion terms.
3. Consent to the study; separately opt in or out of one neutral reminder.
4. Receive deterministic concealed AB/BA assignment.
5. Complete period 1 over its assigned matched interval.
6. Leave for the preregistered real 24–72 hour interval.
7. Return voluntarily or after the single consented neutral reminder.
8. Complete period 2 with the alternate presentation.
9. Review bounded answers and append corrections if necessary.
10. Complete one concrete nonfunctional demand probe.
11. Choose retention of minimized row-level data until report freeze, immediate
    withdrawal/deletion, or completion.
12. Receive a neutral completion/debrief screen with support and deletion
    instructions.

### 7.4 Facilitator Boundary

Facilitators may:

- explain navigation and accessibility controls;
- restate the exact frozen question scope;
- record coded technical incident categories;
- stop a session for safety or technical failure.

Facilitators may not:

- explain Gray Harbor causality;
- reveal the alternate condition;
- suggest an answer or branch;
- encourage return or completion;
- reinterpret a rating;
- exclude a negative participant;
- view another participant’s row-level answers;
- edit data directly in PostgreSQL.

Every facilitated intervention uses a preregistered bounded code and is reported
in aggregate.

## 8. Deployment Architecture Requirements

Build a production-pilot deployment, separate from development:

- pinned API, worker, frontend, PostgreSQL and Redis artifacts;
- TLS-only public origin;
- strict trusted-host, origin, CSRF and CSP policies;
- no demo identity headers or debug routes;
- random expiring access codes;
- default-off enrollment and reminder kill switches;
- isolated admin origin or private network path;
- database role separation for API, migration, backup, and read-only reporting;
- encrypted secrets outside images and Git;
- health/readiness without database contents;
- bounded rate limits for code activation, reads, writes, corrections,
  withdrawal, and deletion;
- no-store study responses;
- request/body/header redaction;
- disk, connection, backup-age, and deletion-SLA alerts;
- documented teardown that preserves only approved aggregate artifacts.

The normal fixed-world/no-push product must continue when the study, analytics,
admin report, reminder mechanism, or monitoring is disabled.

## 9. Access-Code and Session Requirements

- at least 128 bits of randomness before encoding;
- store only a versioned keyed hash;
- constant-time comparison where applicable;
- activation and expiry timestamps;
- bounded failed attempts and neutral enumeration errors;
- same code resumes the same assignment without reassignment;
- duplicate concurrent activation creates one participant;
- device change requires the same code and reveals no prior answers until
  authentication succeeds;
- withdrawal revokes normal study access but still permits authenticated deletion;
- secret rotation has an overlap and revocation plan;
- no code in URLs, referrers, logs, analytics, screenshots, exports, or backups
  outside the encrypted database;
- facilitator cannot derive participant answers from code issuance records.

## 10. Data Integrity and Protocol Immutability

Add or prove:

- database-enforced protocol/question immutability after first enrollment;
- condition and presentation hash immutability after exposure;
- one assignment per protocol participant;
- one exposure per participant/period/condition;
- response ownership and period fencing;
- no answer before completed render;
- idempotent retries;
- acyclic append-only correction chains;
- no completion until all required bounded questions exist;
- period 2 cannot begin before the minimum real interval unless recorded as a
  preregistered technical pilot exclusion;
- withdrawal wins over reminders, report claims, and queued work;
- deletion removes every row-level dependent record;
- aggregate report fencing on protocol, dataset, application, and input hashes;
- a stale report cannot become current;
- small-cell suppression applies to every slice and combination, not only branch
  counts.

If TASK-023’s current migration cannot enforce a requirement, add one reversible
normalized migration rather than hiding critical state in JSON.

## 11. Analysis and Expansion Gate

Use the frozen TASK-023 primary analysis:

- paired causal-minus-chronological comprehension difference;
- practical superiority margin;
- exact sign sensitivity;
- confidence interval;
- period, sequence, and carryover checks;
- missingness and between-sequence sensitivity;
- participant-experienced pressure, anxiety, manipulation, guilt and interruption;
- separate fictional-world intensity;
- clarity, usefulness, fictional framing and accessibility difficulty;
- voluntary return and reminder path;
- continued interest after reject/partial-follow;
- first-choice, initiation and completion of each bounded demand probe.

Hard gates remain zero tolerance for:

- private, cross-owner, future, or unattributed exposure;
- assignment duplication or reassignment;
- answer without consent/assignment/exposure;
- participant data entering world or Agent inputs;
- reminder without consent or after withdrawal;
- manipulative copy or automatic permission prompt;
- raw identifier/narrative/prompt/vector/endpoint leakage;
- stale report promotion;
- study-caused world mutation;
- deletion or retention violation.

Branch selection additionally requires:

- at least 8 completed participants;
- every deterministic and human safety gate;
- branch first choice by at least 50% of included participants;
- completed, not merely endorsed, bounded probe;
- support across both AB and BA sequences;
- autonomy-compatible coded reasons;
- no dependence on one participant, facilitator, device, or interval;
- documented engineering cost, privacy, safety, and reversibility.

If no branch passes, TASK-025 must be fixed-world refinement, a new evidence
operation, or explicit continued deferral. It cannot become a general editor by
product-owner preference alone.

## 12. API and Admin Requirements

Harden the existing `/playtest` boundary:

- protocol/consent retrieval;
- code activation and session resume;
- participant-local state only;
- exact assigned presentation;
- render/exposure acknowledgement;
- bounded response and correction;
- demand probe;
- pause, withdrawal, and deletion;
- reminder preference;
- neutral debrief;
- rate-limit and expiry errors;
- outage-safe retries.

Admin capabilities must be isolated and aggregate-first:

- stop/start enrollment;
- stop reminders;
- issue and revoke codes without answer visibility;
- view bounded operational counts;
- run/fence/freeze aggregate analysis;
- export minimized reproducible dataset;
- reconcile withdrawals/deletions after restore;
- record incident and protocol-supersession decisions.

Do not add a general row-level participant browsing endpoint. Exceptional
incident access requires two-person approval, bounded purpose, audit record, and
no narrative/answer export.

## 13. Frontend Requirements

Complete the focused playtest shell for real operation:

- server-provided frozen consent wording and protocol hash;
- access-code expiry/retry without enumeration;
- English and Chinese wording parity;
- explicit fictional framing on every return;
- period/resume state derived from server;
- causal and chronological renderers over identical source sets;
- progressive source disclosure;
- all comprehension, clarity, usefulness, safety, interest, and accessibility
  questions;
- separate participant safety and fictional intensity;
- answer review and append-only correction flow;
- real 24–72 hour neutral return state;
- concrete nonfunctional demand probes;
- reminder consent separated from browser permission;
- pause, withdrawal, deletion, and debrief;
- offline/reconnect and duplicate-submit recovery;
- expired/revoked code path;
- no countdown, streak, guilt, relationship health, attachment language, or
  automatic notification prompt.

Accessibility gates:

- keyboard-only completion;
- visible focus and skip link;
- focus restoration after every step/error;
- semantic headings/fieldset/legend/labels;
- status announcements without repeated interruption;
- 200% zoom and 320px reflow;
- high contrast and forced-colors;
- reduced motion;
- NVDA or Narrator documented completion;
- Chrome and Firefox; Edge/Safari/WebKit reported where available;
- automated axe/selected equivalent with zero serious/critical violations.

## 14. Required Executable Gates

Before enrollment:

1. container/image hashes match the frozen deployment manifest;
2. TLS renewal and HTTP-to-HTTPS behavior pass;
3. debug, observer-private, model, database, and admin routes are unreachable
   publicly;
4. forged/shared/expired/revoked codes fail neutrally;
5. two workers activate one code into one assignment;
6. protocol/question mutation after enrollment fails at database level;
7. causal and chronological views have the exact same source set;
8. future/private/cross-owner decoys reach neither view nor logs;
9. response retry creates one logical answer;
10. correction preserves and invalidates the old answer;
11. period-2 early entry is rejected;
12. withdrawal fences reminder and analysis;
13. deletion removes all row-level data within SLA;
14. restore plus deletion reconciliation does not resurrect active data;
15. stale report cannot be promoted;
16. small-cell suppression survives combined filters;
17. API, proxy, monitoring, backup, and error logs scan clean for forbidden data;
18. world progress is identical with study enabled, disabled, or unavailable;
19. one deployment rollback preserves the normal no-push product;
20. Chrome/Firefox keyboard, narrow, zoom, reduced-motion and accessibility gates
    pass;
21. automatic notification permission prompts remain zero;
22. empty and sub-8 datasets return `directional/defer`;
23. independent analysis matches the repository implementation;
24. backup restore, secret rotation, stop-enrollment, stop-reminder, incident,
    withdrawal, deletion, and teardown runbooks execute successfully;
25. load at 32 concurrent participants stays within preregistered latency,
    connection, storage, and cost budgets.

During operation:

- daily encrypted backup and restore-age check;
- enrollment/assignment balance and missingness counters;
- deletion-SLA check;
- disk/database/latency/error monitoring;
- facilitator deviation log;
- incident and stop-rule review;
- no inspection of outcome differences before the analysis freeze.

## 15. Stop Rules and Incident Handling

Immediately stop enrollment for:

- any private/cross-owner/future source exposure;
- access-code or answer leakage;
- automatic notification permission request;
- reminder after withdrawal;
- participant data reaching Agent/world inputs;
- protocol or question mutation;
- incorrect condition assignment;
- correction loss;
- deletion failure;
- manipulative or emergency-mimicking production copy;
- serious unmitigated accessibility barrier;
- backup or admin exposure;
- evidence that the wrong build/protocol/dataset is running.

Freeze affected data, preserve audit evidence, notify the product owner, execute
the incident runbook, and supersede rather than silently patch an enrolled
protocol. Do not restart confirmatory enrollment until the root cause and affected
cohort decision are documented.

## 16. Operations and Budgets

Predeclare:

- maximum 32 activated participants;
- target 16 completed;
- 24–72 hour interval;
- zero reminders by default, maximum one after consent;
- row-level retention 30 days after report freeze;
- deletion acknowledgement immediately and completion within 72 hours;
- encrypted backup retention and disclosed deletion limitation;
- zero model/provider calls for presentations and analysis;
- per-participant response/event byte cap;
- API p95 and p99 latency targets;
- rate-limit thresholds;
- facilitator time per participant;
- accessibility review time;
- deployment and monitoring monthly cost;
- recruitment and compensation budget;
- incident-response availability;
- public deployment start and mandatory teardown dates.

The report must include actual cost, not only estimates.

## 17. Implementation Sequence

1. Research candidates, security history, data defaults, costs, and removal seams.
2. Execute deployment/auth/backup/monitoring/accessibility spikes.
3. Publish ADR-017 and public-pilot threat model.
4. Freeze recruitment, compensation, facilitation, stop rules, and analysis plan.
5. Add any required normalized migration and database immutability/fencing.
6. Harden access codes, sessions, rate limits, trusted origins, CSP, logs, secrets,
   admin isolation, enrollment/reminder kill switches, and deletion.
7. Complete two-period resume, full questionnaire, correction, reminder-consent,
   debrief, localization, and accessibility UX.
8. Build pinned artifacts, SBOM, vulnerability report, and deployment manifest.
9. Deploy to a non-public staging origin and execute every deterministic gate.
10. Restore staging from backup and reconcile deletion.
11. Run accessibility/manual browser review.
12. Run only technical/wording pilot sessions; fix by superseding before included
    enrollment.
13. Freeze exact production hashes and open enrollment.
14. Operate the study without inspecting outcome differences.
15. Stop at the preregistered end/max sample.
16. Freeze data and input watermark.
17. Reproduce analysis through two implementations.
18. Review severe ratings, missingness, deviations, order/carryover, and incidents
    without post-hoc exclusion.
19. Publish completion report and minimized aggregate export.
20. Select exactly one TASK-025 branch or explicitly defer.
21. Delete/retain data according to participant choices and retention schedule.
22. Tear down public access and verify secrets/revoked codes.

## 18. Allowed Changes

- deployment manifests and production-pilot infrastructure;
- study access/session, rate-limit, CSP, origin and admin boundaries;
- one normalized reversible study migration if required;
- backup/restore/deletion reconciliation;
- privacy-safe operational metrics;
- full two-period playtest UX and localization;
- accessibility tooling justified by research;
- recruitment/facilitation/incident/runbook documentation;
- minimized reproducible analysis and report artifacts;
- nonfunctional demand probes already defined by TASK-023.

## 19. Out of Scope

- functional world or character creation;
- ordinary-character promotion;
- authoritative event editor;
- unrestricted dialogue;
- broad new Action types;
- production Push/email/SMS/chat delivery;
- engagement, attachment, obedience, fear, or return optimization;
- session replay, heatmaps, fingerprinting, raw clickstream, or free-text lore;
- collecting names, email, phone, raw IP, full user agent, or social login;
- changing the frozen outcome after inspecting included data;
- dynamically reallocating conditions;
- model-generated personalized questions, summaries, recruitment, or decisions;
- changing Agent identity, relationships, memories, decisions, or world state;
- claims of product-market fit from an internal pilot;
- Temporal/Kubernetes/vector-service migration without a demonstrated failure.

## 20. Test and Quality Gates

Keep every TASK-001–023 gate and add:

- domain/property/schema/TypeScript tests;
- PostgreSQL two-worker activation/report/deletion races;
- protocol/question database immutability;
- period timing and resume tests;
- code expiry/revocation/brute-force/rate-limit tests;
- CSRF, origin, trusted-host, CSP, cookie and cache tests;
- correction-chain and all-required-answer tests;
- withdrawal/reminder/report fencing;
- backup/restore/deletion reconciliation;
- proxy/monitoring/log forbidden-data scans;
- deployment health/rollback/teardown;
- container/SBOM/vulnerability checks;
- Chrome/Firefox and available Edge/WebKit coverage;
- axe plus documented manual keyboard/screen-reader/zoom/reflow/contrast review;
- 32-participant load and budget test;
- full seven-day scenario twice;
- complete infrastructure-enabled backend suite;
- frontend unit, TypeScript, ESLint, Prettier and production build;
- Alembic upgrade/downgrade/re-upgrade on a disposable database and clean drift;
- independent analysis reproduction.

Record exact commands, versions, counts, environment, skips, failures, retries,
incidents, negative results, and costs.

## 21. Definition of Done

TASK-024 is done only when:

- the 41-page product plan and TASK-023 evidence are cited in the decision;
- research and ADR-017 contain measured versioned choices;
- production-pilot threat model and runbooks are exercised;
- frozen protocol/dataset/application/deployment hashes predate included
  enrollment;
- TLS, auth, rate limiting, CSP, log redaction, secrets, backup, restore,
  monitoring, kill switches, admin isolation, rollback and teardown pass;
- protocol/question/presentation immutability is database-enforced;
- access, assignment, response, correction, period, withdrawal, reminder,
  deletion and report races pass on PostgreSQL;
- focused UX completes both periods with real interval/resume behavior;
- automated and documented manual accessibility gates pass;
- no deterministic privacy, provenance, authority, copy, deletion, or stale
  report gate fails;
- at least 8 real participants complete both periods for any non-directional
  conclusion;
- enrollment, missingness, withdrawal, deletion, exclusion, compensation,
  recruitment source, facilitator involvement, device/browser and language are
  reported in aggregate;
- primary, interval, exact, order, carryover, missingness and between-sequence
  analyses reproduce independently;
- every severe safety rating is reviewed without deleting it as an outlier;
- concrete demand probes are analyzed under the frozen branch rule;
- no human result, participant, return, reminder, or branch demand is fabricated;
- exactly one evidence-backed TASK-025 branch is selected, or expansion is
  explicitly deferred;
- row-level retention/deletion choices are executed;
- public pilot access is torn down after the declared window;
- completion report records all failures, incidents, limitations, and negative
  evidence without overstatement.

## 22. Completion Report and TASK-025 Branches

Create `docs/task-024-completion.md` containing:

- research matrix, ADR-017 and security decisions;
- deployment manifest and exact hashes;
- data processors, regions, retention, deletion and teardown;
- recruitment, consent, compensation and facilitation;
- enrollment funnel, evidence class, missingness and deviations;
- assignment balance and period/order/carryover;
- primary comprehension effect and intervals;
- safety, clarity, usefulness, framing and accessibility;
- real-offline return and continued interest;
- correction and ambiguity results;
- demand-probe initiation/completion and autonomy-compatible reasons;
- backup, restore, deletion, incident and log-privacy evidence;
- actual cost and operational budgets;
- exact quality commands/counts;
- limitations and falsified hypotheses;
- one TASK-025 recommendation or explicit deferral.

Permitted TASK-025 branches:

- **World/character creation foundation** only if completed creation probes and
  autonomy/safety gates pass.
- **Ordinary-character promotion** only if repeated promotion probes value
  source-grounded history carry-forward.
- **Dialogue legibility** only if causality passes but relationship experience is
  repeatedly insufficient.
- **Action breadth** only if valid goals repeatedly fail for missing authoritative
  affordances.
- **Return-loop UX/accessibility refinement** if clarity, usefulness, safety,
  return, or accessibility misses.
- **Delivery hardening** only if in-site experience passes and participants
  concretely choose a neutral external channel.
- **Defer expansion** if sample, safety, comprehension, return, interest, concrete
  demand, incident, or deterministic gates are insufficient.

No branch may be selected from clicks, opens, raw return frequency, a single
participant, facilitator preference, product-owner preference, or an LLM judge.
