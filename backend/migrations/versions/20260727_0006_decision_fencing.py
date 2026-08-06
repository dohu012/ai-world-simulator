"""add decision claim fencing token"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260727_0006"
down_revision: str | None = "20260727_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    columns = {
        column["name"] for column in sa.inspect(op.get_bind()).get_columns("agent_decisions")
    }
    if "claim_token" not in columns:
        op.add_column(
            "agent_decisions",
            sa.Column("claim_token", sa.Integer(), nullable=False, server_default="1"),
        )
    op.alter_column("agent_decisions", "claim_token", server_default=None)


def downgrade() -> None:
    columns = {
        column["name"] for column in sa.inspect(op.get_bind()).get_columns("agent_decisions")
    }
    if "claim_token" in columns:
        op.drop_column("agent_decisions", "claim_token")
