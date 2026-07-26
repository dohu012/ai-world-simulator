# TASK-006: Agent-Scoped Demo Read API

## Background

TASK-004 built the fixed Gray Harbor observer UI with frontend fixture data.
TASK-005 moved that observer data behind the backend read-only API:

```text
GET /demo/worlds/gray-harbor
```

That endpoint intentionally returns the whole observer payload because the observer UI is allowed to see objective events, all special characters, per-agent observations, beliefs, Oracle requests/responses, action intents, and adjudicated results.

The next milestone should validate ADR-002 Information Isolation more directly. The frontend currently can still receive the full observer payload and then filter observations/beliefs locally for the selected character. That is acceptable for an observer dashboard, but it is not the right boundary for a future agent-facing or player-facing character perspective.

TASK-006 should add the first agent-scoped read API for the fixed demo world. It should return only the information that a specific demo character is allowed to see, while preserving the full observer API from TASK-005.

## Goal

Implement a read-only agent-scoped demo API for Gray Harbor, and update the frontend character first-person panel to fetch a selected character's perspective from that API instead of deriving the selected character view from the all-agent observer payload.

Target boundary:

```text
Backend fixed demo read model
  -> observer API: full dashboard payload
  -> agent-scoped API: one character's local perspective only
  -> frontend query per selected character
  -> first-person Observation / Belief UI
```

This task is still not a real simulation task. It is a read-model boundary task.

## Dependencies

- TASK-001
- TASK-002
- TASK-003
- TASK-004
- TASK-005
- ADR-001: World State Authority
- ADR-002: Information Isolation
- ADR-003: Action Lifecycle
- ADR-004: Module Boundaries
- `docs/architecture-handbook.md`
- `docs/development-handbook.md`
- `docs/domain-contracts.md`

## Allowed Changes

Backend:

- `backend/app/api/routes/**`
- `backend/app/api/**`
- `backend/app/services/demo_world.py`
- `backend/app/services/**` only for narrow demo read-model helpers
- `backend/tests/**`

Frontend:

- `frontend/src/features/demo-world/**`
- `frontend/src/lib/api-client.ts` only if a small error/loading improvement is necessary
- `frontend/src/types/api.ts`
- `frontend/src/app/page.tsx` only if wiring requires it
- `frontend/src/test/**`

Docs/tasks:

- `tasks/TASK-006-agent-scoped-demo-read-api.md`
- `tasks/TASK_STATUS.md`
- `docs/current-status.md`
- `docs/known-issues.md`
- `docs/domain-contracts.md` if the new read model shape needs explanation

## Forbidden Changes

- Do not add database business tables.
- Do not add Alembic migrations.
- Do not implement Repository.
- Do not implement World Engine.
- Do not implement Observation Builder.
- Do not implement Action Validator.
- Do not implement Model Gateway.
- Do not call or configure an LLM.
- Do not add Temporal, Celery, cron, queues, or scheduling.
- Do not implement real Oracle reply submission.
- Do not implement real world time advancement.
- Do not let the frontend infer hidden facts for agent-facing data.
- Do not make the agent-scoped response include other agents' observations, other agents' beliefs, secret objective events, or full observer-only timelines.
- Do not treat `OracleResponse` as a command.
- Do not modify generated schema/type files unless a later task explicitly requires the TASK-002 generation flow.
- Do not introduce a new large frontend state manager or API framework.
- Do not add MSW or another test server library unless the task research proves the current fetch mock approach is insufficient.

## Existing Interfaces

Backend:

- FastAPI app and route registration are already present.
- `GET /demo/worlds/gray-harbor` returns the full observer demo read model.
- `backend/app/services/demo_world.py` contains the fixed Gray Harbor fixture/read model.
- Domain contracts already include `World`, `Character`, `AgentProfile`, `WorldEvent`, `Observation`, `AgentBelief`, `OracleRequest`, `OracleResponse`, `ActionIntent`, and `ActionResult`.

Frontend:

- `apiGet` exists in `frontend/src/lib/api-client.ts`.
- TanStack Query provider exists.
- `DemoWorldObserver` already renders the fixed observer UI from the TASK-005 API.
- TASK-004 fixture data may remain available for tests.

## Suggested API

Add one endpoint:

```text
GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective
```

Suggested response shape:

