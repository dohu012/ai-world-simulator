"""add causal communication belief revision and bounded dialogue"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260727_0007"
down_revision: str | None = "20260727_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "communication_channels",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("delay_minutes", sa.Integer(), nullable=False),
        sa.Column("reliability_milli", sa.Integer(), nullable=False),
        sa.Column("distortion_policy_id", sa.String(64), nullable=False),
        sa.Column("privacy_class", sa.String(32), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("delay_minutes >= 0 AND delay_minutes <= 1440", name="ck_channel_delay"),
        sa.CheckConstraint(
            "reliability_milli >= 0 AND reliability_milli <= 1000", name="ck_channel_reliability"
        ),
    )
    op.create_index("ix_communication_channels_world_id", "communication_channels", ["world_id"])
    op.create_table(
        "messages",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_id", sa.String(128), sa.ForeignKey("characters.id", ondelete="SET NULL")),
        sa.Column("content_kind", sa.String(32), nullable=False),
        sa.Column("body", sa.String(1000), nullable=False),
        sa.Column("claims", postgresql.JSONB(), nullable=False),
        sa.Column("sent_world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_messages_world_id", "messages", ["world_id"])
    op.create_index("ix_messages_correlation_id", "messages", ["correlation_id"])
    op.create_table(
        "transmissions",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("delivery_key", sa.String(180), nullable=False),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "message_id",
            sa.String(128),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "channel_id",
            sa.String(128),
            sa.ForeignKey("communication_channels.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("sender_id", sa.String(128), sa.ForeignKey("characters.id", ondelete="SET NULL")),
        sa.Column(
            "recipient_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("sent_world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("claim_owner", sa.String(128)),
        sa.Column("claim_token", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column(
            "delivered_observation_id",
            sa.String(128),
            sa.ForeignKey("observations.id", ondelete="SET NULL"),
            unique=True,
        ),
        sa.Column(
            "delivered_wake_id",
            sa.String(128),
            sa.ForeignKey("agent_wakes.id", ondelete="SET NULL"),
            unique=True,
        ),
        sa.Column("failure_code", sa.String(64)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("delivery_key", name="uq_transmission_delivery_key"),
    )
    op.create_index(
        "ix_transmissions_due_order",
        "transmissions",
        ["world_id", "status", "arrival_world_time", "priority", "created_at", "id"],
    )
    op.create_table(
        "belief_evidence",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("proposition_key", sa.String(128), nullable=False),
        sa.Column(
            "observation_id",
            sa.String(128),
            sa.ForeignKey("observations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("causal_source_key", sa.String(160), nullable=False),
        sa.Column("stance", sa.String(32), nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("reliability_milli", sa.Integer(), nullable=False),
        sa.Column("world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint(
            "agent_id", "proposition_key", "observation_id", name="uq_belief_evidence_observation"
        ),
    )
    op.create_table(
        "belief_revisions",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("proposition_key", sa.String(128), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "prior_revision_id",
            sa.String(128),
            sa.ForeignKey("belief_revisions.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "evidence_id",
            sa.String(128),
            sa.ForeignKey("belief_evidence.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("confidence_milli", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("reason_code", sa.String(64), nullable=False),
        sa.Column("policy_version", sa.String(32), nullable=False),
        sa.Column("causal_source_keys", postgresql.JSONB(), nullable=False),
        sa.Column("world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint(
            "agent_id", "proposition_key", "revision", name="uq_belief_revision_number"
        ),
    )
    op.create_index(
        "ix_belief_revisions_current",
        "belief_revisions",
        ["world_id", "agent_id", "proposition_key", "revision"],
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column(
            "world_id",
            sa.String(128),
            sa.ForeignKey("worlds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("correlation_id", sa.String(128), nullable=False, unique=True),
        sa.Column("participant_ids", postgresql.JSONB(), nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column(
            "current_speaker_id",
            sa.String(128),
            sa.ForeignKey("characters.id", ondelete="SET NULL"),
        ),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_turns", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("used_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_tokens", sa.Integer(), nullable=False, server_default="1200"),
        sa.Column("world_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "latest_transmission_id",
            sa.String(128),
            sa.ForeignKey("transmissions.id", ondelete="SET NULL"),
        ),
        sa.Column("terminal_reason", sa.String(64)),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "turn_count >= 0 AND turn_count <= max_turns", name="ck_conversation_turns"
        ),
        sa.CheckConstraint(
            "used_tokens >= 0 AND used_tokens <= max_tokens", name="ck_conversation_tokens"
        ),
        sa.CheckConstraint("max_turns >= 1 AND max_turns <= 3", name="ck_conversation_max_turns"),
    )
    op.create_index("ix_conversations_world_id", "conversations", ["world_id"])


def downgrade() -> None:
    op.drop_index("ix_conversations_world_id", table_name="conversations")
    op.drop_table("conversations")
    op.drop_index("ix_belief_revisions_current", table_name="belief_revisions")
    op.drop_table("belief_revisions")
    op.drop_table("belief_evidence")
    op.drop_index("ix_transmissions_due_order", table_name="transmissions")
    op.drop_table("transmissions")
    op.drop_index("ix_messages_correlation_id", table_name="messages")
    op.drop_index("ix_messages_world_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_communication_channels_world_id", table_name="communication_channels")
    op.drop_table("communication_channels")
