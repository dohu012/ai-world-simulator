# TASK-022 Completion and Falsification Report

TASK-022 is complete as an engineering and falsification milestone. The expansion
hypothesis is not accepted; unavailable and negative evidence is recorded without
overstatement.

Implemented: dated research and ADR-015; threat model; versioned three-interval
Gray Harbor corpus and playtest protocol; strict causal claim/offline-summary
contracts and schemas; deterministic source compiler; copy taxonomy; follow,
channel, cap, pause, expiry and DST-aware quiet-hour policy; owner-scoped
`no-store` API; CSRF-protected minimized-event boundary; accessible return-loop
panel; native PWA manifest; and a same-origin, redacted, disabled-by-default
service worker. Migration `20260728_0012` adds normalized preferences, intervals,
summaries, immutable claims, inbox state and minimized playtest events.

The compiler is extractive, calls no model/provider, obtains no world lock, and
cannot mutate simulation state. Fixed tests prove cross-owner, future and unsafe
claims are excluded and source watermarks are deterministic. Default push is off;
high fictional priority cannot bypass caps or quiet hours.

Verified gates: the complete infrastructure-enabled backend suite passes 243
tests; Ruff, Ruff format and strict mypy pass. PostgreSQL migration passes
`0011 -> 0012 -> 0011 -> 0012` and clean drift. A real integration test proves
repeat projection creates exactly one logical inbox item and four immutable
claims, owner-forged mutation fails, read is transition-idempotent, and repeated
playtest instrumentation produces one row. Frontend 35 tests, TypeScript, ESLint,
Prettier and Next.js production build pass. The manifest route is generated.

Not verified: push subscription secret persistence, provider delivery fencing and
revocation, VAPID rotation, live HTTPS Chrome/Firefox/WebKit
subscribe/deny/revoke/expiry/offline receipt/update tests, or a controlled
multi-participant sample. The later consented `n=1` result below provides
directional comprehension and safety evidence, but no control-group interest
margin or delivery-value result.

Browser evidence added on 2026-07-29: Playwright 1.62.0 running the installed
stable Google Chrome channel passes 2/2 tests for the complete no-push view,
source-linked outcome rendering, zero provider calls, service-worker readiness,
permission remaining untouched on load, and a gesture-only permission control.
Playwright browser downloads timed out and Docker later became unavailable, so
the browser test uses an intercepted fixed API response while the earlier real
PostgreSQL integration remains the persistence evidence. This does not claim live
push delivery or Firefox/WebKit coverage.

The durable in-site engineering baseline is complete. Keep external push disabled
unless a later safety-refined in-site loop and live provider matrix both pass.

## Directional human result

On 2026-07-30 one participant explicitly consented to the minimized protocol.
Only coded answers and ratings were retained. The participant answered 5/5 causal
questions correctly (100%), correctly attributed Chen's action to learned route
information and her judgment, wished to continue following Chen, and did not
report feeling prompted or blamed.

Ratings out of five were clarity 3, usefulness 3, and fiction framing 4. The
participant initially supplied pressure and anxiety as 4/5 while interpreting
them as properties of the fictional character environment. After clarification
that the fields measure effects on the participant, both were corrected to 1/5.
The machine-readable report retains the invalidated values, corrected values,
date, and reason code. Safety therefore passes directionally. The sample is n=1,
has no chronological control assignment, and cannot support a confidence interval
or continued-interest margin. It is explicitly directional rather than evidence
of market demand.

The machine-readable aggregate is
`backend/app/scenarios/gray_harbor_return_playtest_report_v1.json`; it contains no
identity, raw text, IP, user agent, or cross-site identifier.

## TASK-023 decision

Do not select a feature-expansion branch yet. Preserve the complete no-push path
and repeat the controlled playtest with the predeclared sample target and
unambiguous participant-directed safety wording. The corrected result does not
support a safety-refinement mandate, but n=1 without a control group also does not
justify creation, broader dialogue, actions, or external delivery.
