# 已知限制

- 健康就绪检查依赖本地 PostgreSQL 和 Redis；服务未启动时按设计返回 503。
- Compose 配置面向本地开发，不包含生产部署、备份、TLS 或高可用方案。
- 当前只有验证迁移能力的 `system_metadata` 基础表，不是最终领域模型。
- TASK-004 的灰港封锁区 demo 是静态前端 fixture，不代表真实模拟、真实数据持久化或真实 API 已实现。
- TASK-004 尚未实现真实 Observation Builder、Action Validator、World Engine、Oracle workflow、Repository、Model Gateway、Memory 或 Scheduler。
- 世界时间暂用带时区的公历 datetime，尚未实现自定义世界历法。
- 尚未定义 `ScheduledEvent` 独立契约；当前 EventType 值不代表未来事件调度能力。
- `schema_version` 已固定为 `1.0`，但尚无契约迁移或历史版本加载工具。
- TypeScript 是 JSON Schema 的静态生成结果；数值范围、日期格式等运行时约束仍由后端 Pydantic 校验，前端若接收不可信数据，后续仍需增加运行时验证。
- 2026-07-23 的 `npm audit --omit=dev` 对 TASK-001 既有 Next.js 依赖链报告 1 个 moderate 和 2 个 high 告警（PostCSS、sharp）；TASK-004 未升级公共前端技术栈。
## TASK-005 Fixed Demo API Limits

- `GET /demo/worlds/gray-harbor` returns a fixed service-layer fixture. It does not read from business database tables.
- The project still has no real Observation Builder, Action Validator, World Engine, Oracle workflow, Repository, Model Gateway, Memory, or Scheduler.
- OracleResponse remains player-provided information/advice and is not treated as a command.

## TASK-006 Agent-Scoped Demo API Limits

- `GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective` enforces isolation by filtering fixed fixture data at the service/API read-model layer only.
- The project still has no real Observation Builder, memory permissioning, runtime prompt isolation, agent authentication, or player-facing authorization boundary.
- The observer dashboard intentionally continues to receive objective events and all demo records from `GET /demo/worlds/gray-harbor`; that endpoint is not an agent-facing data source.

## TASK-007 Demo Access Boundary Limits

- `GET /demo/worlds/gray-harbor/me/perspective` uses `X-Demo-Agent-Id` as a fixed demo caller identity boundary only.
- This is not production authentication or authorization. It is not login, OAuth, JWT, session, cookie, user management, role-based access control, or real player-agent binding.
- The endpoint demonstrates that future agent/player-facing APIs should derive "me" from server-side caller identity rather than trusting a caller-selected `agent_id` URL parameter.

## TASK-008 Current-Agent Preview Limits

- The `Agent Preview` panel is a frontend test harness for the demo current-agent read path, not a production player or agent client.
- The fixed caller remains `char-chen-mo`; there is still no real logged-in user, player-agent binding, or runtime permission system.
- The panel renders existing fixture read-model records only. It does not submit Oracle advice, advance world time, create actions, or run agent decisions.

## TASK-009 Demo Agent Input Feed Limits

- `GET /demo/worlds/gray-harbor/me/input` is a fixed read-model projection, not a real Observation Builder.
- The Chen Oracle advice Observation is hand-authored from fixture data. No player submission, delivery workflow, memory update, or agent reasoning occurs.
- The endpoint shows the intended agent-input shape, but it is not runtime prompt isolation or production authorization.

## TASK-010 Agent Input Feed Preview Limits

- The `Agent Input Feed` panel is a frontend harness for inspecting TASK-009 data, not a production agent runtime.
- The UI does not submit decisions, invoke an LLM, mutate world state, update memory, or validate actions.
- It depends on the fixed demo caller `char-chen-mo` and the fixed demo fixture projection.

## TASK-011 Persistence Limits

- Replay is an audit/debug projection over explicit event, observation, Oracle, and action records; it is not full event-sourced aggregate reconstruction.
- The fixed seed uses PostgreSQL upserts and requires migrations plus a running database. It does not run automatically at API startup.
- Existing fixture endpoints remain available while clients migrate to the database-backed demo route.

## TASK-012 Database Read Cutover Limits

- Gray Harbor is still fixed seeded demo data; it is not a World Engine or live simulation.
- The API never seeds on startup. Missing seed data returns DEMO_WORLD_NOT_SEEDED, and database readiness remains independently observable.
- /persistent is a temporary compatibility alias for the primary observer route.
- Replay Inspector is an observer/debug audit projection, not event-sourced reconstruction or a replay player.
- Chen's Oracle-derived Observation remains a temporary application-layer projection pending TASK-013.

## TASK-013 Observation Builder Limits

- Visibility propagation is deterministic but fixed to the Gray Harbor slice; it has no geometry, range, line-of-sight, organization membership, or general channel graph.
- Restricted indirect recipients are explicit seed policy, not inferred from a live world topology.
- Observations are generated during explicit seed execution; no runtime event publication or wake loop exists yet.
- Oracle advice is now persisted through Observation Builder, superseding TASK-012's temporary read-time projection.

## TASK-014 Action Lifecycle Limits

- Only parameterless `wait` is accepted; all other action types are auditable rejections.
- Successful wait produces a private event but intentionally changes no resources, location, facts or world time.
- Demo identity headers are not production authentication, and there is no frontend action submission UI.
- The World Engine is a narrow Gray Harbor implementation, not a general action dispatcher or simulation engine.
- Deterministic IDs and primary keys protect retries; distributed per-world locking remains deferred until meaningful concurrent state mutation exists.

## TASK-015 limits (2026-07-26)

- Topology is deliberately fixed and internal: no map editor, coordinates, pathfinding, travel time, or public Location contract.
- The demo retains TASK-014 same-key semantics: a reused key returns the first persisted lifecycle even if the later body differs.
- Live PostgreSQL concurrency and smoke checks require the local infrastructure and `RUN_INFRA_TESTS=1`; unit/static/frontend gates do not substitute for that operational evidence.
- Infrastructure verification attempt on 2026-07-26 could not connect to PostgreSQL `localhost:5432` or Redis `localhost:6379`. `docker compose up -d postgres redis` also failed because Docker Desktop's Linux engine pipe was unavailable. Therefore migration/seed/live move/stale/retry/concurrency smoke IDs are not recorded on this workstation.

### TASK-015 infrastructure status resolved

The earlier local infrastructure blocker is resolved: Docker Desktop, PostgreSQL, and Redis are running healthy; migration `20260726_0003`, idempotent seed, all 9 infrastructure tests, and real accepted/stale/retry smoke scenarios pass. The historical failure note above is retained only as execution history, not a current limitation.

## TASK-016 residual risks

- Claim leases are persisted and non-terminal same-key calls fail closed with `DECISION_IN_PROGRESS`; automatic expired-lease takeover and crash injection coverage remain follow-up hardening.
- OpenAI response mapping is covered by the adapter boundary but no paid live-provider smoke was run; live evaluation remains explicitly opt-in.
- Decision audit is returned by the decision endpoint; the observer Replay Inspector has not yet merged decision rows into its global replay response.
