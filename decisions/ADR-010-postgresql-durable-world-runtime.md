# ADR-010: PostgreSQL-backed durable world runtime

- Date: 2026-07-27
- Status: Accepted for the fixed Gray Harbor milestone

## Decision

Use a bounded PostgreSQL state machine behind `WorldRuntimePort`. A separate worker claims due rows with `FOR UPDATE SKIP LOCKED`; persisted generation and claim tokens fence stale workers. PostgreSQL is authority. LISTEN/NOTIFY may reduce polling latency, but notifications are hints and every wake performs an authoritative query. API handlers only issue bounded commands and never host a loop.

## Research matrix

| Option | Version / license | Strength | Rejection or selection |
| --- | --- | --- | --- |
| Temporal Server + Python SDK | SDK 1.27.0; Apache-2.0 | Durable timers, signals, replay, cancellation, time-skipping | Deferred behind the port. Excellent semantics, but adds a server, worker topology, deterministic-code/versioning discipline, history privacy controls and CI services for one fixed world. Adopt when multiple worlds or long histories make the bounded DB scheduler costly. |
| PostgreSQL 17/18 + SQLAlchemy 2.x | PostgreSQL license / MIT | Existing authority; transactional outbox; row locks, `SKIP LOCKED`, advisory locks, LISTEN/NOTIFY | Selected. Lowest removal and operational cost; all lifecycle winners and causal IDs remain in the existing replay database. |
| Celery 5.6 + RabbitMQ/Redis | BSD-3-Clause | Mature retries and distributed execution | Rejected: broker/result-backend topology does not by itself model player signals, simulation time, or replay-safe transitions. |
| APScheduler 4 pre-release docs / 3.x stable | MIT | Persistent stores, leases, async scheduler | Rejected: 4.x migration is still a partial rewrite and its generic job model duplicates the domain lifecycle. |
| Dramatiq/arq | LGPL-3.0 / MIT | Small background workers | Rejected: queue delivery helps execution but not durable decision-window semantics; adds a second truth risk. |
| SimPy 4.1 | MIT | Clear discrete-event and virtual-time concepts | Used as design reference only. The small clock/order functions are dependency-free and persisted. |
| Synchronous API-only | n/a | No new service | Rejected for production runtime: cannot continue offline and request lifetime is not a durable lease. Retained only as bounded deterministic `advance` test control. |

## Executable spike results

`test_world_runtime.py` proves without sleeping: monotonic/fenced clock advancement, pause rejection, stable equal-time order, bounded catch-up, deterministic reply-before-timeout and timeout-before-reply, server-owned Oracle eligibility, and owner-scoped wake selection. Database tables encode unique schedule keys, causal wakes, Oracle decision windows, delivered response/Observation IDs and notification dispatch keys. Migration `20260727_0005` is reversible.

The multi-worker database spike uses the standard queue query shape: ordered candidate selection followed by `FOR UPDATE SKIP LOCKED`, a committed incrementing claim token, and commit-time fencing on runtime generation plus claim token. A crashed worker loses its lease; takeover increments the token. Publication is logically exactly once through unique `published_event_id`/schedule key. LISTEN/NOTIFY is optional because PostgreSQL documents an initial-listen race; workers always rescan after subscribing.

## Time, retries and races

World time never decreases. Equal-time order is `(due_world_time, priority, created_at, id)`. Catch-up is rejected above the configured bound and can resume in another activation. Pause freezes world time. Real-time and world-time deadlines race by persisted instant; an already accepted reply wins an equal instant. The transaction locks one waiting window, changes it once, persists response or typed silence Observation, and emits one outbox key. Transient execution retries are bounded; validation, privacy and stale-generation failures are terminal. Cancellation and supersession are explicit statuses.

## Privacy and history

Rows contain bounded typed parameters, IDs, safe summaries and hashes. They never contain credentials, headers, raw prompts, hidden global facts or chain-of-thought. Player text is bounded player content and is only delivered to the owning Agent through Observation Builder. Workflow/outbox payloads contain safe references, not private content.

## Topology and ceiling

Local/CI: FastAPI + PostgreSQL + an explicit worker command; deterministic tests call the adapter with virtual time. Production slice: the same two processes and database; Redis is not truth. This adapter is intentionally limited to fixed typed events, bounded activation batches and short causal histories. No cron compiler or general workflow DSL may be added. The migration seam is `WorldRuntimePort`; a future Temporal adapter maps schedule IDs to workflow IDs, Oracle replies to signals, deadlines to timers and database mutations to idempotent activities while PostgreSQL remains replay authority.

## Removal plan

Drop the worker adapter and TASK-017 scheduling tables only after draining open windows/outbox records and migrating their IDs/statuses. Domain contracts, API DTOs and replay projection remain. No Agent or World Engine code may import adapter-specific types.

## Sources

- Temporal Python SDK releases and repository: https://github.com/temporalio/sdk-python/releases
- PostgreSQL row/advisory locking: https://www.postgresql.org/docs/17/explicit-locking.html
- PostgreSQL LISTEN/NOTIFY: https://www.postgresql.org/docs/17/sql-notify.html
- Celery brokers: https://docs.celeryq.dev/en/latest/getting-started/backends-and-brokers/index.html
- APScheduler persistent/multi-scheduler guidance: https://apscheduler.readthedocs.io/en/master/userguide.html
- SimPy environments: https://simpy.readthedocs.io/en/4.1.0/topical_guides/environments.html
