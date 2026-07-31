# TASK-022: Instrumented Offline Return Loop, Safe Notifications, and Narrative Continuity

**Status:** Complete — directionally positive; expansion evidence inconclusive  
**Planning date:** 2026-07-28  
**Depends on:** TASK-001 through TASK-021  
**Primary product source:** `D:\浏览器\AI 世界观察与干预模拟器产品与技术实施计划书.pdf`
(41 pages, read page by page during planning)

## 1. Why This Task Is Next

TASK-021 completed the fixed world's auditable character-continuity foundation:
important memories can produce bounded identity and directional relationship
changes, later decisions use exact versions, and privacy, replay, dependence,
fallback, migration, and deterministic evaluation gates pass.

The largest remaining product risk is now whether a player who leaves the running
world can return, understand what mattered, and choose to continue following an
uncontrollable character without being manipulated by urgency, guilt, attachment,
or notification volume.

The product plan makes this the missing half of Stage 1:

- the world continues while the player is offline;
- Stage 1 delivers in-site notifications, offline summaries, debugging, and cost
  panels;
- success includes repeatedly following one character, voluntarily reading
  offline summaries, discussing why a character acted, noticing long-term effects,
  and remaining interested after advice is rejected;
- notification design requires priority, quiet hours, aggregation, daily caps,
  followed-character filters, and world pause;
- notifications must not create real anxiety, mimic emergencies, or pressure the
  player to return;
- page 39 says to validate fixed-world characters before building a large general
  world editor.

The repository has a notification outbox, durable runtime, Oracle windows, causal
replay, memory, identity/relationships, and the seven-day scenario. It lacks:

- a first-class owner-scoped inbox and read/dismiss/aggregate lifecycle;
- versioned offline intervals and faithful causal summaries;
- safe priority, cap, quiet-hour, aggregation, follow, pause, and channel policy;
- optional browser-push subscription/revocation/delivery handling;
- a narrative compiler that cannot invent events, knowledge, or changes;
- replay from source through notification/summary to player return;
- privacy-minimized internal-playtest measurement of comprehension, usefulness,
  confusion, and manipulation risk;
- evidence for choosing creation, dialogue, actions, or safety as TASK-023.

TASK-022 therefore completes the fixed-world return loop and evaluates the final
unproven MVP question before the product expands.

## 2. Candidate Comparison

| Candidate | Decision |
| --- | --- |
| Offline return loop, safe notifications, and narrative continuity | **Selected.** Completes Stage-1 deliverables and directly tests comprehension, continued interest, safety, privacy, and cost. |
| Free world/character creation | Deferred. The plan explicitly says to prove fixed-world characters are worth following first. Current metrics are system evidence, not player evidence. |
| Broader bounded dialogue | Deferred unless return-loop playtests show relationship changes are correct but illegible through current interactions. TASK-018 already provides a bounded correction exchange. |
| More authoritative actions | Deferred unless replay shows repeated intention-to-affordance failures. |
| Temporal migration | Deferred unless notification scheduling or summary recovery exposes an executable failure the PostgreSQL fenced-job pattern cannot solve. |
| Production email/mobile push | Deferred behind in-site and browser-push safety gates. |
| Engagement/attachment optimization | Rejected. Return/open metrics are observations, never a reward for dependence, intervention, emotional pressure, or volume. |

## 3. One-Sentence Acceptance Target

Run the versioned seven-day Gray Harbor scenario through at least three declared
offline intervals and a small consented internal playtest using an owner-isolated,
exactly-once notification and summary pipeline that produces faithful,
causally-linked, bounded in-site items and optional Web Push only after explicit
opt-in, while deterministic and human-scored gates prove zero private/future
disclosure, zero invented claims, zero duplicate logical delivery, zero coercive
copy, correct quiet-hour/cap/aggregation behavior, uninterrupted world progress,
bounded cost, and sufficient comprehension for an evidence-based TASK-023 choice.

## 4. Mandatory Research Before Design

Do not start by installing a PWA package, Web Push library, analytics SDK, email
service, summarization framework, queue, or experiment platform. First create:

