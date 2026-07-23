# ADR-006: Model Gateway

## Problem

Model-provider calls require shared retries, timeouts, logging, parsing, and provider neutrality, but must not become authority.

## Decision

Model Gateway is the only module that calls LLM providers. It returns structured output but cannot mutate world state, validate authority, or write persistence.

## Reasons

- Provider changes remain isolated.
- Model failure behavior is explicit.
- Prompt text cannot replace code rules.

## Impact

Prompt builders and Gateway interfaces must be tested separately from world mutation.

## Forbidden Actions

- LLM SDK imports outside Model Gateway.
- Prompt text deciding authorization.
- Gateway writing database rows.
- Gateway producing `ActionResult` directly.

## Future Changes

Adding a provider requires tests for request mapping, response parsing, timeout handling, and failure behavior.
