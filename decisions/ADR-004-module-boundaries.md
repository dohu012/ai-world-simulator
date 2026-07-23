# ADR-004: Module Boundaries

## Problem

Independent Agents may add code in convenient places, creating cycles between API, persistence, domain, and model code.

## Decision

The dependency direction is Frontend -> API -> Application -> World Engine -> Repositories -> Infrastructure, with Domain remaining framework-independent.

## Reasons

- Keeps pure contracts testable.
- Limits framework and infrastructure leakage.
- Makes ownership clear.

## Impact

Some boundaries may need DTOs, interfaces, or mapping code instead of direct imports.

## Forbidden Actions

- Domain importing FastAPI, SQLAlchemy, Redis, or LLM SDKs.
- API routes implementing world rules.
- Repositories calling Model Gateway.
- World Engine calling provider SDKs.

## Future Changes

Boundary changes require an ADR before implementation.
