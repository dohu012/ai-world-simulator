# ADR-003: Action Lifecycle

## Problem

Intentions, validation, consequences, and event history can be confused without a strict lifecycle.

## Decision

The lifecycle is `WorldEvent -> Observation -> Agent -> ActionIntent -> ActionValidator -> WorldEngine -> ActionResult -> WorldEvent`.

## Reasons

- Separates attempted action from consequence.
- Requires validation before mutation.
- Keeps event history append-oriented.

## Impact

New action types must define intent shape, validation rules, engine behavior, result shape, and emitted events.

## Forbidden Actions

- Treating `ActionIntent` as success.
- Skipping Action Validator.
- Emitting `WorldEvent` from Agent reasoning.

## Future Changes

Lifecycle changes require updating `docs/architecture-handbook.md`, schema docs, and affected tests.