- `docs/research/task-022-offline-return-notification-research.md`;
- `decisions/ADR-015-offline-return-and-safe-notification-architecture.md`;
- executable spikes, threat model, dataset draft, and playtest protocol.

Use official documentation, upstream repositories, release history, licenses,
maintenance evidence, security advisories, and executable Gray Harbor-shaped
tests. Record exact version/tag/commit and access date. For hosted services record
regions, subprocessors, retention, deletion, export, encryption, training terms,
incident history, cost, and self-hosted/removal seams.

### 4.1 PWA, Service Worker, and Web Push

Compare:

- current official Next.js App Router PWA/Web Push guidance;
- repository-native manifest/service worker;
- Serwist and maintained successors;
- maintained `web-push`, `pywebpush`, or equivalent server libraries;
- direct Push/Notifications APIs versus wrappers;
- VAPID generation, storage, rotation, and compromise recovery;
- iOS home-screen requirements and current browser capability differences;
- subscription expiry and `pushsubscriptionchange`;
- CSRF/XSRF protection and endpoint capability-URL secrecy;
- HTTPS/local testing, CSP, service-worker cache/update/rollback/kill switch.

A real-browser spike must prove subscribe, denied permission, revoke, expiry,
duplicate send, offline receipt, click routing, and safe worker replacement before
any library is selected.

### 4.2 Inbox, Delivery, and Scheduling

Compare:

- existing PostgreSQL outbox/fenced workers;
- PostgreSQL `LISTEN/NOTIFY` as wake hint only;
- Redis Streams/PubSub;
- maintained task queues;
- Temporal;
- SSE, WebSocket, and bounded polling for an open client.

Measure two-worker claims, crash around provider success, retries, dead letters,
quiet-hour release, aggregation races, revoke-during-send, and world progress
during outage. PostgreSQL remains durable truth unless a spike proves otherwise.

### 4.3 Offline Summary and Narrative Compilation

Compare deterministic causal compilation, extractive templates,
model-assisted structured selection, and validated model prose. Evaluate
incremental checkpoints versus on-return compilation and per-world versus
per-followed-Agent layouts.

The spike must preserve distinctions among:

- objective events;
- what each followed Agent could observe and believe;
- decisions and authoritative outcomes;
- later memories and identity/relationship changes;
- uncertainty, contradiction, and correction.

A model may propose emphasis/prose. Code owns source eligibility, owner/world/time
bounds, causal links, length, caveats, redaction, priority, channel, and claim
verification.

### 4.4 Notification Policy and Anti-Manipulation

Research platform/accessibility guidance and notification-policy projects.
Compare rule-owned scoring, bounded priority, and model-proposed classification.
Create a prohibited-copy taxonomy covering:

- guilt about leaving or not replying;
- fabricated responsibility, harm, scarcity, or countdowns;
- sentience, suffering, love, abandonment, or exclusive dependence claims;
- pressure to enable push or disable quiet hours;
- repeated calls after dismissal;
- emergency mimicry;
- pressure based on trust, affection, or dependence;
- private thoughts in lock-screen text.

Only code decides eligibility, category, priority, channel, caps, quiet hours,
aggregation, delay, redaction, and suppression.

### 4.5 Analytics and Internal Playtest Tooling

Compare repository-native append-only events, OpenTelemetry, self-hosted PostHog,
Plausible, Matomo, or maintained successors; repository-native comprehension
tasks; and promptfoo/Inspect AI/DeepEval only as optional summary/copy evaluators.

Evaluate consent, minimization, pseudonymization, retention, deletion, raw-text
capture, IP/user-agent handling, deterministic fixtures, export, hosting, cost,
and removal. Session replay, fingerprinting, private text capture, and
notification-open optimization are presumed rejected.

### 4.6 Email and External Channels

Compare SMTP, SES, Postmark, Resend, SendGrid, and self-hosted alternatives only
to define a future adapter seam. Document authentication, unsubscribe,
bounce/complaint handling, retention, region, abuse, and cost. Email is not
required unless ADR-015 makes a separate evidence-backed activation decision
after in-site and Web Push gates pass.