```ts
{
  world: Pick<World, "id" | "name" | "current_time" | "schema_version" | "version">;
  character: Character;
  agentProfile: AgentProfile;
  observations: Observation[];
  beliefs: AgentBelief[];
  oracleRequests: OracleRequest[];
  oracleResponses: OracleResponse[];
  actionIntents: ActionIntent[];
  actionResults: ActionResult[];
}
```

If the exact `Pick<World, ...>` shape is awkward in Pydantic, use either:

- a narrow HTTP read model with explicit world summary fields; or
- the existing `World` contract if keeping the implementation smaller is more valuable.

The important rule is that this response must not include all world events, all characters, other agents' observations, or other agents' beliefs.

For an unknown `agent_id`, return 404 using the existing API error style.

## Implementation Requirements

- Add a backend read model for one demo agent perspective.
- Add a service function, for example:

```python
get_gray_harbor_agent_perspective(agent_id: str) -> DemoAgentPerspectiveReadModel
```

- Reuse the fixed TASK-005 data source rather than duplicating the fixture in multiple places.
- Keep route code thin: parse HTTP path parameter, call the service, map not found to HTTP 404.
- Keep the full observer endpoint unchanged.
- In the frontend, keep the observer dashboard layout.
- The selected character's first-person panel should fetch agent-scoped data for the selected character.
- The objective world event timeline may continue to use the full observer API, because it belongs to the observer dashboard.
- The first-person panel must render `observations` and `beliefs` from the agent-scoped API, not by filtering all observations/beliefs from the observer payload.
- Add loading and error states for the selected character perspective panel.
- Preserve the explanation that OracleResponse is advice/information, not a command.
- Do not redesign the UI beyond what is needed to show agent-perspective query states.

## Information Isolation Requirements

The agent-scoped API must obey these fixed-demo isolation rules:

- Lin Zhixia perspective includes Lin's character, profile, observations, beliefs, and only Oracle/action records addressed to Lin if any exist.
- Zhou Qiming perspective includes Zhou's character, profile, observations, beliefs, and only Oracle/action records addressed to Zhou if any exist.
- Chen Mo perspective includes Chen's character, profile, observations, beliefs, Chen's OracleRequest/OracleResponse, and Chen's ActionIntent/ActionResult.
- No perspective response includes another character's `Observation`.
- No perspective response includes another character's `AgentBelief`.
- No perspective response includes the full objective event timeline.
- No perspective response includes secret events merely because the observer API has them.

## Test Requirements

Backend must add or update tests and run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

At minimum cover:

- agent perspective endpoint returns 200 for each of the three special characters;
- response contains `world`, `character`, `agentProfile`, `observations`, `beliefs`, `oracleRequests`, `oracleResponses`, `actionIntents`, and `actionResults`;
- Chen Mo response includes Chen's Oracle request/response and action lifecycle records;
- Lin Zhixia response does not include Chen Mo observations, Chen Mo beliefs, Chen Oracle records, or Chen action records;
- unknown `agent_id` returns 404;
- observer endpoint from TASK-005 still returns 200 and full dashboard payload;
- endpoint does not require database state.

Frontend must run:

```powershell
cd frontend
npm run typecheck
npm run test
npm run build
npm run lint
npm run format:check
```

Frontend tests must cover:

- selected character perspective loading state;
- selected character perspective success state;
- selected character perspective error state;
- switching character triggers/uses the corresponding agent-scoped data;
- first-person Observation / Belief panel does not render data from another character's mocked perspective;
- Chen Mo's Oracle request remains visible from Chen's perspective;
- observer objective timeline still renders from the full observer API.

## Acceptance Criteria

- Backend exposes a read-only agent-scoped demo perspective API.
- Full observer API from TASK-005 continues to work.
- Frontend first-person panel uses the agent-scoped API for selected character data.
- Frontend no longer derives selected character Observation/Belief by filtering all agents' private data from the observer payload.
- Information isolation is verified by backend and frontend tests.
- No new database business models or migrations are added.
- No real simulation, LLM, scheduler, Repository, World Engine, Observation Builder, or Action Validator is implemented.
- All required backend and frontend checks pass.
- Documentation records that this is still fixed fixture data and not real agent runtime isolation.

## Documentation Updates

Complete the following:

