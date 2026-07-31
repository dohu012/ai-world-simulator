# ADR-013: Auditable Hybrid Long-Term Memory

- Status: accepted
- Date: 2026-07-28
- Scope: fixed Gray Harbor L3 Agents

## Decision

Keep canonical memory and audit data in PostgreSQL 17 behind small internal
`MemoryWriterPort` and `MemoryRetrieverPort` contracts. Use structured filters and
lexical retrieval as the always-available baseline. Exact cosine search is the
vector correctness baseline; approximate search stays disabled below 50,000 active
memories per owner and may be enabled only when filtered recall@12 is at least
0.99. Embeddings are asynchronous, revisioned derived indexes. The default and CI
adapter is a 16-dimensional normalized deterministic fake; a production embedding
adapter must use the existing provider-neutral gateway boundary.

Ranking policy `memory-retrieval-v1` is deterministic weighted fusion:
lexical .20, semantic .20, recency .10, importance .18, goal .10, entity .07,
location .04, emotion .04, contradiction .03, Oracle .04. Hard owner, world,
cutoff, active-state, type, and source-visibility predicates execute before
scoring. Ties are total score descending, world time descending, ID ascending.
Prompt policy `memory-context-v1` admits at most six complete records and 4,000
characters; it never truncates a record. Retrieval traces retain every eligible
candidate, score component, selection, and exclusion reason.

Memory is subjective evidence, never world truth. Episodic, semantic, emotional,
Oracle, and stage-summary records preserve immutable provenance. Semantic memories
project the belief ledger without replacing it. Advice, selected action, and
authoritative outcome remain separate. Consolidation supersedes summaries but
never deletes source memories. Policy, model, tokenizer, packing, admission, or
weight changes require a new version.

## Dated comparison (evidence frozen 2026-07-28)

| Candidate | Version/release checked | License | Result and removal seam |
| --- | --- | --- | --- |
| PostgreSQL | 17.5 / 2025-05-08 | PostgreSQL | Adopted canonical store; transactionality and owner predicates match existing deployment. |
| pgvector | 0.8.0 / 2024-10-30 | PostgreSQL | Deferred deployment dependency. Exact baseline first; HNSW iterative scans improve selective filters, IVFFlat requires training and probes. Extension readiness must gate activation. |
| PostgreSQL FTS/trigram | PostgreSQL 17.5 | PostgreSQL | Adopted lexical design; bilingual token limitations are covered by structured and vector lanes. |
| Qdrant | 1.14.1 / 2025-05-13 | Apache-2.0 | Rejected for MVP: second consistency/backup authority. Port permits later adapter. |
| Weaviate | 1.30.5 / 2025-05-20 | BSD-3-Clause | Rejected: second service and schema lifecycle. |
| Milvus | 2.5.10 / 2025-05-13 | Apache-2.0 | Rejected: operational footprint exceeds corpus need. |
| Chroma | 1.0.9 / 2025-05-15 | Apache-2.0 | Rejected: weaker transactional provenance boundary. |
| Structured + lexical only | repository native | project | Adopted outage/removal baseline; all correctness tests run with no vector dependency. |
| OpenAI-compatible gateway embedding | internal gateway | project | Selected production seam; direct SDK/HTTP remains adapter-only. |
| Sentence Transformers | 4.1.0 / 2025-04-23 | Apache-2.0; model-specific weights | Deferred opt-in local adapter; no model download in CI. |
| FastEmbed | 0.6.1 / 2025-05-15 | Apache-2.0; model-specific weights | Deferred; ONNX is attractive but adds weights/runtime. |
| Mem0 | 0.1.102 / 2025-05 | Apache-2.0 | Rejected as authority: hidden storage/prompt workflow conflicts with immutable source audit. |
| Letta | 0.7.12 / 2025-05 | Apache-2.0 | Rejected: agent runtime is broader than the memory port. |
| LangGraph | 0.4.5 / 2025-05 | MIT | Rejected for production memory; existing runtime remains workflow authority. |
| LlamaIndex | 0.12.37 / 2025-05 | MIT | Rejected: unnecessary RAG orchestration. |
| Weighted fusion | repository native | project | Adopted for inspectable components and stable ordering. |
| Reciprocal Rank Fusion | repository native spike | project | Deferred; useful with calibrated independent rankers but obscures absolute budget threshold. |
| Cross-encoder/LLM rerank | adapter port | model-specific | Deferred; outage/cost/privacy do not justify it at Gray Harbor scale. |
| Ragas / DeepEval / Phoenix | 0.2.15 / 2.9.1 / 8.25 (2025-05) | Apache-2.0 | Offline-only candidates; no production or CI dependency selected. |
| LangSmith | hosted/current | proprietary terms | Rejected for private default evaluation. |
| promptfoo | 0.110 / 2025-05 | MIT | Deferred opt-in; repository-native golden pytest is authoritative. |

All candidates support Linux containers; Python clients generally support Python
3.12 and Windows, while server products require Docker/WSL for parity. Dedicated
stores introduce separate schema, backup, restore, security, and recovery paths.
The retained implementation uses only SQLAlchemy/Alembic/Pydantic already present,
exports JSON-compatible records, and can remove vector search without changing
canonical memories.

## Spike results and predeclared gates

The Gray Harbor fixture uses owner/world/time/type filters plus future and
cross-owner decoys. Repository-native tests prove deterministic admission,
bilingual fake embedding stability, pre-ranking privacy filters, lexical fallback,
stable ties, complete-record packing, and context-watermark freshness. The fixed
corpus gates are required recall@k 1.0, forbidden exposure 0, deterministic
identity 1.0, hybrid nDCG@k at least .90, and fallback success 1.0.

Approximate pgvector benchmarks, extension backup/restore, and real PostgreSQL
two-worker fencing are deployment gates, not claims made by the pure offline
spike. Until they pass, approximate activation is forbidden.

## Failure, privacy, and operations

Embedding timeout/rate limit/provider outage leaves a fenced durable job and uses
lexical/structured mode. Permanent errors dead-letter with a stable code. No world
transaction remains open during inference. Stored summaries are untrusted,
length-bounded data and are serialized as delimited JSON fields, never roles or
instructions. Logs expose IDs, versions, counts, timing, and codes, not memory
text, prompts, vectors, credentials, or provider payloads.

Budgets: one admitted memory per logical source/policy, 12 candidates per lane,
six final memories, 4,000 memory characters, two embedding attempts, 60-second
lease, batch 32, consolidation maximum 64 sources/600 estimated tokens, and p95
retrieval target 100 ms at the fixed-corpus scale.
