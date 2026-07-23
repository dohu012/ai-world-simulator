# Domain

这里保存不依赖 FastAPI、SQLAlchemy、Redis 或模型 SDK 的纯领域契约。

`schemas.py` 是 Python 公共入口；`python -m app.domain.export_schemas` 将契约稳定导出到
`schemas/domain/`。本目录只定义数据结构和校验，不包含持久化、世界裁定、感知过滤、
Agent 决策或模型调用。
