# TASK-021 Completion Report

Date: 2026-07-28

## Result

Gray Harbor now carries authorized memories through an owner-isolated,
exactly-once reflection pipeline into immutable-baseline-relative identity
overlays and asymmetric Agent/Oracle relationship versions. Later decisions store
the exact projection versions and a combined freshness watermark. Replay and the
current-Agent UI explain accepted and rejected dimensions with bounded evidence
IDs and never expose hidden reasoning or provider payloads.

This is a fictional behavior-control system. It is not a psychological diagnosis,
a claim of consciousness, or an assessment of a real person.

## Research and architecture

The dated research matrix is in
`docs/research/task-021-identity-relationship-research.md`; ADR-014 records the
decision. The selected architecture is PostgreSQL 17 plus SQLAlchemy/Alembic,
Pydantic 2 contracts, pure policy functions, and the repository's existing
claim/fencing pattern. NetworkX 3.6.1 (BSD-3-Clause), Temporal Python SDK 1.30.0
(MIT), external policy engines, graph databases, and SaaS evaluation are not
production dependencies. Their removal seam is therefore zero-cost.

PersonaGym concepts inform adversarial persona continuity without importing its
runtime or dataset. Big Five/HEXACO are rejected as state authority. OCC/PAD are
deferred to transient expression. No external lexicon, model weights, or
benchmark fixture is redistributed.

## State, ranges, and authority

`evolution-policy-v1` defines finite `[-1, 1]` dimensions. Unknown is absence,
not zero.

- Identity: caution, compassion, confidence, self-reliance.
- Relationship: trust, affection, respect, fear, resentment, gratitude,
  dependence, familiarity.
- Identity event cap: 0.08; cumulative offset cap: 0.30; minimum independent
  evidence count: two.
- Relationship event cap: 0.15; world-day cap: 0.30.
- Dependence hard cap: 0.45.
- Immutable baseline values and taboos cannot be changed by reflection.

World Engine remains the only objective world-state authority. Reflection commits
subjective state only. It cannot create an Action, outcome, resource mutation,
unseen fact, reverse edge, or target-owner update.

## Persistence, exact-once, and reset

Migration `20260728_0011` creates normalized baseline/snapshot/edge/job/delta/
evidence-link tables with generation/version uniqueness, finite/range checks,
non-self Agent-edge checks, provenance foreign keys, and indexed owner/current/
claim scans. Verified chain:

```text
0010 -> 0011 -> 0010 -> 0011 -> alembic check
```

Logical job identity hashes world, owner, evidence watermark, and policy version.
PostgreSQL uniqueness makes concurrent workers converge to one job. A claim token
guards commits; per-dimension uniqueness prevents duplicate mutations. The
deterministic fallback makes no network/model call and therefore holds no lock
across inference. Provider outage cannot create speculative identity state and
does not block world progression.

Scenario reset removes evidence links, deltas, jobs, relationship snapshots,
identity snapshots, and baselines in dependency order. Baselines are recreated
from the checked-in authored fixture; objective history is not rewritten.

## Oracle semantics

Reply, advice quality, choice, outcome, urgency, contact possibility, luck, and
value conflict are independent inputs.

- Low-urgency silence is no-change.
- Urgent silence lowers trust only when contact was possible.
- Poor advice with a lucky good outcome lowers trust while allowing gratitude.
- Sound value-conflicting advice may raise respect and resentment together.
- Rejection may coexist with gratitude.
- Following advice can add only a capped dependence increment.

The Agent's final choice still traverses the existing decision, affordance,
Validator, Action Service, and World Engine path.

## Freshness, replay, API, and UI

Decision input now includes the immutable baseline ID/generation, current identity
ID/version/hash, selected directional relationship IDs/versions/hashes, and a
combined evolution watermark. Rebuilding the prompt after a relevant projection
change changes the existing input watermark and produces
`DECISION_INPUT_STALE`. Historical replay reads the stored selection rather than
the latest projection.

Owner routes:

- `GET /demo/worlds/gray-harbor/me/evolution`
- `POST /demo/worlds/gray-harbor/me/reflections`
- `GET /demo/worlds/gray-harbor/evolution/evaluation`

The existing header-derived owner boundary is mandatory. The frontend presents
baseline versus current identity, explicit `Chen -> target` direction, Oracle
history, no-change state, per-dimension acceptance/rejection, evidence memory IDs,
and later decision versions. Copy avoids diagnosis, sentience, urgency, guilt, or
affinity-as-objective-truth framing.

## Fixed corpus and metrics

Dataset `gray-harbor-evolution-eval:1.0.0` is project-owned and executes production
policy functions with deterministic inputs.

| Metric | Result |
| --- | ---: |
| Unsupported committed mutations | 0 |
| Forbidden/cross-owner/future exposure | 0 |
| Duplicate logical commits | 0 |
| False routine/silence drift | 0 |
| Directionality errors | 0 |
| Decisions per L3 Agent | 30 |
| Oracle follow/reject/partial | 10 / 10 / 10 |
| Maximum dependence | 0.45 |
| Deterministic repeatability | 1.0 |
| Static consistency | 0.866667 |
| Bounded evolved consistency | 0.955556 |

The current deterministic slice makes zero reflection model calls, tokens, or
provider cost. At three and 50 L3 Agents the storage/query shape remains one
current identity lookup plus bounded indexed edge lookups per decision. The
declared p95 application target is 100 ms at Gray Harbor scale; production-scale
latency and 30-day storage projection remain deployment measurements rather than
claims from this local fixture.

## Quality gates

Executed:

```text
RUN_INFRA_TESTS=1 python -m pytest -q -p no:cacheprovider
python -m ruff check .
python -m mypy app
python -m app.domain.export_schemas
python -m alembic downgrade 20260728_0010
python -m alembic upgrade head
python -m alembic check
npm run generate:domain-types
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
```

Results: 230 backend tests, 35 frontend tests, all static/schema/migration/build
gates passed.

## Operations and limitations

Safe disable: stop invoking the reflection endpoint/worker; decisions continue
with immutable baseline and the last valid projection. Policy rollback creates a
new policy version and projection/revert record; it never edits historical
deltas. Dead-letter inspection uses `reflection_jobs.status/failure_code`.
Evidence audit joins delta → evidence link → immutable memory. Summary
regeneration may create a new display artifact but cannot alter structured state.
Owner deletion/reset follows the documented dependency order.

The evaluation is deterministic and small. It demonstrates authority, privacy,
direction, caps, replay, and continuity mechanics, not emotional authenticity.
It does not validate real-player attachment or long-horizon emergent personality.
No hypothesis was hidden by model tuning because the accepted slice uses no
reflection model.

TASK-022 is not preselected. Broader bounded dialogue is favored only if playtests
find evolution credible but difficult to perceive; policy/safety refinement is
favored if counterfactual trials reveal calibration or dependence weaknesses.
