# Development Handbook

Every Coding Agent must read this file, `docs/architecture-handbook.md`, `docs/ai-collaboration-guide.md`, `docs/current-status.md`, `docs/known-issues.md`, and the active task before changing code.

## Directory Rules

- `backend/app/domain`: Pydantic v2 public domain contracts. This is the source of truth for domain schemas.
- `schemas/domain`: generated JSON Schema. Do not edit manually.
- `frontend/src/types/generated`: generated TypeScript declarations. Do not edit manually.
- `frontend/src/types/domain`: frontend public import surface for generated domain types.
- `backend/app/api`: FastAPI routes, request/response mapping, and HTTP errors.
- `backend/app/services` and future `backend/app/application`: use-case orchestration.
- `backend/app/repositories`: persistence interfaces and implementations.
- `backend/app/model_gateway`: provider-neutral model calls.
- `backend/app/infrastructure`: database, Redis, config, logging, process adapters.
- `backend/migrations`: Alembic revisions.
- `frontend/src/app`: Next.js App Router entry points and providers.
- `frontend/src/features`: feature UI.
- `docs`: living documentation.
- `decisions`: ADRs.
- `tasks`: task definitions and status.

## New Module Flow

1. Confirm the active task allows the module.
2. Check `docs/architecture-handbook.md` for ownership and dependencies.
3. Add the smallest module with one responsibility.
4. Add tests at the closest layer.
5. Update docs if boundaries or workflows changed.

## New API Flow

1. Define the domain and application contract first.
2. Add API schemas only at the HTTP boundary.
3. Route into Application; do not implement rules in routes.
4. Add tests for success, validation failure, and error mapping.
5. Update frontend API client and types only after the backend contract is stable.

## New Domain Schema Flow

1. Modify Pydantic models in `backend/app/domain`.
2. Run `python -m app.domain.export_schemas` from `backend`.
3. Run `npm run generate:domain-types` from `frontend`.
4. Run `npm run typecheck`.
5. Commit Python models, JSON Schema, generated TS declarations, fixtures, and tests together.
6. Never manually edit generated schema or generated TS files.

## Database Migration Flow

1. Change persistence models or SQL metadata.
2. Generate an Alembic revision with a descriptive message.
3. Inspect generated SQL manually.
4. Verify upgrade and downgrade where feasible.
5. Run `python -m alembic check` when model metadata exists.
6. Never mix unrelated schema changes in one migration.

## Test Flow

Backend:

```powershell
cd backend
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m app.domain.export_schemas
```

Frontend:

```powershell
cd frontend
npm run generate:domain-types
npm run typecheck
npm run lint
npm run format:check
npm run test
npm run build
```

Add unit tests for pure rules, contract tests for schema boundaries, integration tests for repositories and use cases, API tests for HTTP behavior, and frontend tests for user-visible states.

## ADR Flow

Create or update an ADR when changing architecture authority, dependency direction, information isolation, action lifecycle, persistence strategy, concurrency behavior, model-provider policy, public contract source, or long-term development rules.

ADR files use `decisions/ADR-NNN-short-name.md` and must include problem, decision, reasons, impact, forbidden actions, and future change rules.

## Commit Rules

- Keep commits single-purpose.
- Prefer Conventional Commits, for example `docs: add architecture handbook`.
- Commit lock files only when dependencies intentionally changed.
- Do not commit secrets, virtual environments, build output, or caches.

## Review Flow

Reviews must prioritize correctness, boundary violations, missing tests, migration safety, schema compatibility, API compatibility, data leakage, and concurrency risk. Style-only findings are secondary.

## Code Style

- Backend uses Python 3.12+, Pydantic v2, SQLAlchemy 2, Ruff, and mypy.
- Frontend uses TypeScript strict mode, React, Next.js App Router, Tailwind CSS, TanStack Query, ESLint, Prettier, and Vitest.
- Prefer explicit domain models over untyped dictionaries.
- Do not add abstractions until repeated real use cases prove the shape.

## Refactoring Rules

Refactoring is allowed only when required by the active task, needed to fix an architecture violation, or tightly local to touched code. Large cross-module cleanup requires a separate task.

## When To Create A New Task

Create a new task when work crosses multiple major systems, needs database plus frontend plus engine changes, changes public contracts outside the stated goal, introduces a new module owner, or cannot be completed and verified in one coding context.

## When To Update Architecture Handbook

Update `docs/architecture-handbook.md` when changing authority, ownership, dependency rules, lifecycle, information isolation, LLM authority, repository rules, scheduler behavior, or concurrency assumptions.
