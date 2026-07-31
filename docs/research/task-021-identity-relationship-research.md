# TASK-021 identity, relationship, and trust research

Date/access date: 2026-07-28. This concerns fictional behavior controls, not
clinical diagnosis or claims about real people.

## Decision matrix

| Area | Candidate checked | Version / license | Executable fit and decision |
| --- | --- | --- | --- |
| Persona continuity | PersonaGym | repository current, Apache-2.0 | Useful adversarial persona-consistency concept; no runtime dependency. |
| Persona continuity | CharacterEval / RoleBench | published datasets, research-specific terms | Concepts adapted; fixtures not redistributed because dataset licenses and generated-character provenance require separate review. |
| Personality | Big Five/IPIP, HEXACO | framework/data licenses vary | Rejected as diagnosis/state authority; dimensions do not map cleanly to authored values and taboos. |
| Personality | project-native schema | repository-native | Accepted: observable, versionable fictional controls and immutable core commitments. |
| Affect | OCC, PAD/VAD | conceptual; lexicon licenses vary | Deferred to transient narrative expression; not durable-state evidence. |
| Relationships | PostgreSQL 17 directed edge | PostgreSQL license | Accepted: indexed asymmetric lookup, transactions, historical versions, owner isolation. |
| Relationships | NetworkX 3.6.1 | BSD-3-Clause | Spike semantics work, but rejected dependency: in-memory graph adds no MVP query benefit. |
| Relationships | igraph / graph database | maintained; license/service varies | Rejected: operational and synchronization cost exceeds three/50-Agent fixture. |
| Update rule | bounded additive / EMA / Beta | repository-native math | Bounded additive accepted for legibility; EMA and Beta deferred until evidence is calibrated enough for priors/decay. |
| Policy | Pydantic 2 + pure functions | MIT | Accepted: strict typed input, deterministic reason codes, replay, no untrusted code. |
| Policy engine | general rules engines | project-dependent | Rejected: dynamic rules increase versioning/security surface without improving current finite policy. |
| Evaluation | pytest 8.3+ | MIT | Accepted deterministic authority: fake provider, state-transition and privacy graders. |
| Evaluation | Inspect AI, promptfoo, DeepEval, Ragas | maintained, permissive (component terms vary) | Deferred opt-in. No SaaS or subjective judge may override hard gates. |
| Workflow | existing PostgreSQL fenced jobs | repository-native | Accepted: already proves lease/fencing/restart and lock-free inference. |
| Workflow | Temporal Python SDK 1.30.0 | MIT | Rejected for MVP: new service/worker/replay authority and migration cost. |

Sources were official project repositories, release histories, documentation, and
licenses accessed on the date above. Hosted services were not selected, so no
private Agent text is uploaded and retention/region/training terms are inapplicable.
Any future hosted adapter requires a separate data-processing review.

## Measured spikes

Pure policy tests execute in under 0.1 seconds locally and show: two independent
items are required for identity change; `0.081` exceeds the per-event cap; future,
cross-owner, and stale-watermark evidence rejects before mutation; low-urgency
silence causes no trust change; poor advice plus a lucky outcome lowers trust while
allowing gratitude. The representation is asymmetric because the owner/subject
key is an input to every validation and stored edge.

At three and 50 L3 Agents, current queries are one indexed current snapshot lookup
per Agent and bounded edge lookups; an in-process graph benchmark provides no
durability or isolation. All code is local/offline and deterministic. Removal seam:
omit derived projections from decision context and keep the immutable baseline.

## Security and benchmark licensing

Narrative evidence is bounded untrusted data, never executable instructions.
IDs, visibility time, ownership, freshness, finite-number constraints, and caps
are checked in code. No third-party model weights, lexicons, or benchmark records
are copied. The checked-in Gray Harbor corpus is project-owned; external benchmark
ideas are adapted as test categories only.

