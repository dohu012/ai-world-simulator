"""Durable, deterministic fixed-scenario propagation and bounded dialogue."""

from datetime import datetime, timedelta
from hashlib import sha256

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.gray_harbor import WORLD_ID
from app.application.social_observation_builder import SocialObservationBuilder
from app.domain.communication import (
    BeliefProjection,
    ClaimStance,
    MessageClaim,
    revise_belief,
)
from app.infrastructure.database import models as db
from app.infrastructure.database import runtime_models as runtime_db
from app.infrastructure.database import social_models as social_db

LIN_ID = "char-lin-zhixia"
ZHOU_ID = "char-zhou-qiming"
CHEN_ID = "char-chen-mo"
PROPOSITION = "gray_harbor.north_gate.closure_time"
SOURCE_KEY = "north-gate-order-v1"


class PropagationItemRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transmission_id: str
    message_id: str
    recipient_id: str
    channel_kind: str
    sent_world_time: str
    arrival_world_time: str
    status: str
    reliability: float
    distortion_policy_id: str
    claim_value: str
    observation_id: str | None


class BeliefRevisionRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    agent_id: str
    proposition_key: str
    revision: int
    value: str
    confidence: float
    status: str
    reason_code: str
    world_time: str


class ConversationRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    participant_ids: list[str]
    state: str
    current_speaker_id: str | None
    turn_count: int
    max_turns: int
    used_tokens: int
    max_tokens: int
    terminal_reason: str | None