- `tasks/TASK_STATUS.md`: mark TASK-006 as Done.
- `docs/current-status.md`: add that agent-scoped fixed demo read API is complete.
- `docs/known-issues.md`: record that isolation is fixture-level/API-level only; no real Observation Builder, memory permissioning, or runtime prompt isolation exists.
- `docs/domain-contracts.md`: update only if a new HTTP read model needs explanation.
- `tasks/TASK-006-agent-scoped-demo-read-api.md`: add implementation notes and final verification results.

## Research Requirement

Limited engineering research is required, but no broad open-source library search is required.

Research goal:

- Confirm the simplest FastAPI pattern for path-parameter 404 mapping with response models.
- Confirm TanStack Query dependent/query-key pattern for selected entity fetches.
- Confirm current Vitest fetch mock approach remains sufficient for multiple endpoints.

Scope:

- Review 2 to 3 official docs or mature examples.
- Prefer official FastAPI docs, TanStack Query docs, and Vitest docs.
- Do not introduce new libraries unless there is a clear test-maintenance benefit.
- Specifically, do not add MSW by default. Current direct fetch mocks are likely sufficient.

Deliverable:

- Add a `Research Notes` section to this task file before implementation summary.
- End the notes with the concrete TASK-006 decision, including whether any library was adopted.

Expected decision:

- No new open-source library should be needed.
- Use existing FastAPI, Pydantic, TanStack Query, Vitest, and `apiGet`.

## Research Notes

- FastAPI official error handling docs confirm the existing route pattern can map an unknown path-parameter resource to a 404 by raising an HTTP-layer exception; TASK-006 kept the local unified `ApiError` style so the response body remains consistent with the app. Source: https://fastapi.tiangolo.com/tutorial/handling-errors/
- TanStack Query docs confirm selected-entity requests should be keyed by every variable used by the query function, and dependent queries can be controlled with `enabled`. TASK-006 uses a query key containing the selected `agent_id`. Sources: https://tanstack.com/query/latest/docs/framework/react/guides/query-keys and https://tanstack.com/query/latest/docs/framework/react/guides/dependent-queries
- Vitest docs confirm `vi.stubGlobal` / direct global mocks are appropriate for replacing browser globals such as `fetch` in tests. TASK-006 kept the existing direct fetch mock approach and extended it to branch by URL. Source: https://vitest.dev/api/vi.html#vi-stubglobal

TASK-006 decision: no new library was adopted. The implementation uses existing FastAPI, Pydantic, TanStack Query, Vitest, and `apiGet`.

## Implementation Notes

- Added `DemoAgentPerspectiveReadModel` and `DemoWorldSummaryReadModel` in `backend/app/services/demo_world.py`.
- Added `get_gray_harbor_agent_perspective(agent_id)` to reuse the TASK-005 fixture and filter one agent's allowed local records.
- Added `GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective`, returning 404 with the existing unified API error style for unknown agents.
- Kept `GET /demo/worlds/gray-harbor` unchanged as the full observer dashboard payload.
- Added backend tests for all three special agents, Chen Mo Oracle/action records, Lin Zhixia isolation from Chen Mo private records, unknown agent 404, observer endpoint continuity, and database-free behavior.
- Added `DemoAgentPerspectiveResponse` on the frontend.
- Updated the observer UI so objective world timeline and character selector still use the observer API, while selected first-person Observation, Belief, Oracle, and action lifecycle panels use the agent-scoped query.
- Added frontend tests for selected perspective loading, success, error, switching, isolation from another mocked perspective, Chen Mo Oracle visibility, and objective timeline continuity.

## Final Verification

- `cd backend; .\.venv\Scripts\python.exe -m pytest` passed: 58 passed, 3 skipped.
- `cd frontend; npm run typecheck` passed.
- `cd frontend; npm run test` passed: 16 passed.
- `cd frontend; npm run build` passed.
- `cd frontend; npm run lint` passed with the existing Next.js deprecation notice for `next lint`.
- `cd frontend; npm run format:check` passed.

Notes:

- The first backend pytest attempt failed inside the restricted sandbox while creating pytest temp/cache files; the same command passed after running with approval.
- One parallel frontend verification attempt made `typecheck` race with `next build` over `.next/types`; rerunning `typecheck` after build passed.

## Final Summary Format

The final agent response must include:

- what was completed;
- backend API(s) added;
- frontend query/data-flow changes;
- information isolation guarantees added;
- files changed;
- checks run;
- any failures or skipped checks;
- remaining limitations;
- recommended TASK-007.
