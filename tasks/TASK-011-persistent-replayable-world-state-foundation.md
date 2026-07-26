# TASK-011: Persistent Replayable World State Foundation

## Goal

Move Gray Harbor from fixture-only demonstration to a seedable PostgreSQL world with repository-backed observer and replay reads.

## Research Notes

- SQLAlchemy 2 async ORM uses one `AsyncSession` per transaction/task; repository methods use explicit 2.x `select()` queries and avoid implicit lazy I/O.
- Alembic remains the schema-history owner. The new revision creates the eleven MVP domain tables after `system_metadata`.
- PostgreSQL `jsonb` is appropriate for full contract-shaped payloads while stable lookup/order/link fields stay as typed columns. B-tree indexes cover world, time, agent, source, and correlation lookups; broad GIN indexes are deferred until query evidence exists.
- The Python `eventsourcing` library provides aggregate repositories, event stores, notification logs, snapshots, and projections. TASK-011 needs an audit/replay read model, not event-reconstructed aggregate state, so adopting that framework now would impose aggregate/event semantics before the World Engine exists.
- Temporal and Celery are workflow/scheduling choices, outside this persistence/read milestone.

Sources: [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html), [SQLAlchemy session concurrency](https://docs.sqlalchemy.org/en/20/orm/session_basics.html), [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [PostgreSQL JSON types/indexing](https://www.postgresql.org/docs/current/datatype-json.html), [eventsourcing](https://eventsourcing.readthedocs.io/en/stable/).

## Decisions

- Use existing SQLAlchemy 2, asyncpg, Alembic, PostgreSQL; add no dependency.
- Keep Pydantic domain contracts authoritative. ORM rows store their complete JSON representation plus explicit operational columns; repositories validate JSON back into contracts.
- Use an application-level idempotent PostgreSQL upsert seed, never seed business data in schema migration.
- Use append-friendly event/observation/action tables and correlation/source IDs for MVP replay; do not claim full event sourcing.
- Keep existing fixture endpoints during migration and add `/persistent` plus `/replay` database-backed demo routes.

## Delivered

- Eleven persistence tables and indexes.
- Idempotent Gray Harbor seed service/CLI.
- Repository observer read and causal replay projection.
- Database-backed demo observer and replay endpoints.
- Unit/API coverage plus infrastructure-gated migration/seed checks.

## Verification

`python -m pytest`, `ruff check .`, and with infrastructure running: `alembic upgrade head`, `python -m app.services.seed_gray_harbor`.

## Status

Done.