class SocialRuntimeService:
    """PostgreSQL is authority; reads never invent delivery or belief state."""

    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    async def seed_scenario(self) -> None:
        async with self.sessions() as session:
            runtime = await session.get(runtime_db.WorldRuntimeRecord, WORLD_ID)
            world = await session.get(db.WorldRecord, WORLD_ID)
            if world is None:
                return
            sent_at = runtime.current_world_time if runtime else world.current_time
            await self._seed(session, sent_at)
            await session.commit()

    async def deliver_due(self) -> None:
        """Claim due rows with SKIP LOCKED and commit each winner exactly once."""
        async with self.sessions() as session:
            runtime = await session.get(runtime_db.WorldRuntimeRecord, WORLD_ID)
            if runtime is None or runtime.status != "running":
                return
            rows = list(
                (
                    await session.scalars(
                        select(social_db.TransmissionRecord)
                        .where(
                            social_db.TransmissionRecord.world_id == WORLD_ID,
                            social_db.TransmissionRecord.status == "scheduled",
                            social_db.TransmissionRecord.arrival_world_time
                            <= runtime.current_world_time,
                        )
                        .order_by(
                            social_db.TransmissionRecord.arrival_world_time,
                            social_db.TransmissionRecord.priority,
                            social_db.TransmissionRecord.created_at,
                            social_db.TransmissionRecord.id,
                        )
                        .limit(runtime.catch_up_limit)
                        .with_for_update(skip_locked=True)
                    )
                ).all()
            )
            for row in rows:
                await self._deliver(session, row)
            await self._expire_conversations(session, runtime.current_world_time)
            await session.commit()

    async def _seed(self, session: AsyncSession, sent_at: datetime) -> None:
        if await session.get(social_db.MessageRecord, "message-gate-lin-v1") is not None:
            return
        assert hasattr(sent_at, "isoformat")
        channels = [
            ("channel-direct-official-v1", "direct", 0, 980, "none", "private"),
            ("channel-bulletin-v1", "official_bulletin", 10, 940, "none", "restricted"),
            ("channel-courier-v1", "courier", 20, 520, "all-gates-earlier-v1", "private"),
            ("channel-direct-dialogue-v1", "direct", 5, 900, "none", "private"),
        ]
        for channel_id, kind, delay, reliability, distortion, privacy in channels:
            session.add(
                social_db.CommunicationChannelRecord(
                    id=channel_id,
                    world_id=WORLD_ID,
                    version=1,
                    kind=kind,
                    delay_minutes=delay,
                    reliability_milli=reliability,
                    distortion_policy_id=distortion,
                    privacy_class=privacy,
                    payload={"max_payload_chars": 1000, "policy_version": "routing-v1"},
                )
            )
        plans = [
            (
                "lin",
                LIN_ID,
                "channel-direct-official-v1",
                0,
                10,
                ClaimStance.OBSERVED,
                "north gate closes at 12:00",
                "Official order: the north gate closes at 12:00.",
            ),
            (
                "zhou",
                ZHOU_ID,
                "channel-bulletin-v1",
                10,
                20,
                ClaimStance.HEARD,
                "north gate closes at 12:00",
                "Bulletin: the north gate closes at 12:00.",
            ),
            (
                "chen",
                CHEN_ID,
                "channel-courier-v1",
                20,
                30,
                ClaimStance.UNCERTAIN,
                "all gates may close at 11:30",
                "A courier says all gates may close by 11:30.",
            ),
        ]
        for suffix, recipient, channel_id, delay, priority, stance, value, body in plans:
            message_id = f"message-gate-{suffix}-v1"
            claim = MessageClaim(
                proposition_key=PROPOSITION,
                stance=stance,
                value=value,
                attribution="harbor authority" if suffix != "chen" else "courier rumor",
                causal_source_key=SOURCE_KEY,
            )
            session.add(
                social_db.MessageRecord(
                    id=message_id,
                    world_id=WORLD_ID,
                    sender_id=None,
                    content_kind="gate_notice",
                    body=body,
                    claims=[claim.model_dump(mode="json")],
                    sent_world_time=sent_at,
                    correlation_id="corr-north-gate-propagation-v1",
                )
            )
            session.add(
                social_db.TransmissionRecord(
                    id=f"transmission-gate-{suffix}-v1",
                    delivery_key=f"{message_id}:{channel_id}:{recipient}:v1",
                    world_id=WORLD_ID,
                    message_id=message_id,
                    channel_id=channel_id,
                    sender_id=None,
                    recipient_id=recipient,
                    status="scheduled",
                    sent_world_time=sent_at,
                    arrival_world_time=sent_at + timedelta(minutes=delay),
                    priority=priority,
                )
            )

    async def _deliver(
        self, session: AsyncSession, transmission: social_db.TransmissionRecord
    ) -> None:
        if transmission.status != "scheduled":
            return
        message = await session.get(social_db.MessageRecord, transmission.message_id)
        channel = await session.get(social_db.CommunicationChannelRecord, transmission.channel_id)
        if message is None or channel is None:
            transmission.status = "terminal_failed"
            transmission.failure_code = "COMMUNICATION_CHANNEL_UNAVAILABLE"
            return
        observation_id = f"obs-{transmission.id}"
        wake_id = f"wake-{transmission.id}"
        observation = SocialObservationBuilder().build_for_message(
            observation_id=observation_id,
            world_id=WORLD_ID,
            recipient_id=transmission.recipient_id,
            message_id=message.id,
            sender_id=message.sender_id,
            body=message.body,
            sent_at=message.sent_world_time,
            delivered_at=transmission.arrival_world_time,
            channel_kind=channel.kind,
            reliability=channel.reliability_milli / 1000,
        )
        if await session.get(db.ObservationRecord, observation_id) is None:
            session.add(
                db.ObservationRecord(
                    id=observation.id,
                    world_id=WORLD_ID,
                    agent_id=observation.agent_id,
                    observed_at=observation.observed_at,
                    source_event_id=None,
                    source_message_id=message.id,
                    schema_version=observation.schema_version,
                    payload=observation.model_dump(mode="json"),
                )
            )
        if await session.get(runtime_db.AgentWakeRecord, wake_id) is None:
            session.add(
                runtime_db.AgentWakeRecord(
                    id=wake_id,
                    world_id=WORLD_ID,
                    agent_id=transmission.recipient_id,
                    causal_key=transmission.delivery_key,
                    reason="message_delivered",
                    observation_ids=[observation_id],
                    status="completed",
                )
            )
        claim = MessageClaim.model_validate(message.claims[0])
        await self._append_revision(
            session,
            recipient_id=transmission.recipient_id,
            observation_id=observation_id,
            claim=claim,
            reliability=channel.reliability_milli / 1000,
            world_time=transmission.arrival_world_time,
        )
        transmission.status = "delivered"
        transmission.attempts += 1
        transmission.claim_token += 1
        transmission.delivered_observation_id = observation_id
        transmission.delivered_wake_id = wake_id
        await self._advance_conversation(session, transmission)

    async def _append_revision(
        self,
        session: AsyncSession,
        *,
        recipient_id: str,
        observation_id: str,
        claim: MessageClaim,
        reliability: float,
        world_time: datetime,
    ) -> None:
        prior_row = await session.scalar(
            select(social_db.BeliefRevisionRecord)
            .where(
                social_db.BeliefRevisionRecord.agent_id == recipient_id,
                social_db.BeliefRevisionRecord.proposition_key == claim.proposition_key,
            )
            .order_by(social_db.BeliefRevisionRecord.revision.desc())
            .limit(1)
        )
        prior = (
            BeliefProjection(
                proposition_key=prior_row.proposition_key,
                value=prior_row.value,
                confidence=prior_row.confidence_milli / 1000,
                status=prior_row.status,
                reason_code=prior_row.reason_code,
                causal_source_keys=[str(value) for value in prior_row.causal_source_keys],
            )
            if prior_row
            else None
        )
        projection = revise_belief(prior, claim, reliability=reliability)
        evidence_id = (
            "evidence-"
            + sha256(
                f"{recipient_id}:{observation_id}:{claim.proposition_key}".encode()
            ).hexdigest()[:24]
        )
        revision_number = 1 if prior_row is None else prior_row.revision + 1
        revision_id = f"revision-{recipient_id.removeprefix('char-')}-{revision_number}"
        session.add(
            social_db.BeliefEvidenceRecord(
                id=evidence_id,
                world_id=WORLD_ID,
                agent_id=recipient_id,
                proposition_key=claim.proposition_key,
                observation_id=observation_id,
                causal_source_key=claim.causal_source_key,
                stance=claim.stance.value,
                value=claim.value,
                reliability_milli=round(reliability * 1000),
                world_time=world_time,
            )
        )
        session.add(
            social_db.BeliefRevisionRecord(
                id=revision_id,
                world_id=WORLD_ID,
                agent_id=recipient_id,
                proposition_key=claim.proposition_key,
                revision=revision_number,
                prior_revision_id=prior_row.id if prior_row else None,
                evidence_id=evidence_id,
                status=projection.status.value,
                confidence_milli=round(projection.confidence * 1000),
                value=projection.value,
                reason_code=projection.reason_code,
                policy_version="belief-v1",
                causal_source_keys=projection.causal_source_keys,
                world_time=world_time,
            )
        )

    async def open_correction_dialogue(self) -> ConversationRead:
        """Server-owned Chen闁愁偅濡琱ou闁愁偅澧玥en fixture, capped at three delivered turns."""
        async with self.sessions() as session:
            runtime = await session.get(
                runtime_db.WorldRuntimeRecord, WORLD_ID, with_for_update=True
            )
            if runtime is None:
                raise ValueError("WORLD_RUNTIME_NOT_STARTED")
            existing = await session.get(social_db.ConversationRecord, "conversation-chen-zhou-v1")
            if existing is None:
                chen_belief = await session.scalar(
                    select(social_db.BeliefRevisionRecord).where(
                        social_db.BeliefRevisionRecord.agent_id == CHEN_ID,
                        social_db.BeliefRevisionRecord.proposition_key == PROPOSITION,
                    )
                )
                if chen_belief is None:
                    raise ValueError("MESSAGE_CLAIM_NOT_KNOWN")
                existing = social_db.ConversationRecord(
                    id="conversation-chen-zhou-v1",
                    world_id=WORLD_ID,
                    correlation_id="corr-conversation-chen-zhou-v1",
                    participant_ids=[CHEN_ID, ZHOU_ID],
                    state="awaiting_delivery",
                    current_speaker_id=ZHOU_ID,
                    turn_count=0,
                    max_turns=3,
                    used_tokens=0,
                    max_tokens=1200,
                    world_deadline=runtime.current_world_time + timedelta(minutes=30),
                )
                session.add(existing)
                await self._create_dialogue_message(
                    session,
                    message_id="message-chen-asks-zhou-v1",
                    transmission_id="transmission-chen-asks-zhou-v1",
                    sender_id=CHEN_ID,
                    recipient_id=ZHOU_ID,
                    body="Did an official notice say every gate closes by 11:30?",
                    claim=MessageClaim(
                        proposition_key=PROPOSITION,
                        stance=ClaimStance.UNCERTAIN,
                        value=chen_belief.value,
                        attribution="Chen asking for confirmation",
                        causal_source_key=SOURCE_KEY,
                    ),
                    sent_at=runtime.current_world_time,
                )
                await session.flush()
                existing.latest_transmission_id = "transmission-chen-asks-zhou-v1"
            await session.commit()
        return (await self.conversations())[0]

    async def _create_dialogue_message(
        self,
        session: AsyncSession,
        *,
        message_id: str,
        transmission_id: str,
        sender_id: str,
        recipient_id: str,
        body: str,
        claim: MessageClaim,
        sent_at: datetime,
    ) -> None:
        session.add(
            social_db.MessageRecord(
                id=message_id,
                world_id=WORLD_ID,
                sender_id=sender_id,
                content_kind="dialogue",
                body=body,
                claims=[claim.model_dump(mode="json")],
                sent_world_time=sent_at,
                correlation_id="corr-conversation-chen-zhou-v1",
            )
        )
        session.add(
            social_db.TransmissionRecord(
                id=transmission_id,
                delivery_key=f"{message_id}:channel-direct-dialogue-v1:{recipient_id}",
                world_id=WORLD_ID,
                message_id=message_id,
                channel_id="channel-direct-dialogue-v1",
                sender_id=sender_id,
                recipient_id=recipient_id,
                status="scheduled",
                sent_world_time=sent_at,
                arrival_world_time=sent_at + timedelta(minutes=5),
                priority=5,
            )
        )

    async def _advance_conversation(
        self, session: AsyncSession, transmission: social_db.TransmissionRecord
    ) -> None:
        message = await session.get(social_db.MessageRecord, transmission.message_id)
        if message is None or message.correlation_id != "corr-conversation-chen-zhou-v1":
            return
        conversation = await session.get(
            social_db.ConversationRecord, "conversation-chen-zhou-v1", with_for_update=True
        )
        if conversation is None or conversation.state in {"completed", "cancelled", "faulted"}:
            return
        conversation.turn_count += 1
        conversation.used_tokens += len(message.body.split())
        conversation.version += 1
        if (
            transmission.recipient_id == ZHOU_ID
            and conversation.turn_count < conversation.max_turns
        ):
            official = await session.scalar(
                select(social_db.BeliefRevisionRecord)
                .where(
                    social_db.BeliefRevisionRecord.agent_id == ZHOU_ID,
                    social_db.BeliefRevisionRecord.proposition_key == PROPOSITION,
                )
                .order_by(social_db.BeliefRevisionRecord.revision.desc())
            )
            if official is None:
                conversation.state = "completed"
                conversation.terminal_reason = "participant_declined"
                return
            await self._create_dialogue_message(
                session,
                message_id="message-zhou-corrects-chen-v1",
                transmission_id="transmission-zhou-corrects-chen-v1",
                sender_id=ZHOU_ID,
                recipient_id=CHEN_ID,
                body="The official bulletin says only the north gate closes at 12:00.",
                claim=MessageClaim(
                    proposition_key=PROPOSITION,
                    stance=ClaimStance.CORRECTED,
                    value=official.value,
                    attribution="Zhou citing the official bulletin",
                    causal_source_key="north-gate-bulletin-independent-v1",
                ),
                sent_at=transmission.arrival_world_time,
            )
            await session.flush()
            conversation.latest_transmission_id = "transmission-zhou-corrects-chen-v1"
            conversation.current_speaker_id = CHEN_ID
            conversation.state = "awaiting_delivery"
        else:
            conversation.state = "completed"
            conversation.current_speaker_id = None
            conversation.terminal_reason = "correction_delivered"

    async def _expire_conversations(self, session: AsyncSession, now: datetime) -> None:
        rows = list(
            (
                await session.scalars(
                    select(social_db.ConversationRecord).where(
                        social_db.ConversationRecord.state.in_(
                            ["opening", "active", "awaiting_delivery"]
                        ),
                        social_db.ConversationRecord.world_deadline <= now,
                    )
                )
            ).all()
        )
        for row in rows:
            row.state = "completed"
            row.terminal_reason = "world_timeout"
            row.current_speaker_id = None
            row.version += 1

    async def propagation(self) -> list[PropagationItemRead]:
        async with self.sessions() as session:
            rows = list(
                (
                    await session.scalars(
                        select(social_db.TransmissionRecord)
                        .where(social_db.TransmissionRecord.world_id == WORLD_ID)
                        .order_by(
                            social_db.TransmissionRecord.arrival_world_time,
                            social_db.TransmissionRecord.priority,
                            social_db.TransmissionRecord.created_at,
                            social_db.TransmissionRecord.id,
                        )
                    )
                ).all()
            )
            result = []
            for row in rows:
                message = await session.get(social_db.MessageRecord, row.message_id)
                channel = await session.get(social_db.CommunicationChannelRecord, row.channel_id)
                assert message is not None and channel is not None
                result.append(
                    PropagationItemRead(
                        transmission_id=row.id,
                        message_id=row.message_id,
                        recipient_id=row.recipient_id,
                        channel_kind=channel.kind,
                        sent_world_time=row.sent_world_time.isoformat(),
                        arrival_world_time=row.arrival_world_time.isoformat(),
                        status=row.status,
                        reliability=channel.reliability_milli / 1000,
                        distortion_policy_id=channel.distortion_policy_id,
                        claim_value=MessageClaim.model_validate(message.claims[0]).value,
                        observation_id=row.delivered_observation_id,
                    )
                )
            return result

    async def beliefs(self, agent_id: str | None = None) -> list[BeliefRevisionRead]:
        async with self.sessions() as session:
            query = select(social_db.BeliefRevisionRecord).where(
                social_db.BeliefRevisionRecord.world_id == WORLD_ID
            )
            if agent_id is not None:
                query = query.where(social_db.BeliefRevisionRecord.agent_id == agent_id)
            rows = list(
                (
                    await session.scalars(
                        query.order_by(
                            social_db.BeliefRevisionRecord.world_time,
                            social_db.BeliefRevisionRecord.agent_id,
                            social_db.BeliefRevisionRecord.revision,
                        )
                    )
                ).all()
            )
            return [
                BeliefRevisionRead(
                    id=row.id,
                    agent_id=row.agent_id,
                    proposition_key=row.proposition_key,
                    revision=row.revision,
                    value=row.value,
                    confidence=row.confidence_milli / 1000,
                    status=row.status,
                    reason_code=row.reason_code,
                    world_time=row.world_time.isoformat(),
                )
                for row in rows
            ]

    async def conversations(self) -> list[ConversationRead]:
        async with self.sessions() as session:
            rows = list(
                (
                    await session.scalars(
                        select(social_db.ConversationRecord)
                        .where(social_db.ConversationRecord.world_id == WORLD_ID)
                        .order_by(social_db.ConversationRecord.created_at)
                    )
                ).all()
            )
            return [
                ConversationRead(
                    id=row.id,
                    participant_ids=[str(value) for value in row.participant_ids],
                    state=row.state,
                    current_speaker_id=row.current_speaker_id,
                    turn_count=row.turn_count,
                    max_turns=row.max_turns,
                    used_tokens=row.used_tokens,
                    max_tokens=row.max_tokens,
                    terminal_reason=row.terminal_reason,
                )
                for row in rows
            ]
