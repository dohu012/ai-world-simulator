"""create persistent replayable world-state tables
Revision ID: 20260725_0002
Revises: 20260723_0001
"""

from collections.abc import Sequence

from alembic import op

from app.infrastructure.database.base import Base

revision: str = "20260725_0002"
down_revision: str | None = "20260723_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
TABLES = [
    "worlds",
    "characters",
    "agent_profiles",
    "world_facts",
    "world_events",
    "observations",
    "agent_beliefs",
    "oracle_requests",
    "oracle_responses",
    "action_intents",
    "action_results",
]


def upgrade() -> None:
    bind = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    for name in reversed(TABLES):
        Base.metadata.tables[name].drop(bind, checkfirst=False)
