# TASK-003: Development Handbook And AI Collaboration Rules

## Background

TASK-001 and TASK-002 created the foundation and public contracts, but future independent AI Coding Agents need durable development rules.

## Goal

Create the development infrastructure: architecture handbook, development handbook, AI collaboration guide, ADRs, and task system.

## Dependencies

- TASK-001
- TASK-002

## Allowed Changes

- `docs/`
- `decisions/`
- `tasks/`

## Forbidden Changes

- Business features.
- Database tables or migrations.
- API routes.
- Repositories.
- World Engine.
- Observation Builder.
- Action Validator.
- Prompts.
- Model calls.
- Domain Schema changes.
- TASK-001/TASK-002 public contract rewrites.

## Implemented

- `docs/architecture-handbook.md`
- `docs/development-handbook.md`
- `docs/ai-collaboration-guide.md`
- Eight ADRs for authority, information isolation, lifecycle, boundaries, repository rules, model gateway, concurrency, and development principles.
- Task system README, template, status, and TASK-001 through TASK-003 records.

## Acceptance

A new Agent can begin future work by reading the handbooks, current status, known issues, task status, and active task.
