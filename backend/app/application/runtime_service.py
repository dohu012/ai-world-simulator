"""Bounded PostgreSQL adapter for the fixed Gray Harbor durable-runtime demo."""

import json
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.action_lifecycle import DemoActionSubmission, GrayHarborActionService
from app.application.agent_decision import AgentDecisionApplicationService, DecisionSubmission
from app.application.gray_harbor import WORLD_ID
from app.application.observation_builder import ObservationBuilder
from app.application.seven_day_scenario import daily_affordances
from app.application.social_runtime import SocialRuntimeService
from app.domain.enums import EventType, FactVisibility, ObservationType, OracleRequestStatus
from app.domain.observation import FeltChange
from app.domain.schemas import Character, Observation, OracleRequest, OracleResponse, WorldEvent
from app.infrastructure.database import models as r
from app.infrastructure.database import runtime_models as rr
from app.infrastructure.database import seven_day_models as sr
from app.model_gateway.adapters import ScriptedModelGateway
from app.model_gateway.contracts import ModelGateway
from app.repositories.worlds import WorldRepository

CHEN_ID = "char-chen-mo"
SCHEDULE_ID = "schedule-gray-harbor-north-gate-rumor-v1"


class RuntimeDisabledError(Exception):
    pass


class RuntimeStateError(Exception):
    pass


class OracleWindowClosedError(Exception):
    pass


class AdvanceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: int = Field(ge=0, le=1440)
    expected_generation: int = Field(ge=1)


class OracleReplyCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length=1, max_length=1000)


class RuntimeRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    world_time: datetime
    generation: int
    version: int
    next_due_world_time: datetime | None
    backlog: int


class OracleWindowRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str
    agent_id: str
    status: str
    outcome: str | None
    final_decision_id: str | None = None
    question: str
    context_summary: str
    world_deadline: datetime
    real_deadline: datetime


class NotificationRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: str
    status: str
    created_at: datetime


