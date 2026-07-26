"""add explicit Gray Harbor location topology

Revision ID: 20260726_0003
Revises: 20260725_0002
"""

from collections.abc import Sequence

from alembic import op

from app.infrastructure.database.base import Base

revision: str = "20260726_0003"
down_revision: str | None = "20260725_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.tables["locations"].create(bind, checkfirst=False)
    Base.metadata.tables["location_edges"].create(bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.tables["location_edges"].drop(bind, checkfirst=False)
    Base.metadata.tables["locations"].drop(bind, checkfirst=False)
