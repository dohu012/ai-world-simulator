"""add normalized controlled product-validation records"""

from collections.abc import Sequence

from alembic import op

from app.infrastructure.database import product_validation_models as pv

revision: str = "20260730_0013"
down_revision: str | None = "20260728_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in (
        pv.StudyProtocolRecord.__table__,
        pv.StudyParticipantRecord.__table__,
        pv.StudyQuestionRecord.__table__,
        pv.StudyConsentRecord.__table__,
        pv.StudyPeriodRecord.__table__,
        pv.StudyResponseRecord.__table__,
        pv.StudyDemandProbeRecord.__table__,
        pv.StudyReportRecord.__table__,
    ):
        table.create(bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    for table in (
        pv.StudyReportRecord.__table__,
        pv.StudyDemandProbeRecord.__table__,
        pv.StudyResponseRecord.__table__,
        pv.StudyPeriodRecord.__table__,
        pv.StudyConsentRecord.__table__,
        pv.StudyQuestionRecord.__table__,
        pv.StudyParticipantRecord.__table__,
        pv.StudyProtocolRecord.__table__,
    ):
        table.drop(bind, checkfirst=False)
