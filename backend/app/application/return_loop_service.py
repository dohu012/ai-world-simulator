"""Durable, idempotent offline summary and inbox projection service."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.gray_harbor import WORLD_ID
from app.domain.return_loop import (
    COMPILER_VERSION,
    CausalClaim,
    EpistemicClass,
    NotificationPreferences,
    OfflineSummary,
    compile_summary,
    content_hash,
)
from app.infrastructure.database import return_loop_models as rr


class InboxRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    category: str
    priority: str
    title: str
    preview: str
    fictional: bool
    source_ids: list[str]
    read: bool
    dismissed: bool


class ReturnLoopState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: OfflineSummary
    inbox: list[InboxRead]
    preferences: NotificationPreferences
    debug: dict[str, int | str | bool]


class ReturnLoopService:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    @staticmethod
    def fixed_summary(owner_id: str) -> OfflineSummary:
        start = datetime(2026, 7, 4, 8, tzinfo=UTC)
        end = start + timedelta(days=3)
        rows = (
            (
                "ration",
                "The harbor ration policy changed after the shipment was lost.",
                EpistemicClass.OBJECTIVE,
                0.95,
            ),
            (
                "belief",
                "Chen learned that the north route report had been corrected.",
                EpistemicClass.BELIEVED,
                0.85,
            ),
            (
                "decision",
                "Chen rejected part of the Oracle advice and delayed the route.",
                EpistemicClass.DECIDED,
                0.9,
            ),
            (
                "outcome",
                "Ten rescue seats were allocated by the authoritative world outcome.",
                EpistemicClass.OUTCOME,
                1.0,
            ),
        )
        claims = [
            CausalClaim(
                id=f"return-{key}-{owner_id}",
                owner_id=owner_id,
                world_id=WORLD_ID,
                source_type=key,
                source_id=f"scenario-{key}",
                source_version="1.0.0",
                source_hash=content_hash(WORLD_ID, key, "1.0.0"),
                occurred_at=start + timedelta(hours=index * 10),
                visible_at=start + timedelta(hours=index * 10 + 1),
                epistemic_class=kind,
                text=text,
                agent_id=owner_id,
                importance=importance,
                schema_version="1.0",
            )
            for index, (key, text, kind, importance) in enumerate(rows)
        ]
        return compile_summary(
            summary_id=f"offline-summary-{owner_id}-day4-day7",
            owner_id=owner_id,
            world_id=WORLD_ID,
            interval_start=start,
            interval_end=end,
            claims=claims,
        )

    async def state(self, owner_id: str) -> ReturnLoopState:
        summary = self.fixed_summary(owner_id)
        interval_id = f"offline-interval-{owner_id}-day4-day7"
        preference_id = f"notification-preference-{owner_id}-v1"
        inbox_id = f"inbox-{summary.source_watermark[:24]}"
        logical_key = f"{owner_id}:{summary.source_watermark}:{COMPILER_VERSION}"
        async with self.sessions.begin() as session:
            await session.execute(
                insert(rr.NotificationPreferenceRecord)
                .values(
                    id=preference_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    version=1,
                    active=True,
                    in_site_enabled=True,
                    push_enabled=False,
                    quiet_start=datetime.strptime("22:00", "%H:%M").time(),
                    quiet_end=datetime.strptime("08:00", "%H:%M").time(),
                    timezone="UTC",
                    inbox_daily_cap=4,
                    push_daily_cap=1,
                    paused_until=None,
                    followed_agent_ids={"ids": [owner_id]},
                    enabled_categories={"ids": ["offline_summary", "major_outcome"]},
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await session.execute(
                insert(rr.OfflineIntervalRecord)
                .values(
                    id=interval_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    logical_key="gray-harbor-day4-day7-v1",
                    started_at=summary.interval_start,
                    ended_at=summary.interval_end,
                    source_watermark=summary.source_watermark,
                    preference_version=1,
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await session.execute(
                insert(rr.OfflineSummaryRecord)
                .values(
                    id=summary.id,
                    interval_id=interval_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    source_watermark=summary.source_watermark,
                    compiler_version=COMPILER_VERSION,
                    lifecycle="ready",
                    narrative={"sections": summary.narrative},
                    content_hash=content_hash(*summary.narrative),
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
            for ordinal, claim in enumerate(summary.claims):
                await session.execute(
                    insert(rr.OfflineSummaryClaimRecord)
                    .values(
                        id=f"{summary.id}:claim:{ordinal}",
                        summary_id=summary.id,
                        world_id=WORLD_ID,
                        owner_id=owner_id,
                        source_type=claim.source_type,
                        source_id=claim.source_id,
                        source_version=claim.source_version,
                        source_hash=claim.source_hash,
                        epistemic_class=claim.epistemic_class.value,
                        occurred_at=claim.occurred_at,
                        visible_at=claim.visible_at,
                        text=claim.text,
                        ordinal=ordinal,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            await session.execute(
                insert(rr.InboxItemRecord)
                .values(
                    id=inbox_id,
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    logical_key=logical_key,
                    summary_id=summary.id,
                    category="offline_summary",
                    priority="normal",
                    title="Fictional world summary is ready",
                    preview=f"{len(summary.claims)} source-linked changes from Gray Harbor.",
                    lock_screen_body="A fictional world update is available in your private inbox.",
                    fictional=True,
                    content_hash=content_hash(logical_key),
                    available_at=summary.interval_end,
                    expires_at=summary.interval_end + timedelta(days=30),
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
        async with self.sessions() as session:
            item = (
                await session.execute(
                    select(rr.InboxItemRecord).where(
                        rr.InboxItemRecord.id == inbox_id,
                        rr.InboxItemRecord.owner_id == owner_id,
                    )
                )
            ).scalar_one()
        preferences = NotificationPreferences(
            owner_id=owner_id, world_id=WORLD_ID, followed_agent_ids={owner_id}
        )
        return ReturnLoopState(
            summary=summary,
            inbox=[
                InboxRead(
                    id=item.id,
                    category=item.category,
                    priority=item.priority,
                    title=item.title,
                    preview=item.preview,
                    fictional=item.fictional,
                    source_ids=[claim.source_id for claim in summary.claims],
                    read=item.read_at is not None,
                    dismissed=item.dismissed_at is not None,
                )
            ],
            preferences=preferences,
            debug={
                "candidate_count": len(summary.claims),
                "included_count": len(summary.claims),
                "suppressed_count": 0,
                "push_enabled": False,
                "provider_calls": 0,
                "summary_mode": "deterministic",
            },
        )

    async def mark(self, owner_id: str, item_id: str, action: str) -> bool:
        column = {
            "read": rr.InboxItemRecord.read_at,
            "dismiss": rr.InboxItemRecord.dismissed_at,
            "archive": rr.InboxItemRecord.archived_at,
        }[action]
        async with self.sessions.begin() as session:
            result = await session.execute(
                update(rr.InboxItemRecord)
                .where(
                    rr.InboxItemRecord.id == item_id,
                    rr.InboxItemRecord.owner_id == owner_id,
                    column.is_(None),
                )
                .values({column.key: datetime.now(UTC)})
                .returning(rr.InboxItemRecord.id)
            )
            return result.scalar_one_or_none() is not None

    async def record_event(self, owner_id: str, event_code: str, idempotency_key: str) -> None:
        async with self.sessions.begin() as session:
            await session.execute(
                insert(rr.PlaytestEventRecord)
                .values(
                    id=f"playtest-{uuid4().hex}",
                    world_id=WORLD_ID,
                    owner_id=owner_id,
                    idempotency_key=idempotency_key,
                    event_code=event_code,
                    occurred_at=datetime.now(UTC),
                )
                .on_conflict_do_nothing(index_elements=["world_id", "owner_id", "idempotency_key"])
            )
