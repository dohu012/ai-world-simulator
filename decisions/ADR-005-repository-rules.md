# ADR-005: Repository Rules

## Problem

Repositories can become hidden business-rule containers because they touch data.

## Decision

Repositories only persist and retrieve data. They do not implement business rules, authorization, prompt logic, validation, or consequences.

## Reasons

- Persistence remains replaceable.
- Business behavior remains testable without infrastructure.
- Database operations stay auditable.

## Impact

Application, validators, and World Engine must make decisions before calling repositories.

## Forbidden Actions

- Repository methods that decide outcomes.
- Repository calls to Model Gateway.
- Raw SQL in API routes for business features.

## Future Changes

If a repository needs richer query behavior, document whether it is still retrieval or has become domain logic.
