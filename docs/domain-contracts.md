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