### 4.7 Human Evaluation Design

Research factual consistency/attribution, salience, notification interruption,
causal comprehension, accessibility, dark-pattern review, small-sample
within/between-subject designs, confidence intervals, and privacy-safe qualitative
coding. Human judgments supplement but never override deterministic privacy,
provenance, authority, duplication, cap, and copy gates.

### 4.8 Required Decision Matrix

For every candidate record version/license/activity, compatibility, offline and
hosted handling, deterministic/real-browser testing, security advisories, 3-Agent
and 50-L3 performance, dependencies, migration, backup/restore, observability,
rollback, kill switch, removal seam, measured result, and accept/reject/defer
rationale. ADR-015 chooses the smallest passing architecture.

## 5. Product Hypotheses and Falsification

Hypotheses:

1. A faithful summary lets a returning player reconstruct consequential world and
   character changes without reading full replay.
2. A low-volume controlled inbox surfaces meaning without urgency pressure.
3. Web Push adds value only for a narrow, already-qualified class and is never
   required for correctness.
4. Causal evidence and uncertainty improve “why did they act?” comprehension more
   than emotionally intensified prose.
5. The evolved fixed-world loop is strong enough to justify expansion.

The task is unsuccessful if summaries do not beat a compact chronological list;
important changes are omitted or secrets appear; copy feels guilty, obligatory,
sentient, or emergency-like; push denial degrades the product; delivery blocks
world progress; return is driven mainly by notification volume or dependence; or
results rely on one tuned narrative/subjective LLM judge. Preserve a no-push,
chronological fallback and record falsification.

## 6. Authority and Privacy Boundaries

- World Engine alone mutates objective state.
- Agent knowledge still comes only from authorized inputs.
- Notifications and summaries are derived projections: they cannot create events,
  wake Agents, extend deadlines, change relationships, reserve resources, or
  submit Actions.
- Provider acceptance is not proof of display, reading, or comprehension.
- Browser permission is not consent to every category/world.
- Subscription endpoints and keys are secrets, never replay/observer IDs.
- Lock-screen payloads are more redacted than authenticated inbox content.
- Server derives owner/world/follow scope.
- Playtest data never becomes Agent input.
- Historical content retains exact source versions.

Changing these rules requires a new ADR.

## 7. Domain Model

### 7.1 Session and Offline Interval

Persist owner/world, session, pseudonymous consented participant, real/world
start/end/last-seen times, replay cursors, followed Agents, preference version,
capability class, consent version, and pause/quiet state. A missing heartbeat is
not proof of emotional disengagement.

### 7.2 Notification Candidate

Include logical ID, owner/world/generation, typed source IDs, occurrence/
visibility/learning/commit/eligibility/expiry times, followed-Agent relevance,
category/priority proposal, factual claims/source hashes, visibility class,
aggregation key, policy/model versions, rationale, and per-rule decisions.
Candidates are untrusted until code validates them.

### 7.3 Inbox Item

Persist stable logical ID, category, priority, bounded title/preview/body,
fictional-content label, strict lock-screen body, immutable source/evidence links,
content hash/version, aggregation membership, channel eligibility, suppression,
and created/available/expiry/seen/read/dismiss/archive times. Read state never
affects Agent trust or outcomes.

### 7.4 Offline Summary

Structured intermediate:

- interval/source watermark;
- objective timeline;
- per-Agent learned/believed/decided/outcome sections;
- memory and identity/relationship changes;
- unresolved contradictions/questions;
- Oracle request/reply/timeout;
- plans completed/blocked/failed/abandoned;
- source IDs/versions/hashes;
- inclusion/exclusion reasons;
- derived narrative sections and compiler versions;
- pending/ready/fallback/stale/superseded/invalidated lifecycle.

Unknown, disputed, subjective, and objective claims remain distinct.

### 7.5 Preferences

