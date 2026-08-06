"""harden production pilot access and freeze enrolled protocols"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260731_0014"
down_revision: str | None = "20260730_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "study_access_codes",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "protocol_id",
            sa.String(96),
            sa.ForeignKey("study_protocols.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("hash_version", sa.String(32), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("protocol_id", "code_hash", name="uq_study_access_code_hash"),
        sa.CheckConstraint("hash_version = 'hmac-sha256-v1'", name="ck_study_code_hash_version"),
    )
    op.create_table(
        "study_deletion_tombstones",
        sa.Column("code_hash", sa.String(64), primary_key=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        """
        CREATE FUNCTION reject_enrolled_study_mutation() RETURNS trigger AS $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM study_protocols p
            WHERE p.id = COALESCE(NEW.protocol_id, OLD.protocol_id)
              AND p.enrollment_started_at IS NOT NULL
          ) THEN
            RAISE EXCEPTION 'enrolled study protocol is immutable';
          END IF;
          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER freeze_study_questions
        BEFORE INSERT OR UPDATE OR DELETE ON study_questions
        FOR EACH ROW EXECUTE FUNCTION reject_enrolled_study_mutation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION reject_enrolled_protocol_update() RETURNS trigger AS $$
        BEGIN
          IF OLD.enrollment_started_at IS NOT NULL AND (
            NEW.version IS DISTINCT FROM OLD.version OR
            NEW.content_hash IS DISTINCT FROM OLD.content_hash OR
            NEW.locale IS DISTINCT FROM OLD.locale OR
            NEW.sample_target IS DISTINCT FROM OLD.sample_target OR
            NEW.frozen_at IS DISTINCT FROM OLD.frozen_at
          ) THEN
            RAISE EXCEPTION 'enrolled study protocol is immutable';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER freeze_study_protocol
        BEFORE UPDATE ON study_protocols
        FOR EACH ROW EXECUTE FUNCTION reject_enrolled_protocol_update()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS freeze_study_protocol ON study_protocols")
    op.execute("DROP FUNCTION IF EXISTS reject_enrolled_protocol_update()")
    op.execute("DROP TRIGGER IF EXISTS freeze_study_questions ON study_questions")
    op.execute("DROP FUNCTION IF EXISTS reject_enrolled_study_mutation()")
    op.drop_table("study_deletion_tombstones")
    op.drop_table("study_access_codes")
