# TASK-014: Minimal Action Validation and Adjudication

## Goal

Prove one authoritative, deterministic and idempotent action lifecycle:

```text
Observation input
  -> ActionIntent
  -> ActionValidator
  -> GrayHarborWorldEngine
  -> ActionResult
  -> private WorldEvent
  -> replay
```

## Implemented Slice

- `POST /demo/worlds/gray-harbor/me/actions` derives the actor from
  `X-Demo-Agent-Id`.
- The request requires an idempotency key, action type, parameters and reason.
- TASK-014 supports only `wait` with empty parameters.
- Accepted wait actions produce a succeeded `ActionResult` and private
  `WorldEvent`; they do not mutate resources or advance world time.
- Unsupported actions and invalid wait parameters produce a persisted rejected
  `ActionResult` and no event.
- Deterministic IDs and database primary keys provide retry/concurrency safety.
- Repository persistence commits intent, result and optional event atomically.
- Replay exposes the resulting intent/result/event correlation chain.

## Boundaries

- API authenticates only through the existing demo identity boundary.
- Application owns idempotency and transaction orchestration.
- Action Validator is pure and creates no result.
- Gray Harbor World Engine is the only new code that creates `ActionResult` and
  resulting `WorldEvent`.
- Repository only maps, stores and retrieves already adjudicated contracts.

## Deferred

- No movement, inventory mutation, location validation or world-time advancement.
- No Agent decision loop, LLM, scheduler, wake system or automatic action.
- No general World Engine dispatch, action registry or production authentication.
- No frontend mutation controls.

## Evidence

- Accepted, rejected and identity-bound API tests.
- Validator/engine lifecycle unit tests.
- Sequential idempotency test and concurrent unique-key recovery path.
- PostgreSQL integration proves a repeated idempotency key creates no duplicate
  intent, result or event.
- Replay proves intent -> result -> event correlation.
- Chen cannot read Lin's action through agent perspective.
- Full backend infrastructure and frontend regression suites pass.

## Acceptance

> A demo agent can submit one deterministic wait attempt through the complete
> authoritative lifecycle, and retries cannot duplicate its causal history.

## Status

Done.
