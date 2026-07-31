# TASK-020 Completion Report

Date: 2026-07-28

## Architecture and dependencies

ADR-013 selects PostgreSQL as canonical memory/audit storage, small internal
writer/retriever seams, deterministic weighted fusion, structured plus lexical
outage fallback, and exact vector ranking at Gray Harbor scale. No new production
Python dependency, hosted evaluation service, dedicated vector service, or model
weight was added.

PostgreSQL 17, pgvector, HNSW/IVFFlat, FTS/trigram, Qdrant, Weaviate, Milvus,
Chroma, gateway/direct/local embeddings, Mem0, Letta, LangGraph, LlamaIndex,
weighted/RRF/model reranking, and repository-native/external evaluation options
are compared with versions, licenses, operational cost, and removal seams in
ADR-013.

The running PostgreSQL image does not advertise the `vector` extension. Extension
creation and approximate-index activation are therefore unavailable and
explicitly disabled. Exact normalized vector ranking and the dependency-free
structured/lexical baseline remain active. A future pgvector activation requires
filtered recall@12 >= 0.99 and a new policy/deployment version.

## Persistence and rollback

Migration `20260728_0010` adds normalized memory items, immutable source links,
revisioned embeddings, fenced jobs, retrieval runs, and candidate score traces.
Foreign keys use `RESTRICT` for audited memory history. Logical memory,
source, embedding revision, job, retrieval context, and candidate uniqueness are
database-constrained.

Verified migration path:

```text
20260728_0009 -> 20260728_0010 -> 20260728_0009 -> 20260728_0010
```

Alembic drift reports no new operations.

## Memory production

The deterministic admission policy considers goals, risk, resources,
irreversibility, contradiction, Oracle relevance, novelty, emotion, and
repetition. Owner-visible Observation records produce strict episodic, semantic,
emotional, or Oracle contracts. Routine noise is rejected and repeat projection
is a logical-key replay.

On the current accumulated Gray Harbor source history:

- 226 owner-visible Observation records examined;
- 34 important memories admitted;
- 192 below-threshold records rejected;
- repeat projection admitted zero and identified all 34 as duplicates;
- all memory sources retain exact world and owner provenance.

Stage consolidation is bounded to 32 sources and 600 estimated tokens, creates a
regenerable stage-summary version, and never changes or deletes raw memories.

## Embedding lifecycle and recovery

Default/CI embeddings use normalized `deterministic-hash-v1`, 16 dimensions,
cosine scoring, zero provider tokens, and zero provider cost. Embedding calls run
after the claim transaction closes. Jobs use worker owner, lease, attempt count,
and monotonically increasing fencing token.

Two PostgreSQL workers produce 34 unique results for 34 jobs. Timeout, rate-limit,
and provider-unavailable failures create bounded deterministic retry.
Permanent/invalid output dead-letters with a stable code. A test acquires the job
row from a second session during the provider callback, proving no inference-time
job lock. Retrieval remains available in `lexical_structured_fallback` mode.

## Retrieval and prompt policy

Hard world, owner, time-cutoff, active-state, and type predicates execute before
scoring. `memory-retrieval-v1` preserves separate lexical, semantic, recency,
importance, goal, entity, location, emotion, contradiction, Oracle, and diversity
components. Ordering is total score descending, world time descending, ID
ascending.

`memory-context-v1` selects at most six complete memory records and 4,000
characters. It never partially truncates a memory. Every candidate records rank,
component scores, selection, and `LOW_SCORE`, `TOKEN_BUDGET`, or
`DIVERSITY_LIMIT` exclusion.

TASK-016 prompts now carry recent Observations separately from selected memories.
The decision watermark hashes Observation IDs plus the versioned memory-context
watermark. Rebuilding the context after inference rejects a stale proposal before
the authoritative action transaction.

## Oracle, replay, privacy, and UI

Oracle memory keeps advice/silence distinct from interpretation, chosen action,
and authoritative outcome. When the durable Oracle window has completed, source
links include the delivered Observation and Oracle window plus the resulting
ActionIntent and generated event identifiers.

Owner APIs derive identity from `X-Demo-Agent-Id`; callers cannot supply an owner,
world, visibility override, vector, or scoring policy. Observer replay exposes
only retrieval IDs, modes, selected memory IDs, budgets, and watermarks. It never
returns embeddings, raw prompts, provider responses, credentials, or
chain-of-thought.

The Gray Harbor UI displays typed subjective memories, time, importance,
confidence, source count, embedding state, evaluation gates, and latest candidate
rank/selection/score/budget. Replay displays decision-memory linkage.

## Evaluation

Corpus `gray-harbor-memory-eval/1.0.0` covers Lin medicine recall, Chen ration,
cache rejection, shipment and Oracle continuity, Zhou checkpoint/capacity recall,
cross-owner, cross-world, future, private Oracle and hidden-fact decoys.

The fixture executes production filtering, scoring, and packing:

| Mode | Cases | Required recall@k | Forbidden exposure | Hard gates |
| --- | ---: | ---: | ---: | --- |
| Hybrid deterministic vector | 3 | 1.0 | 0 | Pass |
| Lexical/structured outage fallback | 3 | 1.0 | 0 | Pass |

Identical versioned inputs produce identical ranking and watermarks. No live or
paid model call is used.

## Quality gates

```text
RUN_INFRA_TESTS=1 python -m pytest -q
212 passed

python -m ruff check .
passed
python -m ruff format --check app tests
passed
python -m mypy app
passed
python -m app.domain.export_schemas
passed
python -m alembic check
passed

npm run test -- --run
34 passed
npm run typecheck
passed
npm run lint
passed
npm run format:check
passed
npm run build
passed
```

The TASK-019 seven-day PostgreSQL integration suite passes twice consecutively
after expanding reset-generation fencing to every `scenario-gN-*` key.

## Remaining limitations and TASK-021 recommendation

The current container lacks pgvector, so approximate HNSW/IVFFlat benchmarks
cannot execute in this deployment and approximate search remains off. The fixed
evaluation corpus is intentionally small, and the deterministic fake embedding is
not a production multilingual quality claim.

TASK-021 should evaluate bounded personality, relationship, and Oracle-trust
evolution from these auditable memories. Recall and privacy gates now pass, while
traits and relationships intentionally remain unchanged; that is the next
evidence-backed continuity gap. Mutation must remain versioned, reversible, and
separate from objective world authority.