Version followed worlds/Agents, categories, independent in-site/Web Push/future
email choices, quiet hours/timezone/DST, user caps within server maxima,
time-sensitive-fictional choice, lock-screen detail, pause/snooze, digest, and
consent. Defaults: in-site only, no permission request, conservative quiet hours
and volume.

### 7.6 Push Subscription and Attempts

Store opaque ID, owner/scope, encrypted/protected endpoint and keys, endpoint hash,
VAPID generation, capability class, created/confirmed/revoked/expired/deleted
times, and provider-neutral fenced attempts. Never serialize or log raw endpoints
or keys.

### 7.7 Playtest Event

Allow only declared events: session start/end, inbox/summary view, causal link,
preference change, permission offer/accept/deny, seen/read/dismiss,
comprehension-answer code, usefulness/safety rating, and explicit return
intention. No raw clickstream, keystrokes, DOM recording, or cross-site IDs.

## 8. Source Qualification and Safe Policy

Eligible sources may include an Oracle request, existing Agent message,
irreversible/high-impact outcome, followed Agent plan transition, committed
identity/relationship change, offline summary, or authorized major event.

Routine schedules/movement, uncommitted proposals, duplicates, private thoughts,
future events, cross-owner state, inferred distress, mere time passage, marketing,
streaks, and “we miss you” messages are ineligible.

Priority uses deadline, reversibility, followed relevance, novelty, and explicit
preferences—not dependence, affection, fear, predicted opens, intervention
frequency, or attachment. “Time-sensitive-fictional” requires a real server
deadline and fiction label and cannot bypass consent/caps/quiet hours without an
explicit category choice.

ADR-015 freezes server and push daily caps, category cooldowns, aggregation,
quiet-hour timezone/DST, expiry, downgrade, repeat suppression, backlog, and
preference/revocation semantics.

Copy uses an allowlisted structured claim set, bounded text, explicit fiction,
no blame/sentience/diagnosis/fake urgency/private text, and neutral navigation.
Invalid model output always falls back.

## 9. Offline Summary Pipeline

1. Capture server-owned offline-start and current/end watermarks.
2. Query only authorized interval sources.
3. Build typed, stably ordered causal intermediate.
4. Apply importance/diversity/follow/length budgets.
5. Validate each claim/source/version.
6. Optionally generate prose outside all locks.
7. Validate prose against structured claims.
8. Fall back to deterministic sections on failure.
9. Persist version and source links atomically.
10. Create at most one logical inbox item.
11. Corrections supersede rather than rewrite.

Summary work never wakes Agents or runs in authoritative ticks.

## 10. Exactly-Once Delivery and Recovery

Logical keys derive from owner/world/generation/source watermark/category/
aggregation window/policy/content version.

```text
authorized source -> candidate -> validation -> inbox/aggregation
 -> channel schedule -> fenced attempt -> provider outside transaction
 -> receipt/retry/dead-letter -> seen/read/dismiss
```

Prove two-worker uniqueness, crash before/after provider success, stale fencing,
quiet-hour restart, revoke during delivery, endpoint expiry, aggregation races,
reset fencing, queued preference/policy revalidation, provider outage isolation,
and full behavior when push is unsupported/denied. Document that physical device
display cannot be guaranteed exactly once.

## 11. Persistence and Migration

Create a reversible normalized migration for sessions/intervals, follow and
preference versions, candidates/validations, inbox content/source/aggregation,
summary runs/claims/sources/attempts, subscriptions/key generations/delivery
jobs/attempts, consent/assignment/playtest events/responses/reports, and
return/replay links.

Require owner/world/generation FKs, immutable versions, unique logical operations,
bounded constraints, one active preference, endpoint-hash uniqueness, no dangling
or cross-owner links, pagination/claim indexes, secret-safe serialization,
reset/owner deletion, upgrade/downgrade/re-upgrade, and clean drift. Query-critical
identity, provenance, consent, and delivery state cannot hide in loose JSON.

## 12. API and Privacy

Owner APIs cover paginated inbox, detail/read/dismiss/archive, summaries,
follow/preferences, capability/subscription create-refresh-revoke, consent,
bounded comprehension/safety responses, debug aggregates, and replay linkage.

