"""add durable world runtime, schedules, wakes, oracle windows and outbox"""

from collections.abc import Sequence

from alembic import op

from app.infrastructure.database import models as _models  # noqa: F401
from app.infrastructure.database.base import Base

revision: str = "20260727_0005"
down_revision: str | None = "20260726_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
TABLES = (
    "world_runtimes",
    "scheduled_world_events",
    "agent_wakes",
    "oracle_windows",
    "notification_outbox",
)


def upgrade() -> None:
    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    for name in reversed(TABLES):
        Base.metadata.tables[name].drop(bind, checkfirst=False)
