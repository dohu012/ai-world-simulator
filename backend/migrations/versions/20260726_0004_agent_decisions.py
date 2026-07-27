"""add auditable agent decisions and model attempts"""

from collections.abc import Sequence

from alembic import op

from app.infrastructure.database.base import Base

revision: str = "20260726_0004"
down_revision: str | None = "20260726_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    for name in ("prompt_versions", "agent_decisions", "model_call_attempts"):
        Base.metadata.tables[name].create(bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    for name in ("model_call_attempts", "agent_decisions", "prompt_versions"):
        Base.metadata.tables[name].drop(bind, checkfirst=False)
