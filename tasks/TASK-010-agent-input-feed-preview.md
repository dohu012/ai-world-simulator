# TASK-010: Agent Input Feed Preview

## Goal

Add a lightweight frontend harness for the TASK-009 current-agent input endpoint:

```http
GET /demo/worlds/gray-harbor/me/input
X-Demo-Agent-Id: char-chen-mo
```

The panel should make the Observation-only agent input feed visible without exposing raw `OracleResponse`, `ActionIntent`, or `ActionResult` as agent input.

## Scope

- Keep the observer dashboard unchanged.
- Keep the TASK-008 perspective preview unchanged.
- Add a compact `Agent Input Feed` panel below the current-agent preview.
- Use `getGrayHarborCurrentAgentInput()`.
- Cover loading, success, error, endpoint/header usage, and absence of raw action lifecycle labels in tests.

## Non-Goals

- No backend route changes.
- No real Observation Builder.
- No real agent runtime, LLM call, Scheduler, Memory, World Engine, Action Validator, or Oracle submission workflow.
- No production authorization.

## Implementation Notes

- Added `DemoAgentInputFeed`.
- Wired it into the home page below `DemoAgentPreview`.
- Added component tests for loading, success, error, `/me/input` usage, and Observation-only rendering.
- Updated home-page health tests to mock the additional `/me/input` request.

## Verification

- `cd frontend; npm run test`
- `cd frontend; npm run typecheck`
- `cd frontend; npm run build`
- `cd backend; .\.venv\Scripts\python.exe -m pytest`

## Status

Done.
