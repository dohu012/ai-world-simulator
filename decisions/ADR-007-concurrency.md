# ADR-007: Concurrency

## Problem

Scheduled jobs, user input, Agent actions, and background processing may try to mutate the same world concurrently.

## Decision

World-state mutations must be serialized per world through Application-managed transactions and World Engine calls. Scheduled jobs must be idempotent.

## Reasons

- Prevents duplicate events and conflicting outcomes.
- Supports worker retries and restarts.
- Makes repeated execution testable.

## Impact

Future tasks must define idempotency keys or unique constraints for scheduled and retried work.

## Forbidden Actions

- Background jobs mutating state without transaction boundaries.
- Retried jobs appending duplicate `WorldEvent` records.
- Frontend retries causing repeated authoritative actions without idempotency.

## Future Changes

When distributed workers are introduced, update this ADR with lock, queue, and retry semantics.

## TASK-015 refinement (2026-07-26)

State-changing Gray Harbor actions acquire `SELECT ... FOR UPDATE` on the single `worlds` row before reading mutation state. This is the per-world serialization boundary; lock order is world row, state/topology reads, objective updates, then append records. Client character/world versions are domain preconditions. Same-key retries return the first lifecycle. Lock timeout, deadlock, and serialization failures are operational failures and must roll back rather than create fictional rejected actions. Advisory locks and a new event-sourcing dependency were rejected because the durable world row and current SQLAlchemy/PostgreSQL transaction already provide the required boundary.
