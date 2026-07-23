# 基础架构

前端负责状态展示和 API 调用；后端负责 HTTP 边界、配置、依赖检查及基础设施适配；PostgreSQL 提供持久化；Redis 仅提供后续可复用的连接能力，本阶段没有缓存、发布订阅或锁业务。

后端依赖方向为 `api -> services/repositories -> domain`，基础设施通过外层模块接入。`domain` 层不得依赖 FastAPI、SQLAlchemy、Redis 或模型供应商 SDK。当前空目录用 README 说明边界，避免提前设计业务抽象。

- `frontend/src/app`：页面与 Providers
- `frontend/src/lib`：集中 API client
- `frontend/src/features`：按功能组织的 UI
- `backend/app/api`：HTTP 路由和错误响应
- `backend/app/core`：配置、日志、中间件
- `backend/app/infrastructure`：数据库与 Redis 生命周期
- `backend/app/domain`：未来纯领域代码