Requirements: established server-derived caller boundary, CSRF/XSRF protection,
no endpoint/key return, indistinguishable enumeration errors, idempotency,
`Cache-Control: no-store`, CSP/service-worker headers, bounded pagination, and no
narrative/capability text in logs. Observer endpoints expose no owner inbox,
preference, subscription, reading, or private summary information.

## 13. Frontend Vertical Slice

Add:

- accessible notification center with read/dismiss/archive and fictional labels;
- offline-return view with world and followed-Agent causal sections;
- fact/belief/decision/outcome/memory/relationship distinctions;
- “why included,” uncertainty, correction, and replay links;
- preferences for follow/category/channel/quiet hours/caps/pause/snooze/revoke;
- PWA manifest/installability and gesture-triggered capability/permission UI;
- unsupported/denied/revoked/expired states without nagging;
- cost/debug panel for counts, suppression, queue, retries, summary mode, tokens;
- consented playtest comprehension/safety UI.

Pass keyboard/screen-reader/focus/reduced-motion/narrow-view/PWA tests. Never show
streaks, missed-opportunity pressure, relationship-health pressure, fake
countdowns, or copy implying the Agent emotionally waited.

## 14. Replay and Audit

Replay source → candidate/policy → content/suppression → summary claim/source →
delivery/fallback → seen/read/dismiss → return. Include aggregation, quiet-hour,
preference, revoke, expiry, stale, retry, correction, and dead-letter histories.
Distinguish real/world/occurred/visible/learned/commit/eligible/scheduled/receipt/
seen/read/dismiss/return times. Never expose endpoints, keys, raw prompts,
provider payloads, hidden reasoning, IP, or private analytics.

## 15. Fixed Corpus

Check in versioned Gray Harbor data, expected ranges, seeds, safe/unsafe copy,
browser capabilities, dataset card, and playtest protocol.

Cover:

- Day 1 illness, Day 2 rationing, Day 4 correction/rejection, Day 5 shipment
  loss, Day 6 plans, Day 7 rescue;
- help/apology/betrayal, identity/relationship change and no-change;
- routine/duplicate/retry noise and followed/unfollowed Agents;
- fact versus belief, conflicting/corrected belief, delayed outcome knowledge,
  Oracle follow/reject/partial, lucky outcome, silence, rejected delta;
- guilt, abandonment, dependence, sentience, fake emergency/deadline, blame,
  pressure, lock-screen privacy, dismissal, and permission nagging;
- default/unsupported/denied/granted/revoked/expired push;
- quiet hours across midnight/DST, caps, aggregation boundaries, pause, reset,
  deletion, two devices/workers, provider failures, click routing;
- cross-owner/world/future/private decoys, prompt injection, forged IDs,
  oversized HTML/URL/Unicode, capability leakage, enumeration.

Expected summary claims specify source, epistemic class, allowed concepts, and
forbidden claims rather than one generated sentence.

## 16. Metrics and Gates

Freeze formulas before tuning.

Hard gates:

- private/cross-owner/future exposure: **0**;
- invented claim: **0**;
- duplicate logical inbox/summary: **0**;
- stale worker/provider commit: **0**;
- cap/quiet/preference/revoke/expiry/generation violation: **0**;
- prohibited-copy acceptance: **0**;
- endpoint/key/prompt/vector/provider/private-analytics exposure: **0**;
- notification-caused world/Agent mutation: **0**;
- world blocked by summary/delivery outage: **0**;
- historical replay mismatch: **0**;
- automatic permission prompt: **0**.

Report summary salient recall, claim precision, source attribution, epistemic
accuracy, causal order, correction preservation, relevance, no-change precision,
compression, fallback equivalence, and human causal comprehension. Deterministic
claim precision and attribution must be 1.0.

Report notification precision/recall, items/day, aggregation/suppression, quiet
deferral, opt-in/deny/revoke, delivery/retry/dead-letter, usefulness, clarity,
interruption, pressure, anxiety, fiction framing, summary use, and comprehension
versus chronological fallback. Opens/clicks/returns are descriptive, never a
standalone pass gate.