class PostgresWorldRuntimeAdapter:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        *,
        enabled: bool,
        gateway: ModelGateway | None = None,
        model_max_attempts: int = 2,
        model_timeout_seconds: float = 15.0,
        model_max_output_tokens: int = 300,
    ) -> None:
        self.sessions, self.enabled = sessions, enabled
        # None keeps tests and local demos on the deterministic scripted gateway.
        self.gateway: ModelGateway = gateway if gateway is not None else ScriptedModelGateway()
        self.model_max_attempts = model_max_attempts
        self.model_timeout_seconds = model_timeout_seconds
        self.model_max_output_tokens = model_max_output_tokens

    def _enabled(self) -> None:
        if not self.enabled:
            raise RuntimeDisabledError

    async def start(self) -> RuntimeRead:
        self._enabled()
        async with self.sessions() as session:
            world = await session.get(r.WorldRecord, WORLD_ID)
            if world is None:
                raise RuntimeStateError("WORLD_NOT_SEEDED")
            runtime = await session.get(rr.WorldRuntimeRecord, WORLD_ID, with_for_update=True)
            if runtime is None:
                runtime = rr.WorldRuntimeRecord(
                    world_id=WORLD_ID,
                    status="running",
                    current_world_time=world.current_time,
                    real_time_anchor=datetime.now(UTC),
                    generation=1,
                )
                session.add(runtime)
                session.add(
                    rr.ScheduledWorldEventRecord(
                        id=SCHEDULE_ID,
                        world_id=WORLD_ID,
                        idempotency_key=SCHEDULE_ID,
                        status="scheduled",
                        due_world_time=world.current_time + timedelta(minutes=10),
                        priority=10,
                        parameters={"fixture": "north_gate_supply_warning"},
                        correlation_id="corr-runtime-north-gate-v1",
                    )
                )
            elif runtime.status != "running":
                runtime.status, runtime.generation, runtime.version = (
                    "running",
                    runtime.generation + 1,
                    runtime.version + 1,
                )
                runtime.real_time_anchor = datetime.now(UTC)
            await session.commit()
        return await self.read()

    async def set_status(self, status: str) -> RuntimeRead:
        self._enabled()
        async with self.sessions() as session:
            row = await session.get(rr.WorldRuntimeRecord, WORLD_ID, with_for_update=True)
            if row is None:
                raise RuntimeStateError("WORLD_RUNTIME_NOT_STARTED")
            row.status, row.version = status, row.version + 1
            if status == "running":
                row.generation += 1
            await session.commit()
        return await self.read()

    async def advance(self, command: AdvanceCommand) -> RuntimeRead:
        self._enabled()
        previous_day = 0
        current_day = 0
        scenario_generation = 0
        async with self.sessions() as session:
            runtime = await session.get(rr.WorldRuntimeRecord, WORLD_ID, with_for_update=True)
            if runtime is None or runtime.status != "running":
                raise RuntimeStateError("WORLD_RUNTIME_PAUSED")
            if runtime.generation != command.expected_generation:
                raise RuntimeStateError("WORLD_RUNTIME_GENERATION_CONFLICT")
            runtime.current_world_time += timedelta(minutes=command.minutes)
            runtime.version += 1
            due = list(
                (
                    await session.scalars(
                        select(rr.ScheduledWorldEventRecord)
                        .where(
                            rr.ScheduledWorldEventRecord.world_id == WORLD_ID,
                            rr.ScheduledWorldEventRecord.status == "scheduled",
                            rr.ScheduledWorldEventRecord.due_world_time
                            <= runtime.current_world_time,
                        )
                        .order_by(
                            rr.ScheduledWorldEventRecord.due_world_time,
                            rr.ScheduledWorldEventRecord.priority,
                            rr.ScheduledWorldEventRecord.created_at,
                            rr.ScheduledWorldEventRecord.id,
                        )
                        .limit(runtime.catch_up_limit + 1)
                        .with_for_update(skip_locked=True)
                    )
                ).all()
            )
            if len(due) > runtime.catch_up_limit:
                raise RuntimeStateError("WORLD_ADVANCE_LIMIT_EXCEEDED")
            for schedule in due:
                await self._publish_fixture(session, runtime, schedule)
            await self._expire_windows(session, runtime.current_world_time, datetime.now(UTC))
            checkpoint = await session.get(
                sr.ScenarioCheckpointRecord, WORLD_ID, with_for_update=True
            )
            if checkpoint is not None:
                previous_day = checkpoint.current_day
                generation_value = checkpoint.payload.get("reset_generation")
                if isinstance(generation_value, int):
                    scenario_generation = generation_value
                started_value = checkpoint.payload.get("started_world_time")
                if isinstance(started_value, str):
                    started = datetime.fromisoformat(started_value)
                    checkpoint.current_day = min(
                        7,
                        max(
                            0,
                            int((runtime.current_world_time - started).total_seconds() // 86_400),
                        ),
                    )
                    checkpoint.status = "completed" if checkpoint.current_day == 7 else "running"
                    checkpoint.version += 1
                    current_day = checkpoint.current_day
                    if current_day >= 5:
                        await self._fire_day5_condition(session, runtime, scenario_generation)
            await session.commit()
        for day in range(previous_day + 1, current_day + 1):
            await self._execute_daily_affordances(day, scenario_generation)
        social = SocialRuntimeService(self.sessions)
        await social.seed_scenario()
        await social.deliver_due()
        await self._continue_pending()
        return await self.read()

    async def _fire_day5_condition(
        self,
        session: AsyncSession,
        runtime: rr.WorldRuntimeRecord,
        generation: int,
    ) -> None:
        condition = await session.get(
            sr.ConditionalEventRecord,
            "condition-food-shipment-stop",
            with_for_update=True,
        )
        if condition is None or condition.status != "pending":
            return
        event_id = f"event-scenario-g{generation}-food-shipment-stopped"
        condition.status = "fired"
        condition.fired_at = runtime.current_world_time
        condition.payload = {
            **condition.payload,
            "status": "fired",
            "event_id": event_id,
        }
        if await session.get(r.WorldEventRecord, event_id) is not None:
            return
        character_rows = (
            await session.scalars(
                select(r.CharacterRecord)
                .where(r.CharacterRecord.world_id == WORLD_ID)
                .order_by(r.CharacterRecord.id)
            )
        ).all()
        characters = [self._character(row) for row in character_rows]
        event = WorldEvent(
            id=event_id,
            world_id=WORLD_ID,
            event_type=EventType.SCHEDULED_EVENT,
            title="Food shipment stops",
            description="The expected Gray Harbor food shipment will not arrive.",
            occurred_at=runtime.current_world_time,
            location_id="north-market-store",
            participant_ids=[character.id for character in characters],
            fact_ids=[],
            source_action_id=None,
            visibility=FactVisibility.PUBLIC,
            correlation_id=f"corr-scenario-g{generation}-day5-shipment",
            metadata={
                "condition_id": condition.id,
                "scenario_generation": generation,
            },
            schema_version="1.0",
            created_at=runtime.current_world_time,
        )
        observations = ObservationBuilder().build_for_events([event], characters)
        session.add(
            r.WorldEventRecord(
                id=event.id,
                world_id=event.world_id,
                event_type=event.event_type.value,
                occurred_at=event.occurred_at,
                visibility=event.visibility.value,
                correlation_id=event.correlation_id,
                source_action_id=None,
                schema_version=event.schema_version,
                payload=event.model_dump(mode="json"),
            )
        )
        for observation in observations:
            session.add(
                r.ObservationRecord(
                    id=observation.id,
                    world_id=observation.world_id,
                    agent_id=observation.agent_id,
                    observed_at=observation.observed_at,
                    source_event_id=event.id,
                    source_message_id=None,
                    schema_version=observation.schema_version,
                    payload=observation.model_dump(mode="json"),
                )
            )

    async def _execute_daily_affordances(self, day: int, generation: int) -> None:
        for actor_id, action_type, affordance_id in daily_affordances(day):
            async with self.sessions() as session:
                await GrayHarborActionService(WorldRepository(session)).submit(
                    actor_id,
                    DemoActionSubmission(
                        idempotency_key=(
                            f"scenario-v1-g{generation}-day-{day}-{action_type.value}"
                        ),
                        action_type=action_type,
                        parameters={"affordance_id": affordance_id},
                        reason_summary=(
                            "Execute the current server-offered scenario step "
                            f"for generation {generation}."
                        ),
                    ),
                )

    async def _publish_fixture(
        self,
        session: AsyncSession,
        runtime: rr.WorldRuntimeRecord,
        schedule: rr.ScheduledWorldEventRecord,
    ) -> None:
        schedule.status, schedule.attempts, schedule.claim_token = (
            "published",
            schedule.attempts + 1,
            schedule.claim_token + 1,
        )
        event_id = "event-runtime-north-gate-warning-v1"
        if await session.get(r.WorldEventRecord, event_id) is not None:
            schedule.published_event_id = event_id
            return
        event = WorldEvent(
            id=event_id,
            world_id=WORLD_ID,
            event_type=EventType.SCHEDULED_EVENT,
            title="North gate supply route becomes uncertain",
            description=(
                "A verified courier notice says the north gate supply route may close soon."
            ),
            occurred_at=schedule.due_world_time,
            location_id="north-market-store",
            participant_ids=[CHEN_ID],
            fact_ids=[],
            source_action_id=None,
            visibility=FactVisibility.PRIVATE,
            correlation_id=schedule.correlation_id,
            metadata={"schedule_id": schedule.id, "runtime_generation": runtime.generation},
            schema_version="1.0",
            created_at=schedule.due_world_time,
        )
        observation = ObservationBuilder().build_for_events(
            [event], [self._character(await session.get(r.CharacterRecord, CHEN_ID))]
        )[0]
        session.add(
            r.WorldEventRecord(
                id=event.id,
                world_id=WORLD_ID,
                event_type=event.event_type.value,
                occurred_at=event.occurred_at,
                visibility=event.visibility.value,
                correlation_id=event.correlation_id,
                source_action_id=None,
                schema_version=event.schema_version,
                payload=event.model_dump(mode="json"),
            )
        )
        session.add(
            r.ObservationRecord(
                id=observation.id,
                world_id=WORLD_ID,
                agent_id=CHEN_ID,
                observed_at=observation.observed_at,
                source_event_id=event.id,
                source_message_id=None,
                schema_version=observation.schema_version,
                payload=observation.model_dump(mode="json"),
            )
        )
        schedule.published_event_id = event.id
        wake_id = "wake-" + sha256(event.id.encode()).hexdigest()[:20]
        session.add(
            rr.AgentWakeRecord(
                id=wake_id,
                world_id=WORLD_ID,
                agent_id=CHEN_ID,
                causal_key=event.id,
                reason="relevant_observation",
                observation_ids=[observation.id],
                status="completed",
            )
        )
        await self._open_oracle(session, runtime.current_world_time, schedule.correlation_id)

    @staticmethod
    def _character(row: r.CharacterRecord | None) -> Character:
        if row is None:
            raise RuntimeStateError("CHEN_NOT_SEEDED")
        return Character.model_validate_json(json.dumps(row.payload))

    async def _open_oracle(self, session: AsyncSession, now: datetime, correlation: str) -> None:
        request_id = "oracle-runtime-chen-v1"
        if await session.get(r.OracleRequestRecord, request_id) is not None:
            return
        request = OracleRequest(
            id=request_id,
            world_id=WORLD_ID,
            agent_id=CHEN_ID,
            question="Should I leave the store before the north gate supply route closes?",
            context_summary=(
                "A verified warning affects Chen's child and limited supplies; "
                "advice is not a command."
            ),
            requested_at=now,
            world_deadline=now + timedelta(minutes=30),
            real_deadline=datetime.now(UTC) + timedelta(hours=24),
            status=OracleRequestStatus.PENDING,
            decision_correlation_id=correlation,
            schema_version="1.0",
        )
        session.add(
            r.OracleRequestRecord(
                id=request.id,
                world_id=WORLD_ID,
                agent_id=CHEN_ID,
                requested_at=request.requested_at,
                decision_correlation_id=correlation,
                schema_version=request.schema_version,
                payload=request.model_dump(mode="json"),
            )
        )
        session.add(
            rr.OracleWindowRecord(
                id="window-runtime-chen-v1",
                request_id=request.id,
                world_id=WORLD_ID,
                agent_id=CHEN_ID,
                decision_correlation_id=correlation,
                status="waiting",
                world_deadline=request.world_deadline,
                real_deadline=request.real_deadline,
            )
        )
        session.add(
            rr.NotificationOutboxRecord(
                id="notification-oracle-runtime-chen-v1",
                world_id=WORLD_ID,
                dispatch_key="oracle-opened:" + request.id,
                kind="oracle_opened",
                status="pending",
                payload={"request_id": request.id, "agent_id": CHEN_ID},
            )
        )

    async def reply(self, request_id: str, command: OracleReplyCommand) -> OracleWindowRead:
        self._enabled()
        async with self.sessions() as session:
            window = await session.scalar(
                select(rr.OracleWindowRecord)
                .where(rr.OracleWindowRecord.request_id == request_id)
                .with_for_update()
            )
            if window is None or window.status != "waiting":
                raise OracleWindowClosedError
            request_row = await session.get(r.OracleRequestRecord, request_id)
            assert request_row is not None
            request = OracleRequest.model_validate_json(json.dumps(request_row.payload))
            now = datetime.now(UTC)
            response = OracleResponse(
                id="response-" + request_id,
                request_id=request_id,
                world_id=WORLD_ID,
                agent_id=CHEN_ID,
                content=command.content,
                clarity=0.7,
                responded_at=now,
                schema_version="1.0",
            )
            observation = ObservationBuilder().build_for_oracle(request, response)
            session.add(
                r.OracleResponseRecord(
                    id=response.id,
                    request_id=request_id,
                    world_id=WORLD_ID,
                    agent_id=CHEN_ID,
                    responded_at=now,
                    schema_version="1.0",
                    payload=response.model_dump(mode="json"),
                )
            )
            session.add(
                r.ObservationRecord(
                    id=observation.id,
                    world_id=WORLD_ID,
                    agent_id=CHEN_ID,
                    observed_at=now,
                    source_event_id=None,
                    source_message_id=response.id,
                    schema_version="1.0",
                    payload=observation.model_dump(mode="json"),
                )
            )
            request_row.payload = request.model_copy(
                update={"status": OracleRequestStatus.ANSWERED}
            ).model_dump(mode="json")
            window.status, window.outcome, window.response_id, window.delivered_observation_id = (
                "resumed",
                "replied",
                response.id,
                observation.id,
            )
            session.add(
                rr.NotificationOutboxRecord(
                    id="notification-completed-" + request_id,
                    world_id=WORLD_ID,
                    dispatch_key="oracle-replied:" + request_id,
                    kind="oracle_replied",
                    status="pending",
                    payload={"request_id": request_id},
                )
            )
            await session.commit()
        await self._continue(request_id)
        return await self.window(request_id)

    async def _expire_windows(
        self, session: AsyncSession, world_now: datetime, real_now: datetime
    ) -> None:
        windows = list(
            (
                await session.scalars(
                    select(rr.OracleWindowRecord)
                    .where(rr.OracleWindowRecord.status == "waiting")
                    .with_for_update(skip_locked=True)
                )
            ).all()
        )
        for window in windows:
            if world_now < window.world_deadline and real_now < window.real_deadline:
                continue
            request_row = await session.get(r.OracleRequestRecord, window.request_id)
            assert request_row is not None
            request = OracleRequest.model_validate_json(json.dumps(request_row.payload))
            observation = Observation(
                id="obs-silence-" + window.request_id,
                world_id=WORLD_ID,
                agent_id=CHEN_ID,
                observed_at=world_now,
                observation_type=ObservationType.ORACLE,
                source_event_id=None,
                source_message_id=None,
                visible_entities=[],
                heard_statements=[],
                received_messages=[],
                felt_changes=[
                    FeltChange(
                        description="The Oracle window closed without a player reply.",
                        intensity=0.4,
                    )
                ],
                available_actions=[],
                metadata={
                    "oracle_request_id": window.request_id,
                    "silence": True,
                    "fabricated_advice": False,
                },
                schema_version="1.0",
            )
            session.add(
                r.ObservationRecord(
                    id=observation.id,
                    world_id=WORLD_ID,
                    agent_id=CHEN_ID,
                    observed_at=world_now,
                    source_event_id=None,
                    source_message_id=None,
                    schema_version="1.0",
                    payload=observation.model_dump(mode="json"),
                )
            )
            request_row.payload = request.model_copy(
                update={"status": OracleRequestStatus.EXPIRED}
            ).model_dump(mode="json")
            window.status, window.outcome, window.delivered_observation_id = (
                "resumed",
                "timed_out",
                observation.id,
            )
            session.add(
                rr.NotificationOutboxRecord(
                    id="notification-timeout-" + window.request_id,
                    world_id=WORLD_ID,
                    dispatch_key="oracle-timeout:" + window.request_id,
                    kind="oracle_timed_out",
                    status="pending",
                    payload={"request_id": window.request_id},
                )
            )

    async def _continue_pending(self) -> None:
        async with self.sessions() as session:
            request_ids = list(
                (
                    await session.scalars(
                        select(rr.OracleWindowRecord.request_id).where(
                            rr.OracleWindowRecord.status == "resumed"
                        )
                    )
                ).all()
            )
        for request_id in request_ids:
            await self._continue(request_id)

    async def _continue(self, request_id: str) -> None:
        decision = await AgentDecisionApplicationService(
            self.sessions,
            self.gateway,
            max_attempts=self.model_max_attempts,
            timeout_seconds=self.model_timeout_seconds,
            max_output_tokens=self.model_max_output_tokens,
        ).decide(
            CHEN_ID,
            DecisionSubmission(idempotency_key=f"oracle-final-{request_id}"),
        )
        async with self.sessions() as session:
            window = await session.scalar(
                select(rr.OracleWindowRecord)
                .where(rr.OracleWindowRecord.request_id == request_id)
                .with_for_update()
            )
            if window is None or window.status == "completed":
                return
            window.status = "completed"
            window.final_decision_id = decision.decision_id
            await session.commit()

    async def read(self) -> RuntimeRead:
        async with self.sessions() as session:
            row = await session.get(rr.WorldRuntimeRecord, WORLD_ID)
            if row is None:
                raise RuntimeStateError("WORLD_RUNTIME_NOT_STARTED")
            next_due = await session.scalar(
                select(rr.ScheduledWorldEventRecord.due_world_time)
                .where(
                    rr.ScheduledWorldEventRecord.world_id == WORLD_ID,
                    rr.ScheduledWorldEventRecord.status == "scheduled",
                )
                .order_by(rr.ScheduledWorldEventRecord.due_world_time)
                .limit(1)
            )
            backlog = len(
                list(
                    (
                        await session.scalars(
                            select(rr.ScheduledWorldEventRecord.id).where(
                                rr.ScheduledWorldEventRecord.world_id == WORLD_ID,
                                rr.ScheduledWorldEventRecord.status == "scheduled",
                                rr.ScheduledWorldEventRecord.due_world_time
                                <= row.current_world_time,
                            )
                        )
                    ).all()
                )
            )
            return RuntimeRead(
                status=row.status,
                world_time=row.current_world_time,
                generation=row.generation,
                version=row.version,
                next_due_world_time=next_due,
                backlog=backlog,
            )

    async def windows(self) -> list[OracleWindowRead]:
        async with self.sessions() as session:
            ids = list(
                (
                    await session.scalars(
                        select(rr.OracleWindowRecord.request_id)
                        .where(rr.OracleWindowRecord.world_id == WORLD_ID)
                        .order_by(rr.OracleWindowRecord.created_at)
                    )
                ).all()
            )
        return [await self.window(value) for value in ids]

    async def window(self, request_id: str) -> OracleWindowRead:
        async with self.sessions() as session:
            window = await session.scalar(
                select(rr.OracleWindowRecord).where(rr.OracleWindowRecord.request_id == request_id)
            )
            request = await session.get(r.OracleRequestRecord, request_id)
            if window is None or request is None:
                raise OracleWindowClosedError
            payload = request.payload
            return OracleWindowRead(
                request_id=request_id,
                agent_id=window.agent_id,
                status=window.status,
                outcome=window.outcome,
                final_decision_id=window.final_decision_id,
                question=str(payload["question"]),
                context_summary=str(payload["context_summary"]),
                world_deadline=window.world_deadline,
                real_deadline=window.real_deadline,
            )

    async def notifications(self) -> list[NotificationRead]:
        async with self.sessions() as session:
            rows = list(
                (
                    await session.scalars(
                        select(rr.NotificationOutboxRecord)
                        .where(rr.NotificationOutboxRecord.world_id == WORLD_ID)
                        .order_by(
                            rr.NotificationOutboxRecord.created_at, rr.NotificationOutboxRecord.id
                        )
                    )
                ).all()
            )
            return [
                NotificationRead(id=x.id, kind=x.kind, status=x.status, created_at=x.created_at)
                for x in rows
            ]
