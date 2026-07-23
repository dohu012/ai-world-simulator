# ADR-002: Information Isolation

## Problem

Agents must act from partial knowledge. If observations expose complete world state, hidden information and subjective belief collapse.

## Decision

Observation Builder uniquely owns `Observation` construction. Observations include only information allowed by visibility rules.

## Reasons

- Preserves separation between `WorldFact` and `AgentBelief`.
- Prevents prompt and API leakage.
- Makes visibility behavior testable.

## Impact

All agent-facing input must pass through Observation Builder. `OracleResponse` must become an allowed Observation before Agent reasoning.

## Forbidden Actions

- Passing raw database rows or complete world snapshots into prompts.
- Letting Agent code query hidden state directly.
- Encoding access control in prompt wording.

## Future Changes

Any visibility change must update this ADR and add visibility tests.
