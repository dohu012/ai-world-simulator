# TASK-009: Demo Agent Input Feed

## Goal

Add a fixed demo current-agent input feed that models the data shape a future agent runtime should consume:

```http
GET /demo/worlds/gray-harbor/me/input
X-Demo-Agent-Id: char-chen-mo
```

Unlike `/me/perspective`, this endpoint returns only the current character, profile, world summary, and allowed `Observation` records. Chen Mo's player Oracle advice is represented as an `Observation` with `observation_type: "oracle"` instead of exposing raw `OracleResponse` or action lifecycle records as agent input.

## Scope

- Reuse the TASK-007 fixed demo caller identity header.
- Keep `/me/perspective` and the observer dashboard unchanged.
- Add a demo-only read model for current-agent input.
- Convert the fixed Chen Oracle response into a fixed demo Observation projection.
- Do not implement a real Observation Builder.
- Do not run an agent, LLM, World Engine, Scheduler, Memory, Action Validator, or Oracle workflow.

## Implementation Notes

- Added `DemoAgentInputReadModel`.
- Added `get_gray_harbor_agent_input(agent_id)`.
- Added `GET /demo/worlds/gray-harbor/me/input`.
- The endpoint returns `world`, `character`, `agentProfile`, and `observations` only.
- The Chen Oracle response is represented as `obs-oracle-response-chen-north-gate` with `observation_type: "oracle"`.
- Added frontend `DemoAgentInputResponse` and `getGrayHarborCurrentAgentInput()`.

## Verification

- Backend tests cover Chen input feed, Lin isolation from Chen Oracle input, missing header, and unknown header.
- Frontend tests cover input helper URL/header usage and error propagation.

## Status

Done.
