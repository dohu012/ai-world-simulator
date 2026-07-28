# ADR-011: Causal social runtime without a broker or Agent framework

- Status: Accepted
- Date: 2026-07-27
- Scope: TASK-018

## Decision

Use dependency-free typed adjacency/scenario rules, normalized PostgreSQL rows, an
append-only deterministic evidence ledger, and an explicit persisted conversation
state machine. PostgreSQL remains replay authority. `LISTEN/NOTIFY` may later be a
wake hint, but is not required for correctness. Add no graph, broker, probabilistic
inference, dialogue-framework, evaluation, or telemetry production dependency.

The fixed scenario has four versioned channels: immediate official direct (0 min,
0.98), delayed official bulletin (10 min, 0.94), distorted courier (20 min, 0.52),
and private dialogue direct (5 min, 0.90). Stable due order is world arrival time,
priority, database creation time, then transmission ID. All delivery uses the
existing virtual clock and `FOR UPDATE SKIP LOCKED`.

## Research snapshot

Versions and project state were checked on 2026-07-27 from official documentation
and project repositories.

| Area | Candidates checked | Result |
| --- | --- | --- |
| Routing | typed Python; NetworkX 3.6.1 (BSD-3); python-igraph 1.x (GPL); rustworkx 0.17 (Apache-2); PostgreSQL 18 recursive CTE; pgRouting 4.x (GPL) | Typed rules selected. Three fixed recipients and four edges do not justify dependencies, extension builds, GPL coupling, or spatial SQL. Removal seam is `stable_route_order` plus channel rows. |
| Delivery | normalized PostgreSQL 18; LISTEN/NOTIFY; Redis Streams/PubSub; NATS JetStream; Kafka/Redpanda; Celery/Dramatiq | PostgreSQL selected. Existing runtime already owns virtual time, transaction fencing, replay, and CI. Pub/Sub is not durable truth; brokers add a second recovery plane. |
| Beliefs | deterministic ledger; pgmpy; PyMC; Dempster-Shafer libraries; LLM-only | Ledger selected. It preserves evidence and shared causal source keys, represents conflict, and replays exactly. Probabilistic packages imply false calibration; LLM-only is non-authoritative and nondeterministic. |
| Dialogue | explicit FSM; LangGraph 1.2.9 (MIT, Python ≥3.10); AutoGen; CAMEL; PydanticAI graph | FSM selected. The scenario needs two fixed participants and ≤3 turns; framework recursion/context sharing increases privacy and recovery surface. The seam is `ConversationRecord` plus per-delivery transition. |
| Evaluation | pytest/replay; DeepEval; Promptfoo; Langfuse; Phoenix; OpenTelemetry semconv 1.43 | pytest/replay selected. GenAI conventions remain mobile/partly experimental and raw content capture conflicts with privacy. Observer-safe counters can later map to OTel. |

Primary references:

- https://networkx.org/documentation/stable/release/index.html
- https://www.postgresql.org/docs/18/sql-select.html
- https://www.postgresql.org/docs/18/sql-notify.html
- https://github.com/langchain-ai/langgraph
- https://opentelemetry.io/docs/specs/semconv/

Operational footprint is zero new services and zero new runtime packages. All
selected code supports Python 3.12 and deterministic tests. Removing TASK-018
requires downgrading migration `20260727_0007` and removing the isolated
`communication`, `social_models`, `social_runtime`, and `social_world` modules.

## Executable spikes

`backend/tests/test_social_policies.py` proves deterministic equal-time order,
conflict history, stronger correction, shared-source deduplication, and strict
dialogue budgets. Infrastructure tests exercise PostgreSQL unique delivery keys,
`SKIP LOCKED`, restart-before/after delivery, recipient isolation, and bounded
Chen→Zhou→Chen completion. The same methods are production code; spikes are not
throwaway alternate implementations.

## Authority and privacy

World/runtime code selects recipients, channels, delay, reliability, distortion,
and delivery. Observation Builder is the only message-to-Agent input boundary.
Belief revision changes subjective projections only and never a `WorldFact`.
Message bodies are untrusted content. Agent reads are header-derived and filtered
by recipient/owner. Server-only source keys are stored in evidence/replay but are
not copied into the message Observation.

## Failure semantics

Unique delivery/evidence/revision constraints make replay idempotent. A missing
channel/message becomes `terminal_failed`, never an Observation. A paused runtime
delivers nothing. Conversation timeout, max turns, budget exhaustion, refusal, and
successful correction are explicit terminal reasons. No inference occurs while a
database/world lock is held; the deterministic acceptance fixture uses no paid
model call.
