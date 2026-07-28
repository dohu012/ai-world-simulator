# TASK-018 Completion Report

Completed: 2026-07-27

TASK-018 adds a deterministic causal social-world slice without new production
dependencies or services. ADR-011 records the graph, transport, belief, dialogue,
and observability research. PostgreSQL remains authority; the existing virtual
clock now triggers due social transmissions.

## Fixed timeline

| Recipient | Channel | Delay | Reliability | Claim |
| --- | --- | ---: | ---: | --- |
| Lin Zhixia | direct official | 0 min | 0.98 | north gate closes at 12:00 |
| Zhou Qiming | official bulletin | 10 min | 0.94 | north gate closes at 12:00 |
| Chen Mo | distorted courier | 20 min | 0.52 | all gates may close at 11:30 |

The intermediate projections are owner-scoped. No hidden `WorldFact` identifier is
placed in a message Observation. Evidence and revisions are append-only. A repeated
causal source neither increases confidence nor counts as independent corroboration.
Conflicting evidence remains conflicted unless a higher-reliability claim carries
the explicit corrected stance.

## Dialogue and authority

The fixed Chen→Zhou→Chen correction exchange uses the private direct channel with a
five-minute delay per transmission. It is a persisted finite-state conversation
with two fixed participants, maximum three delivered turns, 1,200 tokens, and a
30-world-minute deadline. Sending is separate from delivery. Delivery uses
Observation Builder and the same PostgreSQL `SKIP LOCKED` claim boundary. The
acceptance fixture completes after two turns with `correction_delivered`; failures
and timeout never create fake speech.

## Persistence and APIs

Migration `20260727_0007` adds normalized channels, messages, transmissions,
belief evidence, belief revisions, and conversations. Unique delivery, evidence,
revision, Observation, and Wake keys fence retries.

Observer APIs:

- `GET /demo/worlds/gray-harbor/propagation`
- `GET /demo/worlds/gray-harbor/beliefs/history`
- `GET /demo/worlds/gray-harbor/conversations`

Owner-derived APIs:

- `GET /demo/worlds/gray-harbor/me/messages`
- `GET /demo/worlds/gray-harbor/me/beliefs/history`

The observer UI distinguishes sent, delivered, believed, and objectively true,
and renders propagation branches, belief evolution, and bounded conversation
state. Agent-local reads filter by the existing server-derived demo identity.

## Deterministic evidence

- Pure policy tests: 5 passed.
- Real PostgreSQL social smoke: exact counts `(5 delivered, 5 Observations,
  5 evidence rows)`, two-worker delivery, service recreation, three different
  intermediate beliefs, correction and explicit termination.
- Paid model calls: 0; recorded token/cost: 0/US$0.
- No sleeps, randomized timing, broker, recursive Agent call, or global prompt
  context.

## Limits and next recommendation

This remains one fixed proposition and a deterministic two-Agent correction
fixture. It does not provide general organization routing, free-form recipient
selection, population simulation, semantic memory, or live push delivery.

TASK-019 should evaluate richer authoritative actions. The completed social loop
can now form coherent different beliefs and exchange a correction, while the
available physical action vocabulary remains predominantly wait/move/message.