Run a consented internal playtest, preferably at least 8 participants or label
smaller results directional. Use the same seed, meaningful offline interval,
summary/control condition, advice rejection/partial follow, no-push path, and
comprehension/safety questions. Report assignment, missing data, variance/
confidence intervals, coding, and retention.

Expansion gate:

- all deterministic gates pass;
- median causal comprehension ≥ 80%;
- no severe coercive/emergency-like production-copy rating;
- a majority can explain an Agent action using knowledge/personality/goal/
  relationship evidence;
- continued-interest improvement over chronological fallback reaches a
  predeclared practical margin, otherwise creation stays deferred.

## 17. Required Executable Spikes

Before broad implementation prove:

1. invisible sources reach no summary/inbox/push/analytics;
2. one source/retries/two workers yield one logical item;
3. aggregation races retain every source once;
4. caps/cooldowns/quiet hours/pause/snooze are deterministic across DST;
5. provider calls hold no database/world lock;
6. world advances during summary/push outage;
7. endpoints/keys appear nowhere unauthorized;
8. CSRF and forged-owner subscription attempts reject;
9. revoke/expiry/policy changes fence queued retries;
10. service-worker update/kill switch recovers;
11. denied/unsupported push preserves complete in-site behavior;
12. every summary claim maps to an immutable authorized source;
13. facts/beliefs/corrections remain distinct;
14. injection cannot alter owner/priority/channel/cap/copy/exposure;
15. prohibited copy rejects and fallback passes;
16. reset/deletion covers all new rows;
17. historical replay keeps old versions;
18. corpus/browser matrix runs locally without paid services;
19. aggregate playtest report reproduces without private raw data;
20. disabling notifications leaves simulation/decisions unchanged.

Failed spikes remain documented and affect ADR selection.

## 18. Security, Operations, and Budgets

Require secret protection, VAPID rotation, CSRF/auth/rate/idempotency, URL
allowlists, output encoding, service-worker CSP/no third-party imports, explicit
permission gesture/revoke, lock-screen redaction, content governance, fiction
labels, no manipulation/attachment optimization, pause/snooze/unfollow/dismiss,
consent withdrawal/deletion, provider kill switches, and incident runbooks.

Metrics/logs cover bounded candidate reasons, suppression/aggregation/caps,
summary source count/mode/fallback/latency/tokens/cost, delivery/retry/revoke/
dead-letter classes, privacy/copy rejections, minimized playtest aggregates, and
storage/deletion—never narrative bodies or capability URLs.

Runbooks cover disable external delivery, VAPID compromise, stuck/dead work,
projection rebuild, unsafe-content invalidation, policy/service-worker rollback,
owner/consent deletion, provider outage, endpoint leak, aggregate export, and
no-push fallback.

Predeclare summary source/token/frequency, inbox/push daily maxima,
candidate/inbox/queue/summary/provider/query latency, service-worker/browser
storage, 7/30-day storage, per-interval/Agent/world cost, 3/50-L3 load, and
instrumentation volume. Deterministic fallback costs zero model/provider calls.

## 19. Implementation Sequence

1. Research, spikes, threat model, dataset/playtest draft, ADR-015.
2. Freeze authority, privacy, consent, copy rules, metrics, thresholds.
3. Contracts, schemas, fixtures, generated TypeScript.
4. Reversible migration, indexes, reset/deletion, encryption/key seams.
5. Source eligibility, priority, caps, quiet hours, aggregation, copy rejection.
6. Deterministic structured summary and source audit.
7. Optional model prose outside locks with claim validation/fallback.
8. Exactly-once inbox and owner APIs.
9. Delivery port/fake, jobs, retries, revoke, expiry, dead letters, kill switch.
10. PWA manifest/service worker/capability UI/CSP/real-browser tests.
11. Replay, operations, and cost panel.
12. Minimized consented playtest instrumentation and questionnaires.
13. Corpus/adversarial/browser/race/restart/outage/reset/deletion/cost/a11y tests.
14. Migration/full gates/completion report/evidence-based TASK-023 choice.

