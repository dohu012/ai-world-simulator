# 已知限制

- 健康就绪检查依赖本地 PostgreSQL 和 Redis，服务未启动时按设计返回 503。
- Compose 配置面向本地开发，不包含生产部署、备份、TLS 或高可用方案。
- 当前只有验证迁移能力的 `system_metadata` 基础表，不是最终领域模型。
- TASK-003 只建立开发体系，不实现业务功能。
- 后续仍需为 World Engine、Observation Builder、Action Validator、Repository、Model Gateway、Memory 和 Scheduler 分别建立小粒度任务。
- 世界时间暂用带时区的公历 datetime，尚未实现自定义世界历法。
- 尚未定义 `ScheduledEvent` 独立契约；当前 EventType 值不代表未来事件调度能力。
- `schema_version` 已固定为 `1.0`，但尚无契约迁移或历史版本加载工具。
- TypeScript 是 JSON Schema 的静态生成结果；数值范围、日期格式等运行时约束仍由后端
  Pydantic 校验，前端若接收不可信数据，后续仍需增加运行时验证。
- 2026-07-23 的 `npm audit --omit=dev` 对 TASK-001 既有 Next.js 依赖链报告 1 个 moderate
  和 2 个 high 告警（PostCSS、sharp）；TASK-002 未升级公共前端技术栈。
