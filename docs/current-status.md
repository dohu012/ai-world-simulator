# 当前状态

当前阶段：TASK-003 已完成。

已完成内容：

- TASK-001：工程骨架、FastAPI 后端、Next.js 前端、PostgreSQL/Redis 本地基础设施、Alembic、健康检查、测试与基础文档。
- TASK-002：World、Character、AgentProfile、WorldFact、AgentBelief、Observation、ActionIntent、ActionResult、WorldEvent、OracleRequest、OracleResponse 的最小领域契约；JSON Schema 稳定导出；TypeScript 类型生成；示例数据和边界校验测试。
- TASK-003：Architecture Handbook、Development Handbook、AI Collaboration Guide、ADR、Task 系统与长期协作规范。

尚未完成内容：

- 数据库领域模型、Repository、业务 Service、世界裁定、感知过滤、Agent 决策、Oracle 投递流程及业务 API。
- World Engine、Observation Builder、Action Validator、Model Gateway、Memory、Scheduler 的业务实现。
- 生产部署、备份、TLS、可观测性和高可用方案。

TASK-004 开始前必须阅读：

- `docs/architecture-handbook.md`
- `docs/development-handbook.md`
- `docs/ai-collaboration-guide.md`
- `docs/domain-contracts.md`
- `docs/current-status.md`
- `docs/known-issues.md`
- `tasks/TASK_STATUS.md`
- 未来具体的 TASK-004 文件
