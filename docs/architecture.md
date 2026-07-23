# 基础架构入口

最高级别架构规范见 `docs/architecture-handbook.md`。本文件保留为早期架构摘要和入口。

- 前端负责状态展示和 API 调用。
- 后端负责 HTTP 边界、配置、依赖检查及基础设施适配。
- PostgreSQL 提供持久化。
- Redis 仅提供后续可复用的连接能力，本阶段没有缓存、发布订阅或锁业务。
- `backend/app/domain` 是 Pydantic v2 纯领域契约来源，不依赖 FastAPI、SQLAlchemy、Redis 或模型供应商 SDK。
- `schemas/domain` 由 Python 领域模型导出，不手工修改。
- `frontend/src/types/domain` 是前端领域类型公共入口。
