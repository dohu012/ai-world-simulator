# AI Collaboration Guide

This guide defines how independent AI Coding Agents collaborate without relying on chat history.

## Required Reading

Before any code change, read:

1. `docs/architecture-handbook.md`
2. `docs/development-handbook.md`
3. `docs/domain-contracts.md`
4. `docs/current-status.md`
5. `docs/known-issues.md`
6. `tasks/TASK_STATUS.md`
7. The active task file

## Task Size

A task should fit in one coding context. If it touches database, frontend, World Engine, prompt, LLM, scheduler, and multiple contracts at once, split it. Prefer separate tasks for implementation, review, and fixes.

## What One Task Must Complete

- State allowed and forbidden files or modules.
- Preserve public contracts unless the task explicitly allows changing them.
- Add or update tests.
- Update `docs/current-status.md`, `docs/known-issues.md` when relevant, and `tasks/TASK_STATUS.md`.
- Leave repository documentation updated, not only a chat summary.

## When To Split

Split when the work introduces more than one module owner, requires broad migration plus UI changes, changes architecture rules, has unclear acceptance criteria, or cannot be safely verified in the current environment.

## Cross-Task Changes

Do not modify code outside the active task scope for convenience. If an out-of-scope defect blocks progress, document it in `docs/known-issues.md` and create or propose a follow-up task.

## Reading The Repository

Read documentation first, then directory READMEs, then the smallest relevant code path, then tests. Treat `backend/app/domain` as the source for domain contracts and generated schema/type files as outputs.

## Updating Status

At task end:

- `docs/current-status.md`: update completed work and next task when project status changed.
- `docs/known-issues.md`: add unresolved blockers, environment limits, or intentional gaps.
- `tasks/TASK_STATUS.md`: move status to `Done`, `Blocked`, `Review`, or leave `In Progress` only when work remains.

## Final Summary Format

- What changed.
- Files changed.
- Tests/checks run.
- Remaining issues.
- Documentation updated.

## Review Rules

Review as a bug finder first. Check authority boundaries, fact/belief separation, observation leakage, persistence safety, schema compatibility, API compatibility, missing tests, and concurrency assumptions before style.

## Stop And Wait For Human Confirmation

Stop when a task requires secrets, production data, destructive database operations, public contract breaking changes not named in the task, paid services, major architecture change without ADR, or a conflict between task instructions and the Architecture Handbook.

## Prohibited AI Behaviors

- No premature abstraction.
- No large drive-by refactor.
- No changes outside task scope.
- No hidden business rules in prompts.
- No direct database writes from LLM, Agent, API route, or frontend.
- No manual edits to generated schemas or generated TypeScript declarations.
- No replacing repository history or reverting user work unless explicitly requested.
