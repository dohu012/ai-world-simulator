# 开发约定入口

完整开发规范见 `docs/development-handbook.md`，AI 协作规范见 `docs/ai-collaboration-guide.md`。本文件保留为早期摘要和入口。

- 提交保持单一目的，建议使用 Conventional Commits。
- 新增依赖时修改对应 `pyproject.toml` 或 `package.json`，说明用途，安装后提交锁文件。
- 创建 Migration 后必须人工检查，再运行升级和降级验证。
- 变更必须补充相应测试。
- 后端使用 Ruff 和 mypy；前端使用 ESLint、Prettier、TypeScript strict mode 和 Vitest。
