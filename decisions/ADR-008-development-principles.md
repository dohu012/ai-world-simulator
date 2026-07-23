# ADR-008: Development Principles

## Problem

Many independent AI Coding Agents will contribute without shared chat context. Unwritten norms will not survive.

## Decision

Development is documentation-driven and task-scoped. Agents must read the handbooks and active task first, keep changes narrow, update repository status, and record architecture decisions in ADRs.

## Reasons

- Reduces dependence on chat history.
- Makes work reviewable after context loss.
- Preserves architecture constraints.

## Impact

Every task must include allowed changes, forbidden changes, tests, documentation updates, and final summary requirements.

## Forbidden Actions

- Drive-by refactoring.
- Changing public contracts without task scope.
- Leaving status only in chat.
- Implementing business behavior during documentation-only tasks.

## Future Changes

Process changes should update this ADR, `docs/development-handbook.md`, and `docs/ai-collaboration-guide.md`.
