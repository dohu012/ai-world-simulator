# TASK-004: Fixed World Observer Frontend Slice

Status: Done

## Summary

TASK-004 implements a read-only frontend slice for the fixed world demo "灰港封锁区". It uses static fixture data and existing generated domain types to show:

- objective world events;
- three special agents;
- one selected agent's first-person Observation;
- the selected agent's subjective Belief;
- one player revelation request and response;
- one ActionIntent and one adjudicated ActionResult.

This task does not implement real backend business APIs, world simulation, observation generation, action validation, LLM calls, map rendering, avatars, 2D/3D scenes, or image generation.

## Research Notes

Limited research was completed before implementation. The goal was to borrow expression patterns, not frameworks.

### 1. Stanford Generative Agents / Smallville

Reference: https://github.com/joonspk-research/generative_agents

Pros:

- Uses a replayable day-in-the-life simulation to make agent behavior legible over time.
- Separates an agent's memory stream, reflection, planning, and action enough that observers can reason about why a behavior happened.
- Demonstrates that "what happened" and "what an agent remembers or infers" need different presentation layers.

Not suitable here:

- The visible experience is centered on a spatial town and character movement, while TASK-004 must not build maps, avatars, 2D scenes, or 3D scenes.
- The original demo tends to make a full simulated environment feel inspectable, while this project must protect information isolation and avoid giving agents a global state view.
- It is too broad as an implementation model for a static frontend slice.

TASK-004 takeaway:

- Use replay/debug style labels to keep objective events, local observations, and subjective beliefs visually separate instead of presenting all narrative text as one stream.

### 2. AI Town

Reference: https://github.com/a16z-infra/ai-town

Pros:

- Makes multi-agent activity approachable by showing who is present, what they are doing, and how conversations unfold.
- Has a clear public demo orientation and a fixed-ish simulated setting that helps users quickly understand the world.
- Shows the value of a shared "watching the simulation" surface.

Not suitable here:

- Its primary affordance is a live town scene with characters and chat-like interactions; TASK-004 explicitly avoids map, avatar, scene, and chat-window-as-main-experience designs.
- It is built around a real-time multiplayer/demo stack that would exceed this task's frontend-only static scope.
- It does not emphasize the contractual distinction between Observation, Belief, ActionIntent, and ActionResult as first-class domain objects.

TASK-004 takeaway:

- Keep a compact world overview and a visible list of special agents, but make the role switcher open a subjective dossier rather than a global live scene.

### 3. Langfuse

Reference: https://github.com/langfuse/langfuse

Pros:

- Uses traces, observations, sessions, metadata, and evaluation views to make AI application behavior auditable.
- Encourages drilling from a high-level execution trace into individual observations and outputs.
- Treats debugging artifacts as inspectable records instead of as chat transcript alone.

Not suitable here:

- Langfuse is observability infrastructure for LLM applications, not a simulation product UI.
- Its data model is trace/provider oriented rather than world/agent authority oriented.
- Bringing in a similar observability product model would overfit TASK-004 to tooling rather than product experience.

TASK-004 takeaway:

- Borrow the trace-like "lifecycle panel" pattern: show ActionIntent as an attempted action record and ActionResult as a later adjudication record.

### 4. Jaeger Trace UI

Reference: https://github.com/jaegertracing/jaeger-ui

Pros:

- Presents spans on a timeline while preserving hierarchy, duration, and causal relationships.
- Makes it easy to scan a large amount of execution history without turning everything into prose.
- Supports a clear split between summary rows and detail panes.

Not suitable here:

- Span duration and service topology are not the same as narrative world time and subjective knowledge.
- A literal trace waterfall would make the demo feel like infrastructure debugging rather than an observer console for an AI world.
- It does not cover subjective beliefs or player revelation semantics.

TASK-004 takeaway:

- Use a dense objective timeline with short summary rows, then place agent-local detail panels beside it for subjective reading.

## TASK-004 Design Decisions

1. The first screen is an internal observer console, not a marketing landing page.
2. The objective world timeline is always visible and explicitly labeled as "Objective World".
3. Agent selection changes only the first-person Observation and Belief panels. It does not change objective history and does not infer hidden facts.
4. Observation cards show local sensory/message fragments and include notes such as "不知道北门封锁预案" to make information isolation visible.
5. Belief cards show confidence and source type, and state that a belief is not automatically an objective fact.
6. The player revelation panel uses "建议是信息，不是命令" wording and disables submission because this task has no real Oracle workflow.
7. ActionIntent and ActionResult are rendered as separate lifecycle records, so intent never implies success.
8. The fixture data is static TypeScript using existing generated domain types; UI helper functions only filter or format already-provided records.
