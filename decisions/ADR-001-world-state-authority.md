# ADR-001: World State Authority

## Problem

Future modules will observe, suggest, validate, persist, narrate, and schedule world changes. Without a single authority, objective state will become inconsistent.

## Decision

World Engine is the only module allowed to modify authoritative world state and create `ActionResult`.

## Reasons

- Centralized mutation preserves causality.
- `WorldFact`, `WorldEvent`, and `ActionResult` stay coherent.
- LLM output remains advisory or expressive, not authoritative.

## Impact

Application use cases route state-changing work through World Engine. Repositories persist results but do not decide them.

## Forbidden Actions

- API routes directly updating world state.
- Agents directly producing `ActionResult`.
- Model Gateway writing state to the database.
- Repository methods deciding consequences.

## Future Changes

Changing this requires a new ADR naming the replacement authority and migration plan.
