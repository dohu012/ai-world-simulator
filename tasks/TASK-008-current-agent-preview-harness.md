# TASK-008: Current-Agent Preview Harness

## Goal

Add a small frontend agent-facing preview harness that consumes the TASK-007 current-agent endpoint:

```http
GET /demo/worlds/gray-harbor/me/perspective
X-Demo-Agent-Id: char-chen-mo
```

The preview should prove the frontend can render a current-agent perspective without selecting `agent_id` from the URL and without deriving private records from the observer dashboard payload.

## Scope

- Keep the observer dashboard unchanged.
- Add a lightweight `Agent Preview` panel under the observer dashboard.
- The panel must use the `/me/perspective` helper added in TASK-007.
- Loading, error, and success states must be tested.
- The panel must not read from or filter the observer payload.

## Non-Goals

- No backend endpoint changes.
- No real login, OAuth, JWT, session, cookie, or user table.
- No production authorization model.
- No real player-agent binding.
- No Observation Builder, World Engine, Memory, LLM, Scheduler, or Oracle submission flow.
- No redesign of the main observer dashboard.

## Implementation Notes

- Added `DemoAgentPreview`, a compact current-agent panel backed by TanStack Query.
- Wired `DemoAgentPreview` into the home page below the observer dashboard.
- Reused `getGrayHarborCurrentAgentPerspective()` so the request uses `X-Demo-Agent-Id: char-chen-mo`.
- Added component tests covering loading, success, error, header/endpoint usage, and no observer-payload fallback.
- Updated home-page health tests to mock the new `/me/perspective` request.

## Verification

- `cd backend; .\.venv\Scripts\python.exe -m pytest`
- `cd frontend; npm run test`
- `cd frontend; npm run typecheck`

## Status

Done.
