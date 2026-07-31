# TASK-020 Progress Evidence

Date: 2026-07-28

Implemented:

- ADR-013 comparison and one selected architecture;
- five strict, exported memory contracts with immutable owner/world provenance;
- deterministic importance admission, fake embeddings, hard-filtered hybrid
  retrieval, score components, stable ordering, bounded whole-record packing,
  lexical fallback, and context freshness hashes;
- reversible normalized migration `20260728_0010` for memories, sources,
  embeddings, fenced jobs, retrieval runs, and candidates;
- initial versioned Gray Harbor evaluation corpus with required and forbidden
  memory labels.
- exactly-once Observation projection into episodic, semantic, emotional, and
  Oracle memory records;
- two-worker fenced deterministic embedding execution and hybrid retrieval audit;
- memory-aware TASK-016 prompts and post-inference freshness checking;
- bounded idempotent stage consolidation with raw-source retention;
- owner memory/retrieval/consolidation APIs, offline evaluation API, and internal
  frontend memory/evaluation surface.
- provider calls outside transactions, bounded transient retry/permanent
  dead-letter classification, and lexical fallback during provider outage;
- observer replay linkage and frontend display for retrieval mode, selected
  memory IDs, context watermark, and bounded context size.

Verified:

- `python -m pytest -q -p no:cacheprovider --basetemp=<workspace>`:
  181 passed, 21 skipped;
- targeted memory and decision-recovery PostgreSQL tests: 12 passed;
- default backend regression: 182 passed, 23 skipped;
- Ruff check and format check: passed;
- mypy: passed;
- deterministic schema export: passed;
- Alembic `0009 -> 0010 -> 0009 -> 0010` and drift check: passed.
- frontend: 34 tests, typecheck, ESLint, Prettier, and production build passed.

This interim report is superseded by `docs/task-020-completion.md`. Subsequent
work completed Oracle outcome linkage, the candidate inspector, production-policy
corpus execution, and the repeatable 212-test infrastructure run. Pgvector remains
an explicitly unavailable and disabled optional deployment path.
