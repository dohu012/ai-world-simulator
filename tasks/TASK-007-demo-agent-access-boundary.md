# TASK-007: Demo Agent Access Boundary

## Goal

Add a demo-only caller identity boundary on top of the TASK-006 agent-scoped read model.

The fixed demo current-agent endpoint is:

```http
GET /demo/worlds/gray-harbor/me/perspective
X-Demo-Agent-Id: char-chen-mo
```

The backend decides the current demo agent from `X-Demo-Agent-Id`, not from a caller-chosen `agent_id` URL segment.

## Scope

- Keep `GET /demo/worlds/gray-harbor` as the observer dashboard payload.
- Keep `GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective` as an observer/dev-only demo endpoint.
- Add a demo access dependency that accepts only the three fixed special agents.
- Reuse `get_gray_harbor_agent_perspective(agent_id)` for the response.
- Do not implement login, OAuth, JWT, sessions, cookies, user tables, real player-agent binding, Observation Builder, World Engine, Memory, LLM, or Scheduler.

## Implementation Notes

- Added `backend/app/api/demo_access.py` with `require_demo_agent_id`.
- Missing `X-Demo-Agent-Id` returns `401 DEMO_AGENT_ID_REQUIRED`.
- Unknown demo agent ids return `403 DEMO_AGENT_FORBIDDEN`.
- Added `GET /demo/worlds/gray-harbor/me/perspective`.
- Added a frontend helper for the future agent/player-facing direction:
  `getGrayHarborCurrentAgentPerspective()`.
- The observer dashboard remains unchanged and continues to use the observer endpoint plus the existing selected-character dev perspective endpoint.

## Verification

- Backend tests cover Lin and Chen current-agent headers, Lin isolation from Chen private records, missing header, unknown header, and unchanged observer payload.
- Frontend tests cover the current-agent helper URL/header usage and API error propagation without deriving private data from the observer payload.

## Status

Done.
