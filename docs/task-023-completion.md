# TASK-023 completion report

Date: 2026-07-30  
Decision: **defer expansion**  
Evidence class: **directional / no included participant (`n=0`)**

TASK-023 completed the engineering and preregistration gate without inventing
human evidence. ADR-016 selects a repository-native, removable architecture. The
privacy threat model, frozen protocol, fixed `gray-harbor-product-validation:
1.0.0` corpus, deterministic assignment and standard-library aggregate analysis
are checked in before any included enrollment.

Two matched Gray Harbor intervals contain rejection, partial follow, correction,
decision and irreversible outcome cases. Presentation contracts require the
causal and chronological conditions to have exactly the same source tuple set.
Future, private, cross-owner and prompt-injection decoys are forbidden. The
ambiguity regression rejects TASK-022-style world/character wording and accepts
only participant-directed “caused to you” wording.

Migration `20260730_0013` adds normalized protocol, opaque participant, consent,
period/exposure, coded response/correction, demand-probe and aggregate-report
records. Study models have no path into observations, memories, reflection,
decisions or authoritative world ticks.

The focused `/playtest` route provides consent/privacy and fictional framing,
progressive source disclosure, participant/world safety separation, bounded
Stage-2 probes, live status, focus restoration, pause and withdrawal controls.
It contains no countdown, streak, automatic permission request, external script,
functional editor, or model call.

Human outcomes are intentionally absent: enrolled 0, completed 0, withdrew 0,
excluded 0, missing 0. Paired effect, variance, order/carryover, safety medians,
real-offline return, continued interest and branch demand therefore cannot be
estimated. Small cells are suppressed and analysis returns `defer` below eight.

The durable API now covers frozen protocol retrieval, default-paused enrollment,
opaque access-code authentication, CSRF, deterministic assignment, exact
presentation retrieval, exposure, return, bounded response, idempotency,
append-only correction, probe, period completion, withdrawal and deletion.
Admin aggregate access is separately keyed and suppresses small cells.

Verified gates:

- real PostgreSQL `0012 -> 0013` upgrade and clean Alembic drift;
- self-deleting consent/response/correction/probe/withdrawal flow;
- two concurrent enrollment workers produce one participant and assignment;
- TASK-023 backend unit/API/infrastructure tests: 10 passed;
- complete infrastructure-enabled backend suite: 253 passed;
- frontend suite: 37 passed;
- Ruff, TypeScript, ESLint and Prettier pass;
- Next.js 15.5.21 production build passes, including static `/playtest`;
- installed Chrome playtest gate: 1 passed at 320px with calm/no-push assertions.

The earlier build timeouts were caused by the foreground execution budget; the
same build completed normally when allowed to finish in the background. The
earlier timezone failures were corrected by declaring and installing Windows
`tzdata`. Mypy 1.20.2 still reports an internal tool error under Python 3.14 and
is recorded as an environment limitation rather than a product result.

No included human participant was recruited in this implementation session:
enrolled 0, completed 0, withdrew 0, excluded 0, missing 0. Therefore causal
effect, variance, order/carryover, safety medians, real-offline return and demand
cannot be estimated. The preregistered sample gate mandates **defer Stage 2**.
