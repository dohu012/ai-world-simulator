"""add auditable long-term memory and retrieval traces"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260728_0010"
down_revision: str | None = "20260728_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "memory_items",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("logical_key", sa.String(128), nullable=False),
        sa.Column("memory_type", sa.String(32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("admission_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("metadata_payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "supersedes_id", sa.String(128), sa.ForeignKey("memory_items.id", ondelete="RESTRICT")
        ),
        sa.Column("tombstoned_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("admission_score BETWEEN 0 AND 1", name="ck_memory_admission_score"),
        sa.CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_memory_confidence"),
        sa.UniqueConstraint(
            "world_id", "owner_id", "logical_key", "policy_version", name="uq_memory_logical"
        ),
    )
    op.create_index(
        "ix_memory_owner_time_type",
        "memory_items",
        ["world_id", "owner_id", "occurred_at", "memory_type"],
    )
    op.create_table(
        "memory_sources",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "memory_id",
            sa.String(128),
            sa.ForeignKey("memory_items.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("world_id", sa.String(128), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_id", sa.String(128), nullable=False),
        sa.UniqueConstraint("memory_id", "source_type", "source_id", name="uq_memory_source"),
    )
    op.create_table(
        "memory_embeddings",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "memory_id",
            sa.String(128),
            sa.ForeignKey("memory_items.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("model_revision", sa.String(128), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("vector", postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metrics", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("dimensions > 0 AND dimensions <= 4096", name="ck_embedding_dimensions"),
        sa.UniqueConstraint(
            "memory_id", "model_revision", "content_hash", name="uq_memory_embedding_revision"
        ),
    )
    op.create_table(
        "memory_embedding_jobs",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "memory_id",
            sa.String(128),
            sa.ForeignKey("memory_items.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("model_revision", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("claim_owner", sa.String(128)),
        sa.Column("claim_token", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("retry_at", sa.DateTime(timezone=True)),
        sa.Column("failure_code", sa.String(64)),
        sa.UniqueConstraint("memory_id", "model_revision", name="uq_embedding_job"),
    )
    op.create_index(
        "ix_embedding_jobs_claim",
        "memory_embedding_jobs",
        ["status", "retry_at", "lease_expires_at"],
    )
    op.create_table(
        "memory_retrieval_runs",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "decision_id", sa.String(128), sa.ForeignKey("agent_decisions.id", ondelete="RESTRICT")
        ),
        sa.Column("world_id", sa.String(128), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("cutoff", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column("embedding_revision", sa.String(128)),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("context_watermark", sa.String(64), nullable=False),
        sa.Column("token_budget", sa.Integer(), nullable=False),
        sa.Column("token_used", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint(
            "decision_id", "context_watermark", name="uq_retrieval_decision_context"
        ),
    )
    op.create_table(
        "memory_retrieval_candidates",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "retrieval_id",
            sa.String(160),
            sa.ForeignKey("memory_retrieval_runs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "memory_id",
            sa.String(128),
            sa.ForeignKey("memory_items.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False),
        sa.Column("exclusion_reason", sa.String(32), nullable=False),
        sa.Column("score_components", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("rank > 0", name="ck_retrieval_candidate_rank"),
        sa.UniqueConstraint("retrieval_id", "memory_id", name="uq_retrieval_candidate"),
    )


def downgrade() -> None:
    op.drop_table("memory_retrieval_candidates")
    op.drop_table("memory_retrieval_runs")
    op.drop_index("ix_embedding_jobs_claim", table_name="memory_embedding_jobs")
    op.drop_table("memory_embedding_jobs")
    op.drop_table("memory_embeddings")
    op.drop_table("memory_sources")
    op.drop_index("ix_memory_owner_time_type", table_name="memory_items")
    op.drop_table("memory_items")
