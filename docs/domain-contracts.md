# 领域公共契约

TASK-002 的 Pydantic 模型是领域契约唯一来源。它们只描述可传输的数据和结构约束，
不负责持久化、世界状态变更、感知过滤、Agent 决策、模型调用或 HTTP 路由。

## 核心边界

`WorldFact` 是世界裁定为真的客观命题，包含有效期、可见级别和来源事件，但不包含任何
Agent 的置信度。`AgentBelief` 是某个 Agent 的主观命题，包含置信度和认知来源，但没有
权威可见级别，也不要求绑定事实 ID。Belief 可以错误、过时或与 Fact 冲突。

`WorldEvent` 表示已经发生的客观事件。`Observation` 是特定 Agent 被允许获得的局部输入；
它可以引用来源事件，但不包含完整事实列表、数据库快照、其他 Agent 记忆或尚未传播的秘密。
同一 Event 可以产生零个、一个或多个不同 Observation。

`ActionIntent` 只表达 Agent 想尝试的行动及其参数，不包含成功标志或状态变化。
`ActionResult` 由后续世界裁定器生成，单独保存状态、失败原因、结构化状态变化和生成事件。

`OracleResponse` 是玩家提供的信息，不是命令。它不选择最终行动、不直接修改世界或 Belief；
后续系统只能先把它转成 Agent 可接收的特殊 Observation，再由 Agent 正常决策。

```text
WorldEvent
    ↓ perception (future service)
Observation
    ↓ agent decision (future service)
ActionIntent
    ↓ world adjudication (future service)
ActionResult
    ↓ event publication (future service)
WorldEvent

WorldFact   → objective world state
AgentBelief → subjective agent cognition
```

这些边界同时由独立模型、`extra="forbid"` 和明确的架构测试保护。ID 与 correlation ID 只建立
关联，不让一个对象嵌入另一个边界对象。

## 契约约定

- 所有公共模型继承 `DomainModel`，启用 Pydantic 严格模式并拒绝未知字段。
- 实体 ID 是不带生成算法要求的字符串；当前示例采用 `world_001` 等可读格式。
- 时间在 Python 中使用 `AwareDatetime`，拒绝无时区 datetime；JSON 使用 ISO 8601 字符串。
- 稳定有限值使用字符串枚举；自然语言描述保持字符串。
- `schema_version` 当前只能是 `"1.0"`。破坏兼容性的变更应发布新版本，不重写旧契约；
  当前不实现迁移器。
- 核心字段必须显式建模。只有 `metadata`、`parameters`、`resources` 等真实扩展点可使用
  `JSONObject`；任意 JSON 值使用递归 `JSONValue`，不使用 `Any`。
- TypeScript 的 `number`/`string` 类型不能表达全部 JSON Schema 运行时约束，数据可信性仍以
  Pydantic 校验为准。

## JSON Schema 与 TypeScript 同步

从仓库根目录执行：

```powershell
cd backend
python -m app.domain.export_schemas

cd ..\frontend
npm run generate:domain-types
npm run typecheck
```

第一条命令将 11 个模型以稳定顺序和格式写入 `schemas/domain/*.schema.json`。第二条命令使用
`json-schema-to-typescript` 生成 `frontend/src/types/generated/*.d.ts`。生成文件不可手工修改；
前端业务代码从 `frontend/src/types/domain/index.ts` 导入。公共 ID/JSON 别名位于
`frontend/src/types/domain/common.ts`，11 个核心模型均来自自动生成结果。

修改 Python 契约后，必须依次重新导出 Schema、重新生成 TypeScript，并运行后端测试与
`npm run typecheck`。生成文件和 Schema 都纳入版本控制，以便代码审查契约差异。
## TASK-005 Demo Read Model

`GET /demo/worlds/gray-harbor` returns an HTTP read model composed from existing domain contracts: `World`, `Character`, `AgentProfile`, `WorldEvent`, `Observation`, `AgentBelief`, `OracleRequest`, `OracleResponse`, `ActionIntent`, and `ActionResult`.

This read model is for the observer UI only. It does not make the frontend an authority over hidden facts, does not merge objective events with subjective observations or beliefs, and does not change the domain contract source of truth.

## TASK-006 Agent Perspective Read Model

`GET /demo/worlds/gray-harbor/agents/{agent_id}/perspective` returns a narrow HTTP read model for one fixed demo character. It contains a world summary (`id`, `name`, `current_time`, `schema_version`, `version`), that character, that character's `AgentProfile`, and only records locally addressed to that agent: `Observation`, `AgentBelief`, `OracleRequest`, `OracleResponse`, `ActionIntent`, and `ActionResult`.

This endpoint does not include the objective event timeline, all characters, all agent profiles, other agents' observations, other agents' beliefs, or secret observer-only events. The model is still composed from existing domain contracts and is still fixed fixture data rather than runtime isolation.

`GET /demo/worlds/gray-harbor/me/perspective` returns the same narrow read model, but chooses the demo character from the `X-Demo-Agent-Id` header. This is a demo-only caller identity boundary and not production authentication.

## TASK-009 Agent Input Read Model

`GET /demo/worlds/gray-harbor/me/input` returns a current-agent input read model selected by `X-Demo-Agent-Id`. It contains only a world summary, the current character, the current `AgentProfile`, and allowed `Observation` records.

This endpoint intentionally excludes `AgentBelief`, raw `OracleRequest`, raw `OracleResponse`, `ActionIntent`, `ActionResult`, objective event timelines, and other agents' records. In the fixed Gray Harbor demo, Chen Mo's Oracle advice is represented as an `Observation` with `observation_type: "oracle"` to show the intended boundary from player-provided information into agent-local input. This is a hand-authored demo projection, not the real Observation Builder.

## TASK-011 Persistence Mapping

Pydantic domain models remain the public contract authority. SQLAlchemy records are infrastructure-only: each stores the complete contract JSON in `payload` and duplicates only stable query, ordering, ownership, source, version, and correlation fields as typed columns. `WorldRepository` is the DB-to-domain mapping boundary; routes do not issue SQL.

## TASK-012 Application Read Models

GrayHarborReadService now owns composition of the existing observer, agent perspective, current-agent input, and replay HTTP read models. Routes depend on this service and contain no SQL or ORM mapping. Agent perspective records remain owner-filtered, while agent input includes only world summary, character, profile, and allowed Observation contracts. The replay read model is observer/debug-only and exposes ordered events plus existing source and correlation links without changing public domain contracts.

## TASK-013 Observation Construction Boundary

`ObservationBuilder` uniquely constructs event-derived and Oracle-derived `Observation` contracts before persistence. It applies deterministic recipient rules and emits only agent-owned partial projections. Repositories continue to map and retrieve records without deciding visibility. Agent input reads the persisted owner-filtered contracts and no longer synthesizes Oracle observations.

## TASK-014 Action Lifecycle Read/Write Model

`POST /demo/worlds/gray-harbor/me/actions` accepts a demo action submission DTO and returns the canonical `ActionIntent`, `ActionResult`, optional `WorldEvent`, and an idempotent replay flag. The public domain contracts are unchanged. Validator owns acceptance rules, the minimal World Engine exclusively creates result/event contracts, Application owns idempotency orchestration, and Repository atomically persists already adjudicated records.
