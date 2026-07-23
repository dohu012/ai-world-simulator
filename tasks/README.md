# Task System

Tasks are the unit of work for AI collaboration. A task must be small enough for one Agent to understand, implement, verify, and summarize from repository context alone.

## Naming

Use `TASK-NNN-short-name.md`, for example `TASK-004-first-world-event.md`.

## Lifecycle

- `Planned`: approved idea, not started.
- `In Progress`: currently being worked.
- `Blocked`: cannot proceed without human decision or external change.
- `Review`: implementation done, awaiting review.
- `Done`: accepted and documented.

## Dependencies

Each task lists prior tasks or ADRs it depends on. Do not start a task if a required predecessor is not `Done` unless the task explicitly allows it.

## Scope

Each task must name allowed files/modules and forbidden files/modules. Cross-task changes are prohibited unless required to fix a blocking architecture violation, and that must be documented.

## Status

Update `tasks/TASK_STATUS.md` at the end of every task.
