# 已知限制

- 健康就绪检查依赖本地 PostgreSQL 和 Redis，服务未启动时按设计返回 503。
- Compose 配置面向本地开发，不包含生产部署、备份、TLS 或高可用方案。
- 当前只有验证迁移能力的 `system_metadata` 基础表，不是最终领域模型。

