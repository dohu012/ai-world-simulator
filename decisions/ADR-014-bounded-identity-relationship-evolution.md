# ADR-014: Bounded identity and directional relationship evolution

- Status: accepted
- Date: 2026-07-28
- Scope: fictional Gray Harbor L3 Agents

## Decision

Use immutable authored identity baselines, versioned derived overlays, and
PostgreSQL directional edges. Keep eligibility and mutation in repository-native
Pydantic contracts and pure functions. A model may propose evidence interpretation
only; code owns owner/world/time filtering, independent-evidence thresholds,
allowed dimensions, caps, cooldowns, freshness, and commits.

Policy `evolution-policy-v1` uses `[-1, 1]` finite dimensions. Identity changes
require two independent evidence keys, cap each event at `0.08`, and cap cumulative
offset from baseline at `0.30`. Relationship changes cap each event at `0.15` and
each world day at `0.30`; dependence has a hard upper bound of `0.45`. Unknown is
represented by absence, not zero. Baselines and committed deltas are append-only.

Oracle assessment separates response, advice quality, independent choice, outcome,
value conflict, urgency, and contact possibility. Silence is no-change by default;
only urgent silence when contact was possible creates a small trust delta. A lucky
outcome cannot convert poor advice into sound advice.

## Architecture and authority

```text
authorized Observation/memory -> fenced reflection proposal (untrusted)
 -> pure per-dimension policy -> append delta + new projection + audit event
 -> later decision records exact versions -> existing Action/World Engine
```

No graph database, policy engine, external evaluator, or new workflow runtime is
adopted. PostgreSQL remains the canonical owner-isolated audit store. The existing
claim/lease/fencing pattern is reused and model work occurs after the claim
transaction closes.

## Alternatives

Big Five/HEXACO are rejected as diagnoses and as writeable state. Their evaluation
concept of cross-situation consistency is useful, but the product-native
trait/value/desire/fear/taboo schema maps more directly to executable fictional
choices. OCC/PAD are deferred to transient expression; they do not authorize
durable identity changes. NetworkX/igraph are unnecessary for current indexed
edge queries. Temporal adds a service and replay authority without a demonstrated
failure of the existing jobs. External evaluation tools remain removable,
opt-in supplements; checked-in pytest cases are the acceptance authority.

## Failure and removal

Provider outage commits no speculative identity change. Explicit direct
relationship rules may still run through the same caps and evidence checks.
Evolution can be disabled while current snapshots remain readable; decisions then
use immutable baseline plus the last valid projection. Removing evolution means
dropping derived context selection, not rewriting baselines, decisions, memories,
actions, or world history.

