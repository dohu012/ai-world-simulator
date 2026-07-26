# TASK-005: Fixed World Demo Read API

Status: Done

## Summary

TASK-005 moves the Gray Harbor fixed observer demo behind a read-only backend API and makes the frontend observer query that API by default.

Implemented boundary:

```text
backend fixed demo read model
  -> GET /demo/worlds/gray-harbor
  -> frontend apiGet + TanStack Query
  -> DemoWorldObserver UI
```

This remains a fixed fixture demo. It does not introduce database business tables, repositories, migrations, World Engine, Observation Builder, Action Validator, Model Gateway, LLM calls, or scheduling.

## Backend

- Added `backend/app/services/demo_world.py`.
- Added `DemoWorldReadModel` as an HTTP read model composed from existing domain contracts.
- Added `get_gray_harbor_demo_world()` as a service-layer fixed fixture.
- Added `backend/app/api/routes/demo_world.py`.
- Registered `GET /demo/worlds/gray-harbor` in the FastAPI app.
- Added backend API tests for the response shape, minimum data counts, and independence from database state.

## Frontend

- Added `DemoWorldResponse` in `frontend/src/types/api.ts`.
- Updated `DemoWorldObserver` to use TanStack Query and `apiGet("/demo/worlds/gray-harbor")`.
- Kept the TASK-004 observer UI structure: objective events, special agent panels, first-person observations, subjective beliefs, player revelation, ActionIntent, and ActionResult remain separated.
- Added loading, error, and success rendering.
- Kept TASK-004 fixture data for tests only.

## Research Notes

1. FastAPI official "Bigger Applications" docs
   - Borrowed pattern: keep route registration in a small `APIRouter` module and include it from the app entry point.
   - Fit for TASK-005: yes. The endpoint is a new feature route and does not need a new app structure.
   - Decision: adopted `backend/app/api/routes/demo_world.py` with `APIRouter(prefix="/demo/worlds")`.
   - Reference: https://fastapi.tiangolo.com/tutorial/bigger-applications/

2. FastAPI official response model docs
   - Borrowed pattern: declare an explicit `response_model` so FastAPI validates and serializes outbound data.
   - Fit for TASK-005: yes. The API returns a composed observer payload, not a database entity.
   - Decision: adopted `response_model=DemoWorldReadModel` and composed it from existing domain contracts.
   - Reference: https://fastapi.tiangolo.com/tutorial/response-model/

3. TanStack Query official testing guidance
   - Borrowed pattern: tests create an isolated `QueryClientProvider` with retries disabled.
   - Fit for TASK-005: yes. The observer uses a single query and should not depend on app-global query cache in tests.
   - Decision: adopted per-test `QueryClient` wrappers and no new state-management framework.
   - Reference: https://tanstack.com/query/latest/docs/framework/react/guides/testing

4. Vitest official mocking guidance
   - Borrowed pattern: mock global APIs with Vitest mocks and restore between tests.
   - Fit for TASK-005: yes. The demo only needs fetch success/error/loading states.
   - Decision: adopted direct `fetch` mocks instead of MSW because route-level behavior is small and adding MSW would be extra dependency surface.
   - Reference: https://vitest.dev/guide/mocking/globals

Final TASK-005 implementation decision: use existing FastAPI, Pydantic, TanStack Query, Vitest, and `apiGet`; place the fixed fixture in a backend service; keep the route as HTTP mapping only; expose one whole-page observer read model; keep frontend fixture data only for tests; do not change generated domain schemas or introduce persistence/simulation modules.

## Verification

- `backend/.venv/Scripts/python.exe -m pytest`: 53 passed, 3 skipped.
- `frontend npm run typecheck`: passed.
- `frontend npm run test`: 11 passed.

Additional required frontend checks were run after implementation and are recorded in the final agent summary.

## Remaining Limits

- The API returns a fixed service-layer fixture.
- No real world persistence is connected.
- No real Observation Builder, Action Validator, World Engine, Oracle workflow, Model Gateway, LLM call, or scheduler exists.
- OracleResponse remains advice/information, not a command.
