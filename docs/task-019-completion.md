# TASK-019 Completion

TASK-019 completed on 2026-07-28 with scenario `gray-harbor-seven-day` version
1.0.0. ADR-012 selected the existing PostgreSQL runtime, typed policies,
normalized balances plus append-only ledgers, SHA-256 adjudication, deterministic
schedule templates, and pytest/replay evaluation. No production dependency or
paid model service was added.

## Scenario and authority

- Exactly 30 persisted residents: 3 L3, 9 L2, 12 L1, and 6 L0.
- Four schedule templates execute ordinary resident demand with zero model calls.
- Existing runtime start/pause/resume/advance is the only time-advance authority.
- Nine automatic server-offered actions cover consume, transfer, queue, acquire
  rejection, help, route, abandon plan, plan completion, and rescue allocation.
- Every action traverses ActionIntent, Validator, World Engine, ActionResult,
  WorldEvent, Observation, and replay. Actor/type mismatches and hidden targets
  reject before mutation.

## Seven-day result

Day 1 consumes one clinic medicine dose. Day 2 transfers four store rations. Day 3
registers the checkpoint. Day 4 rejects the hidden-cache attempt with
`ACTION_TARGET_NOT_ALLOWED`. Day 5 transfers two more rations and fires the
shipment-stop condition exactly once. Day 6 completes Lin and Zhou's plans and
abandons Chen's blocked plan. Day 7 irreversibly allocates all ten rescue seats.

Final authoritative values:

- store food: 84; transferred household food: 6; conservation total: 90;
- clinic medicine: available 7, consumed 1;
- rescue seats: available 0, consumed 10;
- Lin plan `completed`, Zhou plan `completed`, Chen plan `abandoned`;
- deterministic acceptance model cost: US$0; ordinary resident model calls: 0.

## Recovery and concurrency evidence

Reset persists a monotonic generation derived from both the checkpoint and
historical action audit, so migration/restart cannot reuse an old causal chain.
The full seven days resume after reconstructing the runtime service on Day 4.
Running the scenario twice produces independent generations while same-generation
keys return the first result. Two concurrent database sessions racing for the
final rescue capacity yield one success and one stable
`RESOURCE_INSUFFICIENT` rejection with no over-allocation.

## Gates

- backend with infrastructure/workflow flags: 182 passed;
- frontend: 34 passed;
- Ruff, mypy, schema export, TypeScript, ESLint, Prettier, and production build;
- Alembic downgrade to `20260727_0007`, upgrade through `0008`/`0009`, and drift
  check on PostgreSQL.

The remaining product decision for TASK-020 must be based on playtest evidence,
not preselected by TASK-019 implementation.
