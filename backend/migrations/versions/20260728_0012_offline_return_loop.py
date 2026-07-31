"""add normalized offline return-loop projections"""

from collections.abc import Sequence

from alembic import op

from app.infrastructure.database import return_loop_models as rl

revision: str = "20260728_0012"
down_revision: str | None = "20260728_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in (
        rl.NotificationPreferenceRecord.__table__,
        rl.OfflineIntervalRecord.__table__,
        rl.OfflineSummaryRecord.__table__,
        rl.OfflineSummaryClaimRecord.__table__,
        rl.InboxItemRecord.__table__,
        rl.PlaytestEventRecord.__table__,
    ):
        table.create(bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    for table in (
        rl.PlaytestEventRecord.__table__,
        rl.InboxItemRecord.__table__,
        rl.OfflineSummaryClaimRecord.__table__,
        rl.OfflineSummaryRecord.__table__,
        rl.OfflineIntervalRecord.__table__,
        rl.NotificationPreferenceRecord.__table__,
    ):
        table.drop(bind, checkfirst=False)
