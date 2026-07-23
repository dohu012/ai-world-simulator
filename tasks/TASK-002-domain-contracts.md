# TASK-002: Domain Contracts

## Background

After the foundation, the project needed public domain contracts before implementing business behavior.

## Implemented

- Pydantic v2 domain models for World, Character, AgentProfile, WorldFact, AgentBelief, Observation, ActionIntent, ActionResult, WorldEvent, OracleRequest, and OracleResponse.
- Strict validation and forbidden unknown fields.
- JSON Schema export to `schemas/domain`.
- TypeScript generation to `frontend/src/types/generated`.
- Frontend domain type entry point in `frontend/src/types/domain`.
- Fixtures and contract tests.

## Design Reason

Python domain models are the single source of truth. Generated JSON Schema and TypeScript declarations keep backend and frontend aligned without duplicating contract definitions.

## Left Open

- Persistence models and migrations for domain entities.
- Observation Builder, Action Validator, World Engine, Repository, Model Gateway, Memory, Scheduler, and business APIs.
