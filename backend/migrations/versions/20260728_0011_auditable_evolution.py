"""add auditable identity and directional relationship evolution"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260728_0011"
down_revision: str | None = "20260728_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "identity_baselines",
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
        sa.Column(
            "agent_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("structured_state", postgresql.JSONB(), nullable=False),
        sa.Column("persona_summary", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("generation > 0", name="ck_identity_baseline_generation"),
        sa.CheckConstraint("char_length(content_hash) = 64", name="ck_identity_baseline_hash"),
        sa.UniqueConstraint(
            "world_id", "owner_id", "agent_id", "generation", name="uq_identity_baseline_generation"
        ),
    )
    op.create_table(
        "identity_snapshots",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "baseline_id",
            sa.String(128),
            sa.ForeignKey("identity_baselines.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("world_id", sa.String(128), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("agent_id", sa.String(128), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("offsets", postgresql.JSONB(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("persona_summary", sa.Text(), nullable=False),
        sa.Column("evidence_horizon", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column(
            "previous_snapshot_id",
            sa.String(128),
            sa.ForeignKey("identity_snapshots.id", ondelete="RESTRICT"),
        ),
        sa.Column("lifecycle", sa.String(16), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("version > 0", name="ck_identity_snapshot_version"),
        sa.CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_identity_snapshot_confidence"),
        sa.CheckConstraint(
            "lifecycle IN ('active','superseded','reverted','invalidated')",
            name="ck_identity_snapshot_lifecycle",
        ),
        sa.UniqueConstraint("baseline_id", "version", name="uq_identity_snapshot_version"),
    )
    op.create_index(
        "ix_identity_snapshot_current",
        "identity_snapshots",
        ["world_id", "owner_id", "agent_id", "lifecycle", "version"],
    )
    op.create_table(
        "relationship_snapshots",
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
        sa.Column(
            "subject_agent_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(16), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("dimensions", postgresql.JSONB(), nullable=False),
        sa.Column("uncertainty", sa.Float(), nullable=False),
        sa.Column("interpretation", sa.Text(), nullable=False),
        sa.Column("evidence_horizon", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column(
            "previous_snapshot_id",
            sa.String(128),
            sa.ForeignKey("relationship_snapshots.id", ondelete="RESTRICT"),
        ),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("target_type IN ('agent','oracle')", name="ck_relationship_target_type"),
        sa.CheckConstraint("version > 0", name="ck_relationship_version"),
        sa.CheckConstraint("uncertainty BETWEEN 0 AND 1", name="ck_relationship_uncertainty"),
        sa.CheckConstraint(
            "target_type <> 'agent' OR subject_agent_id <> target_id",
            name="ck_relationship_not_self",
        ),
        sa.UniqueConstraint(
            "world_id",
            "owner_id",
            "subject_agent_id",
            "target_type",
            "target_id",
            "version",
            name="uq_relationship_version",
        ),
    )
    op.create_index(
        "ix_relationship_current",
        "relationship_snapshots",
        ["world_id", "owner_id", "subject_agent_id", "active", "target_type", "target_id"],
    )
    op.create_table(
        "reflection_jobs",
        sa.Column("id", sa.String(160), primary_key=True),
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
        sa.Column(
            "agent_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("logical_key", sa.String(256), nullable=False),
        sa.Column("evidence_watermark", sa.String(64), nullable=False),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("claim_owner", sa.String(128)),
        sa.Column("claim_token", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("retry_at", sa.DateTime(timezone=True)),
        sa.Column("failure_code", sa.String(64)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("logical_key", name="uq_reflection_logical_key"),
    )
    op.create_index(
        "ix_reflection_claim", "reflection_jobs", ["status", "retry_at", "lease_expires_at"]
    )
    op.create_table(
        "evolution_deltas",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "job_id",
            sa.String(160),
            sa.ForeignKey("reflection_jobs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("world_id", sa.String(128), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("agent_id", sa.String(128), nullable=False),
        sa.Column("snapshot_kind", sa.String(16), nullable=False),
        sa.Column("snapshot_id", sa.String(128), nullable=False),
        sa.Column("dimension", sa.String(32), nullable=False),
        sa.Column("proposed_magnitude", sa.Float(), nullable=False),
        sa.Column("applied_magnitude", sa.Float(), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("rationale", sa.String(600), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "snapshot_kind IN ('identity','relationship')", name="ck_evolution_delta_kind"
        ),
        sa.CheckConstraint(
            "proposed_magnitude BETWEEN -1 AND 1", name="ck_evolution_proposed_range"
        ),
        sa.CheckConstraint("applied_magnitude BETWEEN -1 AND 1", name="ck_evolution_applied_range"),
        sa.UniqueConstraint(
            "job_id",
            "snapshot_kind",
            "snapshot_id",
            "dimension",
            name="uq_evolution_delta_dimension",
        ),
    )
    op.create_table(
        "evolution_evidence_links",
        sa.Column("id", sa.String(192), primary_key=True),
        sa.Column(
            "delta_id",
            sa.String(160),
            sa.ForeignKey("evolution_deltas.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "memory_id",
            sa.String(128),
            sa.ForeignKey("memory_items.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("world_id", sa.String(128), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("visible_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_role", sa.String(32), nullable=False),
        sa.Column("independent_key", sa.String(160), nullable=False),
        sa.CheckConstraint("visible_from >= occurred_at", name="ck_evolution_evidence_time"),
        sa.UniqueConstraint("delta_id", "memory_id", name="uq_evolution_evidence_link"),
    )


def downgrade() -> None:
    op.drop_table("evolution_evidence_links")
    op.drop_table("evolution_deltas")
    op.drop_index("ix_reflection_claim", table_name="reflection_jobs")
    op.drop_table("reflection_jobs")
    op.drop_index("ix_relationship_current", table_name="relationship_snapshots")
    op.drop_table("relationship_snapshots")
    op.drop_index("ix_identity_snapshot_current", table_name="identity_snapshots")
    op.drop_table("identity_snapshots")
    op.drop_table("identity_baselines")