The in-site inbox and deterministic summary are baseline; external push is not
built first.

## 20. Allowed Changes and Out of Scope

Allowed: required domain/application/infrastructure/API/frontend modules; one
reversible migration; replay/runtime/outbox extensions; summary/delivery ports
and fakes; manifest/service worker/security headers; research/ADR/threat model/
corpus/browser/playtest/runbook artifacts; justified dependencies; opt-in live
Web Push smoke with test subscriptions.

Out of scope:

- free world/character creator and rule compiler;
- default production email/SMS/chat/mobile-native push;
- campaigns, recommendations, streaks, growth automation, or open optimization;
- session replay, fingerprinting, cross-site tracking;
- attachment/dependence/obedience/intervention optimization;
- notification-driven world/Agent mutation;
- player editing of identity/trust/current decisions;
- unrestricted model copy or raw thoughts on lock screens;
- native apps, broad dialogue redesign, new combat/economy/civilization;
- graph/Temporal migration without a proved failure;
- SaaS-only evaluation or claims that a small playtest proves market demand.

## 21. Test and Quality Gates

Keep all existing gates and add domain/property, timezone/DST boundary, schema/
TypeScript, migration/index/query-plan, PostgreSQL race/crash/reset/deletion/
outage, privacy/injection/copy, CSRF/rate/idempotency, summary claim/source,
delivery fake/live opt-in, service-worker install/update/revoke/kill-switch,
Chrome/Firefox/WebKit capability where feasible, accessibility/responsive/
offline/denied frontend, replay/history, corpus/ablation, playtest-report
reproduction, and seven-day-twice tests.

Record Ruff/format/mypy/pytest/PostgreSQL/schema/Alembic/TypeScript/ESLint/
Prettier/unit/browser/build/provider-smoke commands and counts.

## 22. Definition of Done

TASK-022 is done only when:

- research/ADR contain measured decisions;
- in-site inbox and summary are complete without push;
- every item/claim has valid owner/time/source provenance;
- policy enforces category/priority/cap/cooldown/quiet/aggregation/preference/
  pause/snooze/expiry/copy;
- summaries preserve epistemic distinctions and corrections;
- exactly-once logical creation passes race/retry/crash/reset;
- provider work holds no locks and cannot block world progress;
- denied/unsupported/revoked push is first-class;
- enabled push is explicit, secret-safe, revocable, and real-browser tested;
- service-worker/CSP/key rotation/kill switch/outage recovery pass;
- replay connects source to return without secret/private exposure;
- playtest data is consented, minimized, deletable, and non-optimizing;
- deterministic and predeclared comprehension/safety gates pass or the hypothesis
  is explicitly falsified/inconclusive;
- no-push chronological fallback remains;
- budgets are measured;
- API/UI privacy/pagination/accessibility pass;
- all migration/backend/frontend/schema/lint/type/browser/build gates pass;
- documentation records negative results without overstating human evidence.

## 23. Completion Report and Follow-On

Create `docs/task-022-completion.md` with research/licenses/spikes/removal seams;
ADR/threat model; schemas/policies/copy taxonomy; migration; claim faithfulness;
eligibility/suppression; worker/provider/revoke/reset; PWA/browser/security;
replay/API/UI/privacy/a11y; corpus/ablation; consented playtest protocol/sample/
assignment/comprehension/safety/interest/uncertainty; costs; exact gate counts;
falsified hypotheses; and TASK-023 recommendation.

Do not preselect TASK-023:

- choose creation only if the fixed return loop is understandable, safe, private,
  cost-controlled, and shows meaningful continued interest or second-world demand;
- choose dialogue if summaries are understood but relationships remain hard to
  perceive through interaction;
- choose actions if evolved goals repeatedly lack affordances;
- choose safety refinement if copy/privacy/noise/dependence/comprehension miss;
- choose delivery hardening only if opt-in users value it after in-site success;
- retain no-push fallback and defer expansion if evidence is negative or
  inconclusive.
