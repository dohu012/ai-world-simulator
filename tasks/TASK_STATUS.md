# Task Status

| Task | Status | Notes |
| --- | --- | --- |
| TASK-001 | Done | Project scaffold, infrastructure, health checks, tests, and baseline docs. |
| TASK-002 | Done | Domain contracts, JSON Schema export, TypeScript type generation, fixtures, and contract tests. |
| TASK-003 | Done | Development handbook, architecture handbook, AI collaboration guide, ADRs, and task system. |
| TASK-004 | Done | Fixed world observer frontend slice with research notes, static fixture data, and read-only UI. |
| TASK-005 | Done | Fixed Gray Harbor demo read API, frontend TanStack Query integration, loading/error states, and API-driven observer tests. |
| TASK-006 | Done | Agent-scoped Gray Harbor demo read API and frontend selected-character perspective query, validating fixture/API-level information isolation. |
| TASK-007 | Done | Demo-only current-agent access boundary via `X-Demo-Agent-Id` and `/me/perspective`, showing future agent/player reads should not trust caller-selected URL identity. |
| TASK-008 | Done | Lightweight current-agent preview harness consumes `/me/perspective` with the fixed demo caller header and avoids observer-payload private-data fallback. |
| TASK-009 | Done | Demo current-agent input feed exposes Observation-only agent input at `/me/input`, projecting Chen's Oracle advice into an allowed demo Observation. |
| TASK-010 | Done | Frontend Agent Input Feed preview renders `/me/input` Observation-only records and keeps raw Oracle/action lifecycle data out of agent input UI. |
| TASK-011 | Done | PostgreSQL world tables, idempotent Gray Harbor seed, repository reads, and causal replay API. |
| TASK-012 | Done | All Gray Harbor reads use the PostgreSQL application service; observer replay inspector exposes deterministic causal links. |
| TASK-013 | Done | Deterministic Observation Builder persists visibility-filtered event and Oracle input for each agent. |
| TASK-014 | Done | Idempotent demo wait action traverses Validator, World Engine, atomic persistence, and replay. |
| TASK-015 | Done | Concurrency-safe move, persisted topology, atomic character/world versioning, movement event, isolated runtime Observations, and replay projection. |
| TASK-016 | Done | Auditable Observation-only decisions now include fenced lease takeover, crash recovery without duplicate calls/actions, stale-input rejection, provider failures, privacy fixtures, replay projection, UI states, and clean migration/build gates. |
| TASK-017 | Done | Durable PostgreSQL world runtime, monotonic virtual clock, exactly-once fixed event/wake, restart-safe Oracle reply/timeout winner, fresh authoritative final action, outbox, unified replay, APIs/UI, and real Docker PostgreSQL verification. |
| TASK-018 | Done | Durable multi-channel propagation, append-only belief revision, bounded Chen-Zhou correction dialogue, owner-isolated APIs, observer UI, and PostgreSQL restart/race proof. |
| TASK-019 | Done | Seven-day runtime-only Gray Harbor slice with 30 persisted residents, nine automatic authoritative actions, atomic ledgers/plans, exact-once Day-5 condition, deterministic Day-7 rescue capacity, isolated APIs/UI, and PostgreSQL migration/restart/race proof. |
| TASK-020 | Done | Exactly-once typed memory, fenced async embeddings with retry/dead-letter, owner/time-safe hybrid and fallback retrieval, bounded consolidation, memory-aware decision freshness, Oracle outcome provenance, replay/API/UI inspection, fixed-corpus evaluation, reversible migration, and 212-test PostgreSQL proof. |
| TASK-021 | Done | Immutable identity baselines, bounded versioned identity overlays, asymmetric Agent/Oracle edges, evidence-linked exactly-once deterministic reflection, decision freshness/replay, owner UI/API, fixed adversarial evaluation, reversible migration, and 230-test PostgreSQL proof. |
| TASK-022 | Complete (directionally positive; expansion inconclusive) | Deterministic causal summary, safe policy/copy gates, normalized reversible PostgreSQL persistence, idempotent owner API, reset cleanup, PWA/service-worker no-push path, Chrome browser tests, minimized instrumentation, and a consented n=1 directional playtest are complete. Comprehension was 100%, continued interest positive, participant pressure/anxiety 1/5, and no blame was reported. The sample target/control margin remain unmet and live Push remains disabled, so broader expansion is deferred pending a controlled playtest. |
| TASK-023 | Complete (n=0 directional; expansion deferred) | Frozen research/protocol/privacy/corpus, deterministic AB/BA assignment and analysis, normalized 0013 persistence, access-code/CSRF/kill-switch API, source-fenced two-period UI, idempotent response/correction, demand probe, withdrawal/deletion, aggregate suppression, PostgreSQL race/flow gates, Chrome calm/no-push test and full regressions pass. No human result was fabricated; fewer than 8 completed participants forces the evidence-backed `defer` decision. |
| TASK-024 | In progress (n=0; expansion deferred) | Restore/deletion reconciliation, fresh migration round trip, 32-concurrent activation, 260-test PostgreSQL suite and npm/Ruff/mypy/frontend gates pass. Public enrollment remains stopped by official PostgreSQL image gosu CVEs (1 critical/16 high), TLS/manual screen-reader evidence and the required real-participant gate. |
