# TASK-013: Deterministic Observation Builder and Visibility Propagation

## Goal

Make Observation Builder the unique construction boundary for event and Oracle
information delivered to agents, and persist its isolated output before agent-facing
reads consume it.

## Rules

- Public events reach every seeded special agent.
- Secret and private events reach only explicit participants.
- Restricted events reach participants plus explicitly configured indirect recipients.
- Indirect recipients receive an auditory projection, not objective world snapshots.
- Oracle responses become agent-owned `oracle` Observations and remain advice.
- Output ordering and IDs are deterministic; repeated seed execution is idempotent.
- Unknown configured recipients are ignored rather than creating invalid records.

These are deliberately small Gray Harbor rules, not a general spatial, sensory,
organization, message-propagation, or world-state engine.

## Implementation

- Added pure `ObservationBuilder` application service.
- Gray Harbor seed now builds and persists event and Oracle Observations through it.
- Removed TASK-012's temporary read-time Oracle projection.
- Agent input continues to read only persisted, owner-filtered Observation records.
- No schema migration or external dependency was required.

## Evidence

- Public, restricted, secret, and private visibility unit tests.
- Indirect auditory delivery test.
- Oracle request/response ownership validation and advice-only metadata test.
- Deterministic input-order test.
- Infrastructure test proves nine seeded Observations remain nine after repeated seed.
- Lin receives no Chen Oracle Observation; Chen receives the persisted Oracle record.
- Existing observer, replay, current-agent, health, and frontend tests remain green.

## Forbidden/Deferred

- No World Engine, Action Validator, LLM, prompt assembly, memory, scheduler, or wake loop.
- No geometry, line-of-sight, distance, organization membership, or general channel graph.
- No mutation API or runtime event publication workflow.

## Acceptance

> Gray Harbor agent input now consists only of deterministic, persisted Observations
> constructed by the application-owned visibility boundary.

## Status

Done.
