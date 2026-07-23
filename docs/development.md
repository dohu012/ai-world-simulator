# 开发约定

- 分支建议：`feature/task-xxx-short-name`、`fix/short-name`。
- 提交保持单一目的，建议使用 Conventional Commits，例如 `feat: add readiness endpoint`。
- 新增依赖时修改对应 `pyproject.toml` 或 `package.json`，说明用途，安装后提交锁文件。
- 创建 Migration：修改模型，执行 `python -m alembic revision --autogenerate -m "description"`，人工检查，再运行升级和降级验证。
- 变更必须补充相应测试；依赖 PostgreSQL/Redis 的测试需要本地基础设施可用。
- 后端使用 Ruff 格式化和 lint、mypy 类型检查；前端使用 ESLint、Prettier 和 TypeScript 严格模式。

