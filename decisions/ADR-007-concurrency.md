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
