# AI 世界观察与干预模拟器

纯文字 AI 世界模拟产品。当前已完成前后端工程骨架与第一版最小领域公共契约；尚未实现
领域持久化、世界裁定、感知过滤、Agent 决策或模型调用。

## 技术栈与环境

- 前端：Next.js App Router、React、TypeScript、Tailwind CSS、TanStack Query
- 后端：Python 3.12+、FastAPI、Pydantic v2、SQLAlchemy 2、Alembic、Redis
- 基础设施：Docker Compose、PostgreSQL、Redis
- 需要：Node.js 20+、npm、Python 3.12+、Docker Desktop；可选 GNU Make

## 本地启动

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

另开终端：

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000`。API 默认位于 `http://localhost:8000`。

使用 GNU Make 时可运行 `make infra-up`、`make backend-dev`、`make frontend-dev`。`make dev` 会提示需要分别启动的进程；Windows 未安装 Make 时请使用上面的原生命令。

## 环境变量

根目录 `.env.example` 包含全部示例值。后端读取 `APP_ENV`、`APP_HOST`、`APP_PORT`、`DATABASE_URL`、`REDIS_URL`、`CORS_ORIGINS` 和 `LOG_LEVEL`；前端读取 `NEXT_PUBLIC_API_BASE_URL`；Compose 读取 `POSTGRES_DB`、`POSTGRES_USER`、`POSTGRES_PASSWORD`。示例凭据仅用于本地开发。

## 迁移、测试与质量检查

```powershell
cd backend
python -m alembic upgrade head
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m app.domain.export_schemas

cd ..\frontend
npm run generate:domain-types
npm run typecheck
npm run lint
npm run format:check
npm run test
npm run build
```

创建迁移：`python -m alembic revision --autogenerate -m "description"`，随后检查脚本并执行升级。检查模型与迁移是否一致：`python -m alembic check`。

领域模型位于 `backend/app/domain/`，契约说明见
[`docs/domain-contracts.md`](docs/domain-contracts.md)。Python 是契约唯一来源；导出的
JSON Schema 位于 `schemas/domain/`，生成的前端声明位于
`frontend/src/types/generated/`，前端统一从 `frontend/src/types/domain` 导入。

## 常见问题

- `/health/ready` 返回 503：确认 Compose 服务健康、`.env` 地址正确且迁移已执行。
- 浏览器请求失败：确认后端端口和 `NEXT_PUBLIC_API_BASE_URL` 一致，并在 `CORS_ORIGINS` 中允许前端来源。
- 端口冲突：修改 Compose 端口映射，并同步修改连接 URL。
- Windows 上没有 `make`：直接使用上述 PowerShell/npm/Python 命令。
